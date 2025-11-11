# CapeControl Deployment Environments

## Environment Overview

CapeControl uses a dual-deployment strategy with separate staging and production environments:

- **Staging**: `autorisen` app → https://autorisen-dac8e65796e7.herokuapp.com
- **Production**: `capecraft` app → https://capecraft.herokuapp.com

## Database Configuration

### Staging (autorisen)

```yaml
Database: d57k62hgqkugv9
Cluster: c18qegamsgjut6.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com
User: uee32fstkm38fh
Environment: ENV=prod, DEBUG=false
```

### Production (capecraft)

```yaml
Database: d2ggg154krfc75
Cluster: c3nv2ev86aje4j.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com
User: u8h1en29rnu00
Environment: ENV=prod, DEBUG=false
```

## OpenAI Configuration

### Staging Environment

- **API Key**: sk-proj-TYJ0NJEVUfDc5Mg_...
- **Model**: gpt-4o-mini
- **Usage**: Development and testing

### Production Environment

- **API Key**: sk-proj-ySicmJpiL1X8Kgzkk-...
- **Model**: gpt-4o-mini
- **Usage**: Live customer environment

## Deployment Process

### Single Command Deployment

```bash
make deploy-heroku
```

This deploys to **both** environments:

1. Builds Docker image locally
1. Pushes to `autorisen` (staging)
1. Pushes to `capecraft` (production)
1. Runs release commands on production

### Individual Environment Deployment

```bash
# Staging only
heroku container:push web --app autorisen
heroku container:release web --app autorisen

# Production only  
heroku container:push web --app capecraft
heroku container:release web --app capecraft
```

## Agent System Status

### Current Implementation

- ✅ **CapeAI Guide Agent**: Fully deployed and functional
  - Health: `/api/agents/cape-ai-guide/health`
  - Capabilities: `/api/agents/cape-ai-guide/capabilities`
  - Ask: `/api/agents/cape-ai-guide/ask` (requires auth + OpenAI)

- ✅ **CapeAI Domain Specialist**: Deployed with 4 domains
  - Health: `/api/agents/cape-ai-domain-specialist/health`
  - Capabilities: `/api/agents/cape-ai-domain-specialist/capabilities`
  - Ask: `/api/agents/cape-ai-domain-specialist/ask` (requires auth + OpenAI)

### Marketplace System

- ✅ **Analytics**: `/api/marketplace/analytics`
- ✅ **Categories**: `/api/marketplace/categories`
- ✅ **Search**: `/api/marketplace/search`
- ✅ **Discovery**: Full agent discovery and installation flow

## Environment Isolation

### Benefits

1. **Data Isolation**: Staging tests don't affect production data
1. **API Usage Separation**: OpenAI usage tracked separately
1. **Independent Scaling**: Different resource allocation per environment
1. **Safe Testing**: Can test breaking changes in staging

### Considerations

- Marketplace agents published in staging won't appear in production
- Database schemas must be migrated to both environments
- Environment variables must be configured separately
- Different OpenAI usage quotas and billing

## Quick Reference Commands

### Environment Info

```bash
# Check staging config
heroku config --app autorisen | grep -E "(DATABASE_URL|OPENAI|ENV)"

# Check production config  
heroku config --app capecraft | grep -E "(DATABASE_URL|OPENAI|ENV)"
```

### Logs and Debugging

```bash
# Staging logs
heroku logs --tail --app autorisen

# Production logs
heroku logs --tail --app capecraft

# Run commands in staging
heroku run --app autorisen "python -c 'print(\"Hello from staging\")'"

# Run commands in production
heroku run --app capecraft "python -c 'print(\"Hello from production\")'"
```

### Health Checks

```bash
# Staging health
curl https://autorisen-dac8e65796e7.herokuapp.com/api/health

# Production health
curl https://capecraft.herokuapp.com/api/health

# Agent health (staging)
curl https://autorisen-dac8e65796e7.herokuapp.com/api/agents/cape-ai-guide/health
```

## Migration Strategy

When making database changes:

1. Test migrations locally first
1. Apply to staging via `heroku run --app autorisen "alembic upgrade head"`
1. Verify staging functionality
1. Apply to production via `heroku run --app capecraft "alembic upgrade head"`
1. Monitor production health

## Security Notes

- Both environments use production-grade security settings
- Different OpenAI API keys prevent cross-environment usage leaks
- Database credentials are auto-rotated by Heroku PostgreSQL
- All connections use SSL/TLS encryption

---

**Last Updated**: November 11, 2025
**Deployment Version**: v0.2.1
