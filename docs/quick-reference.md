# CapeControl Quick Reference

## 🚀 Deployment Commands

```bash
# Deploy to both staging and production
make deploy-heroku

# Deploy to staging only
heroku container:push web --app autorisen
heroku container:release web --app autorisen

# Deploy to production only
heroku container:push web --app capecraft
heroku container:release web --app capecraft
```

## 🔍 Environment Info

```bash
# Check staging config
heroku config --app autorisen | grep -E "(DATABASE|OPENAI|ENV)"

# Check production config  
heroku config --app capecraft | grep -E "(DATABASE|OPENAI|ENV)"
```

## 📊 Health Checks

### System Health

```bash
# Staging
curl -s https://autorisen-dac8e65796e7.herokuapp.com/api/health | jq

# Production
curl -s https://capecraft.herokuapp.com/api/health | jq
```

### Marketplace

```bash
# Analytics
curl -s https://autorisen-dac8e65796e7.herokuapp.com/api/marketplace/analytics | jq

# Categories
curl -s https://autorisen-dac8e65796e7.herokuapp.com/api/marketplace/categories | jq

# Search
curl -s https://autorisen-dac8e65796e7.herokuapp.com/api/marketplace/search | jq
```

### Agents

```bash
# CapeAI Guide health
curl -s https://autorisen-dac8e65796e7.herokuapp.com/api/agents/cape-ai-guide/health | jq

# CapeAI Guide capabilities  
curl -s https://autorisen-dac8e65796e7.herokuapp.com/api/agents/cape-ai-guide/capabilities | jq

# Domain Specialist health
curl -s https://autorisen-dac8e65796e7.herokuapp.com/api/agents/cape-ai-domain-specialist/health | jq
```

## 📝 Logs

```bash
# Staging logs
heroku logs --tail --app autorisen

# Production logs
heroku logs --tail --app capecraft

# Filter for errors
heroku logs --app autorisen | grep -i error

# Filter for specific module
heroku logs --app autorisen | grep -i agents
```

## 🗄️ Database

```bash
# Connect to staging database
heroku pg:psql --app autorisen

# Connect to production database
heroku pg:psql --app capecraft

# Run migrations on staging
heroku run --app autorisen "alembic upgrade head"

# Run migrations on production
heroku run --app capecraft "alembic upgrade head"
```

## 🔧 Development

```bash
# Start local development
make docker-run

# Run tests
make codex-test

# Build image
make docker-build

# Local health check
curl http://localhost:8000/api/health
```

## 🌐 URLs

### Staging (autorisen)

- **App**: https://autorisen-dac8e65796e7.herokuapp.com
- **Health**: https://autorisen-dac8e65796e7.herokuapp.com/api/health
- **Docs**: https://autorisen-dac8e65796e7.herokuapp.com/docs

### Production (capecraft)  

- **App**: https://capecraft.herokuapp.com
- **Health**: https://capecraft.herokuapp.com/api/health
- **Docs**: https://capecraft.herokuapp.com/docs

## 🔑 Environment Variables

### Key Variables

- `ENV=prod` (both environments)
- `DEBUG=false` (both environments)  
- `OPENAI_API_KEY` (different keys per environment)
- `OPENAI_MODEL=gpt-4o-mini` (both environments)
- `DATABASE_URL` (different databases per environment)

### Agent Configuration

- `CAPE_AI_GUIDE_MODEL=gpt-4` (default)
- `DOMAIN_SPECIALIST_MODEL=gpt-4` (default)

## ⚡ Quick Debugging

```bash
# Check if agents router is loaded
heroku logs --app autorisen | grep "agents router"

# Test agent import
heroku run --app autorisen "python -c 'from backend.src.modules.agents.cape_ai_guide.router import router; print(\"✅ CapeAI Guide loaded\")'"

# Check routes
heroku run --app autorisen "python -c 'from backend.src.modules.agents.router import router; print([r.path for r in router.routes])'"
```

---
**Tip**: Bookmark this file for quick access during development! 📌
