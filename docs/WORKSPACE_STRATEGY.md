# Workspace Strategy

## Definitions

**VS Code Control Plane**: The authoritative execution environment for CapeControl within this repository. It runs commands, applies code changes, executes `make` targets, and enforces repository workflows via agents and automation.

- **VS Code Control Plane and Agents (within this repository)** are responsible for execution, automation, and code manipulation.
- **External Chat (ChatGPT)** provides strategic guidance, prompt review, and architectural oversight.
- **No automated change is accepted without explicit human review and approval.**
- **`make` is the authoritative interface** for running, testing, and deploying system actions.
