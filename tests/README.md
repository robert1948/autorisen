# Test Configuration and Setup for CapeControl

## Running Tests

### Backend Tests
```bash
cd /workspaces/localstorm/backend
source ../.venv/bin/activate
pip install pytest pytest-asyncio
python -m pytest tests/ -v
```

### Frontend Tests (Future)
```bash
cd /workspaces/localstorm/client
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest jsdom
npm run test
```

## Test Structure

### Backend (`/backend/tests/`)
- `test_auth.py` - Authentication system tests
- `test_database.py` - Database model tests
- `test_capeai.py` - CapeAI system integration tests

### Frontend (`/client/src/__tests__/`)
- `components/` - React component tests
- `hooks/` - Custom hook tests
- `pages/` - Page component tests
- `utils/` - Utility function tests

## Coverage Goals
- **Backend**: 80%+ code coverage
- **Frontend**: 70%+ component coverage
- **Integration**: End-to-end flow testing

## Continuous Integration
Tests should be integrated into the deployment pipeline to run on:
- Pull requests
- Main branch pushes
- Production deployments
