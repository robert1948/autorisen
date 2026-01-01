# Docker Hub Deployment Summary

**Date:** January 1, 2026
**Version:** v0.2.10
**Status:** ✅ COMPLETED

## Overview

Successfully updated Docker Hub registry with the latest production images for both AutoRisen and CapeControl platforms. This release includes the full Payments integration, Marketplace UI, and database seeding capabilities.

## Deployed Images

### AutoRisen Platform

- **Repository:** `stinkie/autorisen`
- **Tags Pushed:**
  - `v0.2.10` (SHA: `sha256:f4c31cf5e22710220951acb8f7b925b01a1fb3b4b5411372b9c519a5a75994d4`)
  - `latest` (SHA: `sha256:f4c31cf5e22710220951acb8f7b925b01a1fb3b4b5411372b9c519a5a75994d4`)
- **Status:** Successfully pushed to Docker Hub

### CapeControl Platform

- **Repository:** `stinkie/capecraft`
- **Tags Pushed:**
  - `v0.2.10` (SHA: `sha256:f4c31cf5e22710220951acb8f7b925b01a1fb3b4b5411372b9c519a5a75994d4`)
  - `latest` (SHA: `sha256:f4c31cf5e22710220951acb8f7b925b01a1fb3b4b5411372b9c519a5a75994d4`)
- **Status:** Successfully pushed to Docker Hub

## Release Highlights

### New Features
- **Payments Integration:** Full PayFast ITN validation and transaction persistence.
- **Marketplace:** Integrated Marketplace UI with backend API.
- **Database Seeding:** Added `scripts/seed_marketplace.py` for automated agent population.
- **Maintenance:** Included `scripts/` directory in production image for remote operations.

### Technical Details
- **Base Images:** Python 3.12-slim + Node 20-alpine
- **Architecture:** linux/amd64
- **Security:** Non-root user execution, updated dependencies.
