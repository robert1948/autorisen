# Marketplace Module Audit & Task List

## Overview

The Marketplace module (`backend/src/modules/marketplace`) is currently in a scaffolded state. Critical business logic for authentication, installation, and metrics is missing.

## Critical Missing Features

### 1. Authentication & User Context

- [ ] **Extract User ID**: `router.py` endpoints need to extract `user_id` from the authenticated session. Currently marked as `TODO`.
- [ ] **Permission Checks**: Verify user has permission to install/manage agents.

### 2. Installation Logic (`service.py`)

- [ ] **Dependency Resolution**: Implement logic to check and resolve agent dependencies before installation.
- [ ] **Installation Execution**: Implement the actual steps to "install" an agent (e.g., database records, config updates).
- [ ] **Duplicate Check**: Prevent installing an agent that is already installed.
- [ ] **Audit Logging**: Track installation events in the audit log.

### 3. Metrics & Algorithms

- [ ] **Trending Algorithm**: `router.py` has a placeholder for trending agents. Needs implementation based on downloads/usage.
- [ ] **Download Tracking**: Increment download counts on installation.
- [ ] **Rating Aggregation**: Calculate average ratings from user reviews (currently hardcoded or missing).

### 4. Data Management

- [ ] **JSON Filtering**: Implement proper filtering for JSON fields in the database queries.
- [ ] **Featured Agents**: Add logic to toggle and retrieve "Featured" agents.

## File-Specific TODOs

### `backend/src/modules/marketplace/router.py`

- `TODO: Add user authentication and extract user_id`
- `TODO: Implement proper trending algorithm`
- `TODO: Add featured flag to agent model`

### `backend/src/modules/marketplace/service.py`

- `TODO: Implement proper JSON field filtering`
- `TODO: Add download count/popularity metrics`
- `TODO: Add rating aggregation`
- `TODO: Check if user already has this agent installed`
- `TODO: Handle dependency resolution`
- `TODO: Perform actual installation steps`

## Recommendations

1. **Prioritize Installation Logic**: The marketplace is unusable without the ability to actually "install" an agent.
1. **Implement Auth**: Secure the endpoints immediately.
1. **Defer Metrics**: Trending and complex ratings can be Phase 2. Focus on core functionality first.
