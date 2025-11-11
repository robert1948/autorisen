# Codex Agent Marketplace Generator

## Objective

Use Codex to automatically generate a complete agent marketplace system with discovery, versioning, and publishing capabilities.

## Codex Prompt for Marketplace

```
# @Codex: Generate agent marketplace infrastructure

Based on our CapeAI Guide agent template, create a complete marketplace system:

## Core Features to Generate:

### 1. Agent Registry & Discovery
- Agent catalog with search/filtering
- Category-based organization  
- Rating and review system
- Usage analytics tracking

### 2. Publishing Pipeline
- Automated agent validation
- Version management (semver)
- Documentation generation
- Security scanning

### 3. Installation & Management
- One-click agent installation
- Dependency resolution
- Update management
- License compliance

### 4. Developer Tools
- Agent template generator
- Testing framework integration
- Performance benchmarking
- Deployment automation

## Generate These Components:

```python
# Agent marketplace models
class AgentMarketplace(BaseModel):
    id: str
    name: str
    description: str
    category: str
    version: str
    author: str
    downloads: int
    rating: float
    published_at: datetime

# Publishing API
@router.post("/marketplace/publish")
async def publish_agent(...)

# Discovery API  
@router.get("/marketplace/search")
async def search_agents(...)

# Installation API
@router.post("/marketplace/install/{agent_id}")
async def install_agent(...)
```

File structure to generate:

```
backend/src/modules/marketplace/
├── models.py           # Marketplace data models
├── router.py          # API endpoints
├── publisher.py       # Publishing pipeline
├── installer.py       # Agent installation
├── validator.py       # Agent validation
└── analytics.py       # Usage tracking
```

Frontend components:

```
client/src/marketplace/
├── AgentCatalog.tsx   # Browse agents
├── AgentDetail.tsx    # Agent details page
├── Publisher.tsx      # Publish new agents
└── Analytics.tsx      # Usage analytics
```

```

## Implementation Strategy

1. **Phase 1**: Core marketplace infrastructure
2. **Phase 2**: Publishing and validation pipeline  
3. **Phase 3**: Frontend marketplace UI
4. **Phase 4**: Analytics and monetization
