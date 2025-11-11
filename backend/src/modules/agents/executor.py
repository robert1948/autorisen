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
    goal: str
    input: Dict[str, Any]
    user_id: str


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: str
    user_id: str
    agent_id: str
    goal: Optional[str]
    input: Optional[Dict[str, Any]]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    result: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


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
            id=task_id,
            user_id=task_data.user_id,
            agent_id=task_data.agent_id,
            goal=task_data.goal,
            input=task_data.input,
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

            # Update task as completed
            self.db.query(models.Task).filter(models.Task.id == task_id).update(
                {
                    "status": TaskStatus.COMPLETED,
                    "completed_at": datetime.utcnow(),
                    "result": result,
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
                id=task.id,
                user_id=task.user_id,
                agent_id=task.agent_id,
                goal=task.goal,
                input=task.input,
                status=task.status,
                started_at=task.started_at,
                completed_at=task.completed_at,
                error_message=task.error_message,
                result=task.result,
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
        """Execute the actual agent logic - to be implemented per agent type."""

        # Placeholder implementation
        await asyncio.sleep(2)  # Simulate processing time

        if websocket:
            await websocket.send_text(
                json.dumps({"message": "Processing step 1 of 3", "progress": 33})
            )

        await asyncio.sleep(1)

        if websocket:
            await websocket.send_text(
                json.dumps({"message": "Processing step 2 of 3", "progress": 66})
            )

        await asyncio.sleep(1)

        if websocket:
            await websocket.send_text(
                json.dumps({"message": "Processing step 3 of 3", "progress": 100})
            )

        return {
            "message": "Task completed successfully",
            "timestamp": datetime.utcnow().isoformat(),
            "processed_data": input_data,
        }
