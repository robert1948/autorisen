# Scripts Directory

This directory contains various utility scripts for the autorisen project.

## Database Management

### `setup_local_postgres.sh`
**Purpose**: Automated local PostgreSQL development environment setup
**Usage**: 
```bash
bash ./scripts/setup_local_postgres.sh "postgres://[HEROKU_DATABASE_URL]" [local_db_name] [local_username]
```
**Example**:
```bash
bash ./scripts/setup_local_postgres.sh "postgres://user:pass@host:port/db" autorisen_local vscode
```
**Features**:
- Creates local PostgreSQL database with production schema
- Handles SSL connections to Heroku PostgreSQL
- Automatically dumps and restores database schema
- Updates `.env` file with local database configuration
- Sets up local user with proper permissions
- Compatible with PostgreSQL 16+ and 17+

### `dummy_register.py`
**Purpose**: Database testing and user creation utility
**Usage**:
```bash
python ./scripts/dummy_register.py
```
**Features**:
- Creates test users for development
- Validates database connectivity and schema
- Tests user registration workflow
- Works with both PostgreSQL and SQLite databases

## Development Servers

### `start-localhost-autorisen.sh`
**Purpose**: Start FastAPI backend server for local development
**Usage**:
```bash
./scripts/start-localhost-autorisen.sh [port] [host]
```
**Default**: Port 8000, host localhost

### `start-backend.sh` / `start-local.sh`
**Purpose**: Alternative backend startup scripts

## Testing & Validation

### `check_sanity.sh`
**Purpose**: Run comprehensive system checks
### `complete_stripe_test.sh`
**Purpose**: Test Stripe payment integration
### `test_enhanced_auth.sh` / `test_enhanced_auth_complete.sh`
**Purpose**: Test authentication system

## Deployment & Assets

### `deploy-static-assets.sh`
**Purpose**: Deploy static assets to S3
### `upload-static-assets.sh` / `upload_static_assets.sh`
**Purpose**: Upload static files to cloud storage
### `verify-production-images.sh`
**Purpose**: Verify production image assets

## Utilities

### `get-health.sh`
**Purpose**: Check application health endpoints
### `sync_checklist.sh`
**Purpose**: Synchronize deployment checklists
### `cache-bust.cjs`
**Purpose**: Cache busting for static assets

## Archive
The `archive/` directory contains deprecated or legacy scripts.

## Setup
The `setup/` directory contains environment setup scripts.

## Tests  
The `tests/` directory contains test-specific scripts.

---

**Note**: Most scripts should be run from the repository root directory. Check individual script headers for specific usage instructions.
