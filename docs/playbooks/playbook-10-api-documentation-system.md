# Playbook 10: API Documentation System

**Owner**: Codex
**Supporting Agents**: DocSmith, CapeAI
**Status**: Todo
**Priority**: P2

## 1) Outcome

**Definition of Done:**
- Interactive API documentation using OpenAPI/Swagger
- Auto-generated API docs from FastAPI endpoints
- Live API testing interface with authentication
- Code examples for all endpoints in multiple languages
- API versioning documentation and migration guides
- Search functionality and categorized endpoint organization

**KPIs:**
- API documentation coverage > 95%
- Developer onboarding time reduced by 50%
- API endpoint discoverability score > 90%
- Documentation page load time < 2 seconds
- Zero undocumented public endpoints

## 2) Scope (In / Out)

**In:**
- OpenAPI/Swagger documentation generation
- Interactive API explorer with authentication
- Code examples and SDK documentation
- API response schemas and validation
- Rate limiting and authentication documentation
- Error response documentation with examples
- API versioning and changelog

**Out:**
- Third-party API integration docs (separate effort)
- Advanced SDK development
- GraphQL documentation (future consideration)
- Webhook documentation (covered in payment playbook)

## 3) Dependencies

**Upstream:**
- FastAPI backend with existing endpoints ✅ Complete
- Authentication system ✅ Complete
- Payment API endpoints (PAY-002) ✅ Complete
- Chat API endpoints (CHAT-001) ✅ Complete

**Downstream:**
- Developer portal (future enhancement)
- Mobile app development
- Third-party integrations

## 4) Milestones

### M1 – OpenAPI Foundation (Week 1)

- Configure FastAPI OpenAPI generation
- Document existing API endpoints
- Set up Swagger UI integration
- Add authentication to docs

### M2 – Enhanced Documentation (Week 2)

- Add comprehensive examples
- Document error responses
- Create API guide sections
- Implement search functionality

### M3 – Developer Experience (Week 3)

- Code generation tools
- API testing interface
- Versioning documentation
- Performance optimization

## 5) Checklist (Executable)

**Backend Documentation:**
- [ ] Configure FastAPI OpenAPI settings
- [ ] Add comprehensive docstrings to all endpoints
- [ ] Document request/response schemas with examples
- [ ] Add authentication documentation
- [ ] Document error responses and status codes
- [ ] Add rate limiting information

**Interactive Documentation:**
- [ ] Set up Swagger UI with custom styling
- [ ] Configure authentication in Swagger UI
- [ ] Add Try-it-out functionality
- [ ] Create API categorization and tagging
- [ ] Implement search and filtering

**Code Examples:**
- [ ] Generate curl examples for all endpoints
- [ ] Add Python SDK examples
- [ ] Create JavaScript/TypeScript examples
- [ ] Document authentication flows
- [ ] Add pagination examples

**Documentation Website:**
- [ ] Create API docs landing page
- [ ] Add getting started guide
- [ ] Document API versioning strategy
- [ ] Create troubleshooting section
- [ ] Add changelog and migration guides

**Testing & Quality:**
- [ ] Validate all documented endpoints
- [ ] Test interactive examples
- [ ] Check documentation completeness
- [ ] Validate code examples
- [ ] Performance test docs page

**Make Targets:**
- [ ] `make docs-api-generate` creates fresh docs
- [ ] `make docs-api-validate` checks completeness
- [ ] `make docs-api-serve` serves docs locally

## 6) Runbook / Commands

```bash
# Backend documentation setup
cd backend
# Update FastAPI app configuration
# Add to backend/src/app.py:
# app = FastAPI(
#     title="AutoRisen API",
#     description="CapeControl AI Automation Platform",
#     version="1.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc"
# )

# Generate OpenAPI schema
curl http://localhost:8000/openapi.json > docs/api_schema.json

# Validate API documentation
python -c "
import json
with open('docs/api_schema.json') as f:
    schema = json.load(f)
    print(f'Endpoints: {len(schema[\"paths\"])}')
    print(f'Components: {len(schema.get(\"components\", {}).get(\"schemas\", {}))}')
"

# Serve documentation locally
uvicorn backend.src.app:app --reload --port 8000
# Visit http://localhost:8000/docs

# Create API documentation website
mkdir -p docs/api
cd docs/api
# Set up documentation generation script

# Deploy documentation
make heroku-deploy
# Verify at https://your-app.herokuapp.com/docs
```

## 7) Implementation Notes

**Key Files to Create/Modify:**

Backend:
- `backend/src/app.py` (OpenAPI configuration)
- `backend/src/modules/*/router.py` (endpoint documentation)
- `backend/src/core/schemas.py` (response models)
- `docs/api_generator.py` (documentation build script)

Frontend:
- `client/src/pages/ApiDocs.tsx` (custom docs page)
- `client/src/components/docs/ApiExplorer.tsx`
- `docs/api/index.html` (static docs hosting)

**OpenAPI Configuration:**

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="AutoRisen API",
    description="CapeControl AI Automation Platform API",
    version="1.0.0",
    contact={
        "name": "CapeControl Support",
        "email": "support@cape-control.com"
    },
    license_info={
        "name": "Proprietary"
    }
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AutoRisen API",
        version="1.0.0",
        description="CapeControl AI Automation Platform",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

**Endpoint Documentation Pattern:**

```python
@router.post(
    "/chat/threads",
    response_model=ChatThreadResponse,
    summary="Create a new chat thread",
    description="Creates a new chat thread for the authenticated user",
    responses={
        201: {"description": "Thread created successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Authentication required"},
        422: {"description": "Validation error"}
    }
)
async def create_thread(
    request: ChatThreadRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new chat thread.
    
    - **placement**: Where the chat is embedded (e.g., 'dashboard', 'onboarding')
    - **context**: Optional context data for the chat session
    
    Returns the created thread with generated ID and timestamps.
    """
    pass
```

**Documentation Categories:**
1. **Authentication**: Login, tokens, CSRF protection
2. **Chat**: Threads, messages, WebSocket endpoints
3. **Payments**: Invoices, transactions, webhooks
4. **Users**: Profiles, preferences, analytics
5. **Agents**: Registry, versions, executions

**Performance Considerations:**
- Cache OpenAPI schema generation
- Minimize documentation page bundle size
- Optimize Swagger UI loading
- Use CDN for documentation assets
- Implement progressive loading for large schemas
