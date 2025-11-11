# Codex Agent Testing Framework Generator

## Objective

Use GitHub Copilot to automatically generate comprehensive test suites for our agent system, including WebSocket streaming, task lifecycle verification, and marketplace integration validation.

## Codex Prompt for Agent Testing

```
# @Codex: Generate comprehensive test framework for CapeControl agent system

Given this architecture:
- Task execution system with tasks, runs, audit_events tables
- CapeAI Guide agent with OpenAI integration
- WebSocket streaming for real-time updates
- FastAPI router integration
- Database persistence with UUID relationships

Create a comprehensive test framework that includes:

1. **Unit Tests**
   - Agent schema validation
   - Knowledge base functionality  
   - Service layer operations
   - Prompt template generation

2. **Integration Tests**
   - FastAPI endpoint validation
   - Database transaction testing
   - Auth integration testing
   - WebSocket connection testing

3. **End-to-End Tests**
   - Complete task execution flows
   - Multi-step agent workflows
   - Error handling and recovery
   - Performance benchmarking

4. **Load Testing**
   - Concurrent WebSocket connections
   - High-volume task processing
   - OpenAI API rate limiting
   - Database connection pooling

Generate pytest test files with:
- Fixtures for database setup/teardown
- Mock OpenAI responses for testing
- WebSocket test clients
- Performance metrics collection
- Test data generators
- Error scenario coverage

File structure:
tests/agents/
├── unit/
├── integration/  
├── e2e/
├── load/
├── fixtures/
└── conftest.py
```

## Implementation Command

Use this command to engage Codex for test generation:

```bash
# Start Codex session for test framework
make codex-generate-tests
```
