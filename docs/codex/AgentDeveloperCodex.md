# AgentDeveloperCodex Playbook

**Objective:** Complete Phase 2 (Core Execution) implementation by finishing the Task execution system, creating database migrations, and implementing the first prototype agent.

**Scope:** Agent system implementation within established architecture. Do **not** modify core authentication, payment systems, or unrelated modules.

## 🎯 **Primary Deliverables**

### **1. Complete Task Execution System**

**Status:** ✅ Models added, 🔄 Migration needed, 🔄 Testing required

**Commands:**
1. `cd /home/robert/Development/autolocal/backend`
2. `ALEMBIC_DATABASE_URL="postgresql://devuser:devpass@localhost:5433/devdb" DB_SSLMODE_REQUIRE=0 python -m alembic revision --autogenerate -m "add_task_execution_system"`
3. `ALEMBIC_DATABASE_URL="postgresql://devuser:devpass@localhost:5433/devdb" DB_SSLMODE_REQUIRE=0 python -m alembic upgrade head`
4. `make codex-test` (validate no regressions)

**Files to Complete:**
- ✅ `backend/src/db/models.py` (Task, Run, AuditEvent models added)
- ✅ `backend/src/modules/agents/executor.py` (AgentExecutor with WebSocket streaming)
- ✅ `backend/src/modules/agents/router.py` (task execution endpoints added)
- 🔄 `backend/migrations/versions/[new]_add_task_execution_system.py` (create via alembic)

**Validation Steps:**
- Database migration applies successfully
- No syntax errors in Python imports
- Task execution endpoints return 200/404 appropriately
- WebSocket connections can be established

### **2. Implement CapeAI Guide Prototype Agent**

**Agent Specification:**

```python
CAPE_AI_GUIDE_SPEC = {
    "name": "CapeAI Guide",
    "description": "Helpful AI assistant that guides users through CapeControl features",
    "version": "1.0.0",
    "capabilities": [
        "feature_explanation",
        "workflow_guidance", 
        "troubleshooting_help",
        "best_practices_advice"
    ],
    "input_schema": {
        "query": {"type": "string", "required": True},
        "context": {"type": "object", "required": False}
    },
    "execution_method": "openai_completion"
}
```

**Files to Create:**
- `backend/src/modules/agents/implementations/cape_ai_guide.py`
- `backend/src/modules/agents/implementations/__init__.py`
- `tests_enabled/test_cape_ai_guide.py`

### **3. Agent Testing Framework**

**Files to Create:**
- `tests_enabled/test_agents_executor.py` - Test task execution engine
- `tests_enabled/test_agents_lifecycle.py` - Test agent registration/execution flow
- `backend/src/modules/agents/testing_utils.py` - Mock WebSocket and task execution helpers

**Test Coverage Requirements:**
- Task creation and execution flow
- WebSocket streaming functionality
- Error handling and recovery
- Agent implementation validation

## 🔧 **Technical Implementation Guide**

### **Database Migration Completion**

```bash
# Ensure Docker PostgreSQL is running
cd /home/robert/Development/autolocal && docker compose up -d db

# Generate and apply migration
cd backend
ALEMBIC_DATABASE_URL="postgresql://devuser:devpass@localhost:5433/devdb" \
DB_SSLMODE_REQUIRE=0 \
python -m alembic revision --autogenerate -m "add_task_execution_system"

ALEMBIC_DATABASE_URL="postgresql://devuser:devpass@localhost:5433/devdb" \
DB_SSLMODE_REQUIRE=0 \
python -m alembic upgrade head
```

### **CapeAI Guide Implementation**

```python
# backend/src/modules/agents/implementations/cape_ai_guide.py
from typing import Dict, Any
import openai
from backend.src.core.config import get_settings

class CapeAIGuide:
    def __init__(self):
        self.settings = get_settings()
        self.client = openai.OpenAI(api_key=self.settings.openai_api_key)
    
    async def execute_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CapeAI Guide task with OpenAI integration."""
        query = input_data.get("query", "")
        context = input_data.get("context", {})
        
        prompt = f"""You are CapeAI Guide, a helpful assistant for CapeControl platform users.
        
User Query: {query}
Context: {context}

Provide helpful, accurate guidance about CapeControl features, workflows, or troubleshooting.
Keep responses concise and actionable."""

        try:
            response = await self.client.chat.completions.acreate(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                "response": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": "gpt-4o-mini"
            }
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
```

### **Testing Implementation**

```python
# tests_enabled/test_agents_executor.py
import pytest
from backend.src.modules.agents.executor import AgentExecutor, TaskCreate

@pytest.fixture
def executor(test_db):
    return AgentExecutor(db=test_db)

def test_task_creation(executor):
    task_data = TaskCreate(
        agent_id="test-agent",
        goal="Test task execution",
        input={"query": "Hello"},
        user_id="test-user"
    )
    
    # Test task creation logic
    assert task_data.agent_id == "test-agent"
    assert task_data.goal == "Test task execution"

async def test_task_execution_flow(executor, mock_websocket):
    # Test full execution with mocked WebSocket
    pass
```

## 📋 **Allowed Modifications**

**SAFE TO MODIFY:**
- `backend/src/modules/agents/` (entire directory)
- `tests_enabled/test_agents_*.py`
- `backend/migrations/versions/` (new migrations only)
- `docs/codex/` documentation

**DO NOT MODIFY:**
- `backend/src/modules/auth/` (authentication system)
- `backend/src/modules/payment/` (payment processing)  
- `backend/src/modules/chatkit/` (chat functionality)
- `app/` (legacy shim layer)
- Production configuration files

## ✅ **Success Criteria**

**Phase Completion Checklist:**
- [ ] Database migration applies without errors
- [ ] All existing tests pass (`make codex-test`)
- [ ] Task execution endpoints return expected responses
- [ ] CapeAI Guide agent can be instantiated and executed
- [ ] WebSocket streaming works for task progress
- [ ] Agent test coverage >80% for new code
- [ ] No lint errors in modified files

**Integration Validation:**
- [ ] Agent registry CRUD operations still functional
- [ ] Task execution integrates with auth system
- [ ] Error handling provides useful feedback
- [ ] Database performance acceptable (<100ms for task operations)

## 🚀 **Deployment Commands**

```bash
# Comprehensive validation
make codex-test          # Run test suite
make docker-build        # Verify containerization  
make lint               # Check code quality

# Local agent testing
cd backend
python -c "
from src.modules.agents.implementations.cape_ai_guide import CapeAIGuide
import asyncio

async def test():
    agent = CapeAIGuide()
    result = await agent.execute_task({'query': 'What is CapeControl?'})
    print(result)

asyncio.run(test())
"
```

## 🎯 **Next Phase Preparation**

Upon completion, prepare for **Phase 3: Advanced Features** by:
- Documenting agent implementation patterns
- Creating agent marketplace schema
- Establishing version management workflow
- Planning multi-agent orchestration

**Done when:**
- PR opened with labels: `codex`, `agent-developer`, `phase-2-complete`
- All success criteria validated
- CapeAI Guide agent functional demonstration included
- Link to updated `docs/agents/ARCHITECTURE_BLUEPRINT.md` with implementation status
