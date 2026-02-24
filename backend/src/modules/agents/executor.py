"""Enhanced agent execution engine and task management."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import WebSocket
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.src.db import models


class TaskStatus:
    """Task execution status constants."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskCreate(BaseModel):
    """Schema for creating new agent tasks."""

    agent_id: str
    goal: str  # maps to tasks.title
    input: Dict[str, Any]  # maps to tasks.input_data
    user_id: str


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: str
    user_id: str = ""
    agent_id: str = ""
    goal: Optional[str] = None  # sourced from tasks.title
    input: Optional[Dict[str, Any]] = None  # sourced from tasks.input_data
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None  # sourced from tasks.output_data
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentExecutor:
    """Core agent execution engine with resource management."""

    def __init__(self, db: Session):
        self.db = db
        self.active_tasks: Dict[str, asyncio.Task] = {}

    async def execute_task(
        self, task_data: TaskCreate, websocket: Optional[WebSocket] = None
    ) -> TaskResponse:
        """Execute an agent task with real-time progress tracking."""

        task_id = str(uuid4())

        # Create task record
        task = models.Task(
            user_id=task_data.user_id,
            agent_id=task_data.agent_id,
            title=task_data.goal,
            input_data=task_data.input,
            status=TaskStatus.QUEUED,
        )
        self.db.add(task)
        self.db.commit()

        try:
            # Update status to running
            self.db.query(models.Task).filter(models.Task.id == task_id).update(
                {"status": TaskStatus.RUNNING, "started_at": datetime.utcnow()}
            )
            self.db.commit()

            if websocket:
                await websocket.send_text(
                    json.dumps(
                        {
                            "task_id": task_id,
                            "status": "running",
                            "message": "Task started",
                        }
                    )
                )

            # Execute agent logic (placeholder for actual implementation)
            result = await self._execute_agent_logic(
                task_data.agent_id, task_data.input, websocket
            )

            # Apply unsupported-policy enforcement to RAG-aware responses
            result = self._apply_unsupported_policy(result, task_data.input)

            # Update task as completed
            self.db.query(models.Task).filter(models.Task.id == task_id).update(
                {
                    "status": TaskStatus.COMPLETED,
                    "completed_at": datetime.utcnow(),
                    "output_data": result,
                }
            )
            self.db.commit()

            if websocket:
                await websocket.send_text(
                    json.dumps(
                        {"task_id": task_id, "status": "completed", "result": result}
                    )
                )

            # Refresh task from database to get updated fields
            self.db.refresh(task)

            return TaskResponse(
                id=str(task.id),
                user_id=task.user_id,
                agent_id=task.agent_id,
                goal=task.title,
                input=task.input_data,
                status=task.status,
                started_at=task.started_at,
                completed_at=task.completed_at,
                error_message=task.error_message,
                result=task.output_data,
                created_at=task.created_at,
            )

        except Exception as e:
            # Update task as failed
            self.db.query(models.Task).filter(models.Task.id == task_id).update(
                {
                    "status": TaskStatus.FAILED,
                    "completed_at": datetime.utcnow(),
                    "error_message": str(e),
                }
            )
            self.db.commit()

            if websocket:
                await websocket.send_text(
                    json.dumps(
                        {"task_id": task_id, "status": "failed", "error": str(e)}
                    )
                )

            raise

    async def _execute_agent_logic(
        self,
        agent_id: str,
        input_data: Dict[str, Any],
        websocket: Optional[WebSocket] = None,
    ) -> Dict[str, Any]:
        """Execute the actual agent logic by dispatching to the appropriate agent service."""
        import os
        from backend.src.core.config import get_settings

        settings = get_settings()

        if websocket:
            await websocket.send_text(
                json.dumps({"message": "Initializing agent...", "progress": 10})
            )

        query = input_data.get("query") or input_data.get("goal", "")
        agent_slug = str(agent_id).lower().strip()

        try:
            # Dispatch to the appropriate agent service
            if agent_slug in ("cape-ai-guide", "cape_ai_guide"):
                from .cape_ai_guide.service import CapeAIGuideService
                from .cape_ai_guide.schemas import CapeAIGuideTaskInput
                service = CapeAIGuideService(
                    openai_api_key=settings.openai_api_key,
                    anthropic_api_key=settings.anthropic_api_key,
                    model=os.getenv("CAPE_AI_GUIDE_MODEL", "claude-3-5-haiku-20241022"),
                )
                task_input = CapeAIGuideTaskInput(query=query, **{k: v for k, v in input_data.items() if k != "query" and k in CapeAIGuideTaskInput.__fields__})
                result = await service.process_query(task_input)
                return result.dict()

            elif agent_slug in ("cape-ai-domain-specialist", "cape_ai_domain_specialist"):
                from .cape_ai_domain_specialist.service import DomainSpecialistService
                from .cape_ai_domain_specialist.schemas import DomainSpecialistTaskInput
                service = DomainSpecialistService(
                    openai_api_key=settings.openai_api_key,
                    anthropic_api_key=settings.anthropic_api_key,
                    model=os.getenv("DOMAIN_SPECIALIST_MODEL", "claude-3-5-haiku-20241022"),
                )
                task_input = DomainSpecialistTaskInput(query=query, **{k: v for k, v in input_data.items() if k != "query" and k in DomainSpecialistTaskInput.__fields__})
                result = await service.process_query(task_input)
                return result.dict()

            elif agent_slug in ("customer-agent", "customer_agent"):
                from .customer_agent.service import CustomerAgentService
                from .customer_agent.schemas import CustomerAgentTaskInput
                service = CustomerAgentService(
                    openai_api_key=settings.openai_api_key,
                    anthropic_api_key=settings.anthropic_api_key,
                    model=os.getenv("CUSTOMER_AGENT_MODEL", "claude-3-5-haiku-20241022"),
                )
                task_input = CustomerAgentTaskInput(query=query, **{k: v for k, v in input_data.items() if k != "query" and k in CustomerAgentTaskInput.__fields__})
                result = await service.process_query(task_input)
                return result.dict()

            elif agent_slug in ("dev-agent", "dev_agent"):
                from .dev_agent.service import DevAgentService
                from .dev_agent.schemas import DevAgentTaskInput
                service = DevAgentService(
                    openai_api_key=settings.openai_api_key,
                    anthropic_api_key=settings.anthropic_api_key,
                    model=os.getenv("DEV_AGENT_MODEL", "claude-3-5-haiku-20241022"),
                )
                task_input = DevAgentTaskInput(query=query, **{k: v for k, v in input_data.items() if k != "query" and k in DevAgentTaskInput.__fields__})
                result = await service.process_query(task_input)
                return result.dict()

            elif agent_slug in ("finance-agent", "finance_agent"):
                from .finance_agent.service import FinanceAgentService
                from .finance_agent.schemas import FinanceAgentTaskInput
                service = FinanceAgentService(
                    openai_api_key=settings.openai_api_key,
                    anthropic_api_key=settings.anthropic_api_key,
                    model=os.getenv("FINANCE_AGENT_MODEL", "claude-3-5-haiku-20241022"),
                )
                task_input = FinanceAgentTaskInput(query=query, **{k: v for k, v in input_data.items() if k != "query" and k in FinanceAgentTaskInput.__fields__})
                result = await service.process_query(task_input)
                return result.dict()

            elif agent_slug in ("content-agent", "content_agent"):
                from .content_agent.service import ContentAgentService
                from .content_agent.schemas import ContentAgentTaskInput
                service = ContentAgentService(
                    openai_api_key=settings.openai_api_key,
                    anthropic_api_key=settings.anthropic_api_key,
                    model=os.getenv("CONTENT_AGENT_MODEL", "claude-3-5-haiku-20241022"),
                )
                task_input = ContentAgentTaskInput(query=query, **{k: v for k, v in input_data.items() if k != "query" and k in ContentAgentTaskInput.__fields__})
                result = await service.process_query(task_input)
                return result.dict()

            elif agent_slug in ("rag-agent", "rag_agent", "rag"):
                from backend.src.modules.rag.service import RAGService
                from backend.src.modules.rag.schemas import RAGQueryRequest, UnsupportedPolicy
                service = RAGService(
                    openai_api_key=settings.openai_api_key,
                    anthropic_api_key=settings.anthropic_api_key,
                    model=os.getenv("RAG_LLM_MODEL", "claude-3-5-haiku-20241022"),
                )
                rag_request = RAGQueryRequest(
                    query=query,
                    doc_types=input_data.get("doc_types"),
                    top_k=input_data.get("top_k", 5),
                    similarity_threshold=input_data.get("similarity_threshold", 0.25),
                    unsupported_policy=input_data.get("unsupported_policy", UnsupportedPolicy.FLAG),
                    include_response=input_data.get("include_response", True),
                )
                user = self.db.query(models.User).filter(
                    models.User.id == input_data.get("user_id")
                ).first()
                if not user:
                    return {"error": "User not found for RAG query"}
                result = await service.query(self.db, user, rag_request)
                return result.dict()

            elif agent_slug in ("capsule-agent", "capsule_agent", "capsule"):
                from backend.src.modules.capsules.service import CapsuleService
                from backend.src.modules.capsules.schemas import CapsuleRunRequest
                service = CapsuleService()
                capsule_request = CapsuleRunRequest(
                    capsule_id=input_data.get("capsule_id", "sop-answering"),
                    query=query,
                    context=input_data.get("context"),
                    unsupported_policy=input_data.get("unsupported_policy", "flag"),
                )
                user = self.db.query(models.User).filter(
                    models.User.id == input_data.get("user_id")
                ).first()
                if not user:
                    return {"error": "User not found for capsule run"}
                result = await service.run(self.db, user, capsule_request)
                return result.dict()

            else:
                # Fallback for unknown/custom agents
                if websocket:
                    await websocket.send_text(
                        json.dumps({"message": f"Executing agent '{agent_slug}'...", "progress": 50})
                    )
                await asyncio.sleep(1)
                return {
                    "message": f"Task executed by agent '{agent_slug}'",
                    "timestamp": datetime.utcnow().isoformat(),
                    "input_data": input_data,
                    "agent_id": agent_slug,
                }

        except Exception as e:
            return {
                "message": f"Agent execution error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "agent_id": agent_slug,
            }

        finally:
            if websocket:
                await websocket.send_text(
                    json.dumps({"message": "Processing complete", "progress": 100})
                )

    @staticmethod
    def _apply_unsupported_policy(
        result: Dict[str, Any],
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run the unsupported-policy gate on any agent result.

        RAG-aware results contain a ``grounded`` flag. Non-RAG agents
        are treated as grounded by default (they don't claim doc backing).
        """
        try:
            from backend.src.modules.rag.policy import (
                check_response_grounding,
                enforce_policy,
                apply_policy_to_response,
            )

            grounded = check_response_grounding(result)
            policy = input_data.get("unsupported_policy", "flag")
            response_text = result.get("response") or result.get("message", "")

            decision = enforce_policy(
                grounded=grounded,
                policy=str(policy),
                response_text=response_text,
            )

            if decision.refused:
                result["refused"] = True
                result["refusal_reason"] = decision.reason
                result["response"] = None
            elif decision.flagged and decision.banner:
                if "response" in result:
                    result["response"] = f"{decision.banner}\n\n{result['response']}"
                elif "message" in result:
                    result["message"] = f"{decision.banner}\n\n{result['message']}"

            result["policy_decision"] = decision.to_dict()

        except Exception:
            # Policy enforcement is non-critical; log and proceed
            import logging
            logging.getLogger(__name__).exception(
                "Unsupported policy enforcement failed — proceeding without gate"
            )

        return result
