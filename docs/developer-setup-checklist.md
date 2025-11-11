# 🚀 CapeControl Developer Setup Checklist

## Prerequisites ✅

- [ ] **Docker Desktop** installed and running
- [ ] **Heroku CLI** installed (`heroku --version`)
- [ ] **Git** configured with your credentials
- [ ] **Node.js 20+** and **Python 3.12+** installed

## Initial Setup 🛠️

### 1. Clone and Setup Environment

```bash
git clone https://github.com/robert1948/autorisen.git
cd autorisen
make install  # Sets up Python venv + dependencies
```

### 2. Environment Files

Create `.env` file in project root:

```bash
# Development settings
ENV=dev
DEBUG=true
DATABASE_URL=postgresql://devuser:devpass@localhost:5433/devdb

# Optional: Add OpenAI key for local agent testing
OPENAI_API_KEY=your-key-here
```

### 3. Start Local Development

```bash
# Start PostgreSQL + Redis via Docker Compose
make docker-run

# Verify local health
curl http://localhost:8000/api/health
```

## Deployment Access 🔑

### Heroku Apps

Request access to:
- [ ] **autorisen** (staging) - https://autorisen-dac8e65796e7.herokuapp.com
- [ ] **capecraft** (production) - https://capecraft.herokuapp.com

### Verification Commands

```bash
# Test Heroku access
heroku auth:whoami
heroku apps --team

# Check you can access both environments
heroku config --app autorisen | head -5
heroku config --app capecraft | head -5
```

## Understanding the Architecture 🏗️

### Key Concepts

- [ ] **Dual Environment**: Staging (`autorisen`) + Production (`capecraft`)
- [ ] **Separate Databases**: Each environment has its own PostgreSQL instance
- [ ] **Agent System**: CapeAI Guide + Domain Specialist with OpenAI integration
- [ ] **Marketplace**: Agent discovery and installation system

### Important URLs

| Environment | App URL | Health Check |
|-------------|---------|--------------|
| **Local** | http://localhost:8000 | /api/health |
| **Staging** | https://autorisen-dac8e65796e7.herokuapp.com | /api/health |
| **Production** | https://capecraft.herokuapp.com | /api/health |

## Development Workflow 🔄

### Daily Commands

```bash
# Pull latest changes
git pull origin main

# Build and test locally
make docker-build
make codex-test

# Deploy when ready (both environments)
make deploy-heroku
```

### Debugging Tools

```bash
# Check staging logs
heroku logs --tail --app autorisen

# Check production logs  
heroku logs --tail --app capecraft

# Test agent endpoints
curl https://autorisen-dac8e65796e7.herokuapp.com/api/agents/cape-ai-guide/health
```

## Reference Documentation 📚

- [ ] **[Deployment Environments](./deployment-environments.md)** - Complete environment details
- [ ] **[Quick Reference](./quick-reference.md)** - Handy commands cheat sheet
- [ ] **[Agents Guide](./agents.md)** - Agent development documentation
- [ ] **[Copilot Instructions](../.github/copilot-instructions.md)** - AI coding assistance setup

## VS Code Setup 💻

### Recommended Extensions

```bash
# Install via VS Code marketplace
- Python (ms-python.python)
- Pylint (ms-python.pylint)
- TypeScript (ms-vscode.vscode-typescript-next)
- Tailwind CSS (bradlc.vscode-tailwindcss)
- JSON (ms-vscode.vscode-json)
```

### Workspace

Open the project workspace:

```bash
code .vscode/capecontrol.code-workspace
```

This provides:
- Pre-configured debug settings
- Build and deploy tasks (Ctrl+Shift+P → "Tasks: Run Task")
- Health check commands
- Python environment integration

## Testing Your Setup ✅

### Final Verification

```bash
# 1. Local development works
curl http://localhost:8000/api/health
curl http://localhost:8000/api/marketplace/categories

# 2. Can deploy to staging
make deploy-heroku

# 3. Staging endpoints work
curl https://autorisen-dac8e65796e7.herokuapp.com/api/health
curl https://autorisen-dac8e65796e7.herokuapp.com/api/agents/cape-ai-guide/health

# 4. Production is accessible (read-only check)
curl https://capecraft.herokuapp.com/api/health
```

## Getting Help 🆘

### Common Issues

- **Docker not starting**: Check Docker Desktop is running
- **Port 8000 in use**: Stop local servers with `make docker-down`
- **Heroku access denied**: Request team access from project admin
- **Database connection**: Verify PostgreSQL container is running

### Resources

- **Slack/Discord**: Check team communication channels
- **GitHub Issues**: Create issues for bugs or questions
- **Documentation**: See `/docs` folder for detailed guides
- **Makefile**: Run `make help` for all available commands

---

## Welcome to the CapeControl team! 🎉

Once you complete this checklist, you'll be ready to contribute to our production agent platform. The dual-environment setup ensures safe development and deployment.
