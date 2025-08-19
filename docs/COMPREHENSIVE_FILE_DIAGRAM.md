# Comprehensive File Diagram
> Snapshot of repository structure for quick onboarding. Update after major refactors.

```
autorisen/
├─ .devcontainer/
│  ├─ devcontainer.json
│  ├─ Dockerfile
│  └─ postCreate.sh
├─ .github/workflows/
│  ├─ deploy-staging.yml
│  └─ deploy.yml
├─ backend/
│  ├─ alembic/
│  ├─ app/
│  │  ├─ api/
│  │  │  └─ payment.py
│  │  ├─ config/
│  │  ├─ core/
│  │  ├─ middleware/
│  │  ├─ models/
│  │  ├─ payfast/
│  │  ├─ routes/
│  │  └─ services/
│  │     ├─ ai_*.py
│  │     ├─ audit_service.py
│  │     ├─ analytics_service.py
│  │     ├─ auth_service.py
│  │     └─ alert_service.py
└─ docs/ (this folder)
```
