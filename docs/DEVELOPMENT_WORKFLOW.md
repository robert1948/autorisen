# Development Workflow and Component Management

## Project Structure Overview

```
autorisen (Development/Staging) → capecraft (Production)
```

- **autorisen**: Development and staging environment
- **capecraft**: Protected production environment (Heroku)
- **capecraft**: Component reference source (most up-to-date)

## Component Source Management

### Source Repository Priority
- **Primary Development**: autorisen project (this repository)
- **Reference Components**: Heroku capecraft (production environment)
- **Production Target**: capecraft (live site)

### Component Integration Workflow
1. **Missing Components**: Copy from capecraft production environment
2. **Development Priority**: autorisen must stay ahead of capecraft
3. **Component Testing**: All components tested in autorisen before production

## Deployment Pipeline Strategy

### 1. Development Phase (autorisen)
```bash
# Local Development Environment
git clone https://github.com/robert1948/autorisen.git
cd autorisen

# Setup development environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Setup local PostgreSQL (production parity)
bash ./scripts/setup_local_postgres.sh

# Start development servers
./scripts/dev-start.sh
```

### 2. Testing Phase (autorisen staging)
- **Unit Tests**: `npm test` (frontend) + `pytest` (backend)
- **Integration Tests**: Full API + UI testing
- **Performance Tests**: Load testing and optimization
- **Security Tests**: Input validation and vulnerability scanning

### 3. Production Deployment (capecraft)
- **Pre-deployment Checks**: All tests passing
- **Zero-downtime Deployment**: Blue-green or rolling deployment
- **Rollback Plan**: Immediate rollback capability
- **Health Monitoring**: Real-time service monitoring

## Quality Assurance Protocol

### Pre-Production Checklist
- [ ] All features tested in autorisen environment
- [ ] Unit tests passing (>95% coverage)
- [ ] Integration tests passing
- [ ] Performance benchmarks met
- [ ] Security scan completed
- [ ] Database migrations tested
- [ ] Frontend build successful
- [ ] API endpoints validated

### Service Continuity Requirements
- **Zero Disruption**: No service interruption during deployment
- **Minimal Downtime**: <30 seconds maintenance windows only
- **Health Checks**: Continuous monitoring of all services
- **Rollback Time**: <2 minutes to previous stable version

## Development Environment Setup

### Local Development Stack
```bash
# Backend (FastAPI + PostgreSQL)
cd /workspaces/autorisen/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (React + Vite)
cd /workspaces/autorisen/client
npm run dev

# Database
# PostgreSQL: autorisen_local (development)
# Heroku Postgres: capecraft (production)
```

### Environment Configuration
```bash
# Development (.env.development)
DATABASE_URL=postgresql://postgres:password@localhost:5432/autorisen_local
ENVIRONMENT=development
DEBUG=true

# Production (.env.production)
DATABASE_URL=${HEROKU_POSTGRES_URL}
ENVIRONMENT=production
DEBUG=false
```

## Component Integration from capecraft

### Copying Components
```bash
# Access capecraft production environment
heroku git:clone -a capecraft ../capecraft-reference

# Copy missing components
cp -r ../capecraft-reference/client/src/components/* ./client/src/components/
cp -r ../capecraft-reference/backend/app/* ./backend/app/

# Update imports and dependencies
npm install  # Frontend dependencies
pip install -r requirements.txt  # Backend dependencies
```

### Integration Testing
```bash
# Test copied components
npm test -- --coverage
pytest backend/tests/ -v

# Build and verify
npm run build
python -m pytest backend/integration_tests/
```

## Deployment Commands

### Development to Staging
```bash
# Ensure all tests pass
npm test && pytest

# Build frontend
npm run build

# Deploy to autorisen staging
git add .
git commit -m "feat: staging deployment $(date)"
git push origin main
```

### Staging to Production (capecraft)
```bash
# Final validation
./scripts/pre-production-check.sh

# Deploy to capecraft (protected)
# This should be done through CI/CD pipeline
# with proper approval gates and rollback mechanisms
```

## Monitoring and Health Checks

### Local Development Health
```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend build status
npm run build && echo "✅ Build successful"

# Database connectivity
psql -d autorisen_local -c "SELECT version();"
```

### Production Health (capecraft)
- **Uptime Monitoring**: 99.9% SLA requirement
- **Performance Metrics**: Response time <200ms
- **Error Rates**: <0.1% error rate
- **Database Health**: Connection pool monitoring

## Emergency Procedures

### Rollback Process
1. **Immediate**: Revert to last known good deployment
2. **Database**: Restore from latest backup if needed
3. **Communication**: Notify stakeholders of incident
4. **Post-mortem**: Document root cause and prevention

### Incident Response
- **Detection**: Automated alerts + monitoring
- **Response Time**: <5 minutes acknowledgment
- **Resolution Time**: <30 minutes for critical issues
- **Communication**: Status page + stakeholder updates

This workflow ensures autorisen serves as a robust development/staging environment that protects the capecraft production environment while maintaining high service reliability standards.
