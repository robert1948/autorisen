# 🧠 Codex Integration Guide

**Project:** AutoLocal / CapeControl  
**Maintainer:** Robert Kleyn  
**Purpose:** Enable Codex as a local project intelligence layer that understands the repo’s context, assists with documentation, playbooks, and automation tasks.

---

## 1. Overview

Codex acts as a **repo-native assistant** in VS Code that reads from key context files and generates context-aware suggestions.  
It uses `.vscode/codex.prompt.md` as its system prompt and the `.vscode/settings.json` file to list context files.

**Core objectives:**
- Keep the repo stable and releasable.
- Offer accurate, minimal code/document changes.
- Maintain synchronized project knowledge across key docs and playbooks.

---

## 2. Context Files

Codex reads from these Markdown files each time it activates:

| File | Purpose |
|------|----------|
| `docs/DEVELOPMENT_CONTEXT.md` | Architecture, stack, and configuration reference |
| `docs/MVP_SCOPE.md` | Product scope and milestone definitions |
| `docs/Checklist_MVP.md` | Running checklist for MVP readiness |
| `docs/agents.md` | Overview of project agents (QA, DevOps, etc.) |
| `docs/Heroku_Pipeline_Workflow.md` | Staging → Production deployment pipeline |
| `.vscode/codex.prompt.md` | System prompt (Codex behavior + rules) |

> 🧩 To verify these at any time:  
>
> ```bash
> make codex-check
> ```

---

## 3. VS Code Setup

Codex uses workspace settings in `.vscode/settings.json`:

```json
{
  "codex.enabled": true,
  "codex.projectName": "CapeControl",
  "codex.contextFiles": [
    "docs/DEVELOPMENT_CONTEXT.md",
    "docs/MVP_SCOPE.md",
    "docs/Checklist_MVP.md",
    "docs/agents.md",
    "docs/Heroku_Pipeline_Workflow.md",
    ".vscode/codex.prompt.md"
  ],
  "codex.maxTokens": 2000,
  "codex.summarizeLongFiles": true
}
