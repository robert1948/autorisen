# CapeControl Security Posture

> **Version:** 1.0  
> **Last Updated:** 2026-02-24  
> **Classification:** Internal — Distribute to investors, auditors, and enterprise prospects under NDA.

---

## 1. Authentication Architecture

### 1.1 JWT Token System

| Property | Value |
|---|---|
| Algorithm | HS256 |
| Access Token TTL | 7 days |
| Refresh Token | Cookie-based rotation |
| Token Versioning | `token_version` column; incrementing invalidates all sessions |
| JTI Deny List | Redis-backed per-token revocation |

- Tokens are issued via `/api/auth/login` and rotated via `/api/auth/refresh`.
- All tokens carry `jti`, `user_id`, `email`, `role`, and `token_version` claims.
- Session invalidation is immediate: incrementing `token_version` rejects all outstanding tokens for a user.

### 1.2 OAuth 2.0 Providers

| Provider | Flow | Status |
|---|---|---|
| Google | Authorization Code | ✅ Production |
| LinkedIn | Authorization Code | ✅ Production |

OAuth callbacks merge-or-create users and issue the same JWT token structure as email/password login.

### 1.3 CSRF Protection

- Custom `CSRFMiddleware` issues a CSRF token via `GET /api/auth/csrf`.
- All state-changing requests (POST/PUT/PATCH/DELETE) must include the `X-CSRF-Token` header.
- Token validation runs before request routing.

---

## 2. Authorization & Access Control

### 2.1 Role-Based Access Control (RBAC)

**Role hierarchy:**

| Role | Scope | Assignment |
|---|---|---|
| Customer | Standard platform access | Default on registration |
| Developer | Extended API access, agent management | Registration or admin promotion |
| Admin | Full platform management | Manual assignment |

**Implementation:**

- **Scalar path (fast):** `User.role` string column checked by `require_roles()` dependency.
- **Many-to-many path (granular):** `users → user_roles → roles → role_permissions → permissions` join chain. `require_roles()` checks both paths; `require_permissions()` checks the join chain for fine-grained permission codes (e.g., `rag.document.delete`).

### 2.2 Permission Codes

Permission codes follow the pattern `<module>.<resource>.<action>`:

```
auth.user.read
auth.user.write
rag.document.upload
rag.document.delete
rag.query.execute
capsules.run.execute
agents.task.create
```

Permissions are linked to roles via the `role_permissions` join table. New permissions can be seeded without code changes.

### 2.3 Multi-Tenant Isolation

- `Organization` and `OrganizationMember` models provide tenant boundaries.
- `get_org_context()` dependency validates `X-Organization-Id` header and confirms membership before granting access.
- RAG documents are scoped to `owner_id`: users can only query their own approved documents.

---

## 3. Data Protection

### 3.1 Data at Rest

| Asset | Protection |
|---|---|
| User passwords | bcrypt hash (via Passlib) |
| Database | Heroku PostgreSQL with encryption at rest (AES-256) |
| JWT signing key | `SECRET_KEY` environment variable, never committed |
| API keys (OpenAI, Anthropic) | Environment variables only |

### 3.2 Data in Transit

- All production traffic is HTTPS-only (enforced by Heroku edge).
- Internal service communication is container-local (no inter-service network calls in the current architecture).
- CORS middleware restricts origins to the configured `APP_ORIGIN` and localhost development URLs.

### 3.3 Sensitive Data Handling

- Email addresses are stored in plaintext for login and communication.
- No PII beyond name/email/company is collected.
- Password reset tokens are single-use with time-limited expiry.
- Audit logs record `actor_id` and `actor_email` but not request/response bodies.

---

## 4. Input Validation & Sanitization

### 4.1 Input Sanitization Middleware

- `InputSanitizationMiddleware` (when available) scans request bodies for injection patterns.
- All API schemas use Pydantic v2 models with strict type validation, length constraints, and enum enforcement.

### 4.2 Rate Limiting

| Endpoint Group | Limit | Backend |
|---|---|---|
| Auth endpoints | Configurable per-route | Redis (slowapi) |
| API general | Configurable global | Redis (slowapi) |
| Health/status | Exempt | — |

Rate limit state is stored in Redis and survives application restarts.

### 4.3 DDoS Protection

- `DDoSProtectionMiddleware` (when available) tracks request rates per IP and blocks excessive traffic.
- Heroku's edge load balancer provides additional L3/L4 protection.

---

## 5. AI-Specific Security

### 5.1 RAG Pipeline Controls

| Control | Description |
|---|---|
| Approved Documents Only | Only explicitly uploaded and approved documents enter the retrieval pipeline |
| Owner Scoping | Users can only query documents they own |
| Unsupported Policy | Configurable behavior when no documents match: `refuse`, `flag`, or `allow` |
| Evidence Trace | Every RAG query produces a full audit trail with citations, similarity scores, and actor identity |
| Policy Enforcement | `_apply_unsupported_policy()` runs on every agent response, not just RAG queries |

### 5.2 LLM Provider Security

- API keys are never logged or returned in responses.
- LLM calls are made server-side only; client never has direct provider access.
- Fallback chain: Anthropic → OpenAI → graceful degradation message.
- No user data is used for model training (per provider DPA terms).

### 5.3 Capsule Workflow Isolation

- Each capsule defines its own document type scope and retrieval parameters.
- Capsule system prompts are server-defined templates, not user-controllable.
- Capsule responses carry the same citation and evidence trace as raw RAG queries.

---

## 6. Audit & Monitoring

### 6.1 Audit Trail

- `AuditEvent` model records user actions with actor identity, event type, and timestamps.
- RAG queries are logged in `rag_query_logs` with query text, grounding status, citations, and processing time.
- Evidence pack export (`GET /api/rag/evidence/export`) bundles all audit data for compliance review.

### 6.2 Request Monitoring

- `MonitoringMiddleware` collects per-path request counts, latency percentiles (p50/p95/p99), and status code distribution.
- Metrics are available at `GET /api/metrics` (JSON snapshot).
- Health endpoints: `/api/health` (with DB check), `/api/health/alive`, `/api/health/ping`, `/api/version`.

### 6.3 Security Stats

- `GET /api/security/stats` reports status of DDoS protection, input sanitization, rate limiting, and CSRF.

---

## 7. Infrastructure Security

### 7.1 Container Security

- Multi-stage Docker builds minimize final image size and attack surface.
- Non-root user execution in production containers.
- No secrets baked into images; all configuration via environment variables.

### 7.2 Dependency Management

- Python dependencies pinned in `requirements.txt` with hash verification where available.
- GitHub Actions CI runs automated security scanning on every PR.
- `ruff` linter enforces code quality and catches common security anti-patterns.

### 7.3 Environment Separation

| Environment | URL | Database | Debug |
|---|---|---|---|
| Local | `localhost:5173` / `:8000` | PostgreSQL `:5433` or SQLite | `DEBUG=true` |
| Staging | `dev.cape-control.com` | Heroku PostgreSQL | `DEBUG=false` |
| Production | `cape-control.com` | Heroku PostgreSQL (isolated) | `DEBUG=false` |

- Staging and production use separate databases with no cross-access.
- `ENV=prod` enables production hardening: reCAPTCHA, stricter CORS, CSRF enforcement.

---

## 8. Incident Response

### 8.1 Token Revocation

**Single user:** Increment `token_version` → all tokens for that user are immediately rejected.

**Global:** Rotate `SECRET_KEY` → all JWTs become invalid platform-wide.

### 8.2 Breach Protocol

1. Rotate all API keys (OpenAI, Anthropic, OAuth client secrets).
2. Increment `SECRET_KEY` to invalidate all sessions.
3. Reset affected user passwords and increment their `token_version`.
4. Review audit logs via evidence pack export.
5. Notify affected users per POPIA/GDPR requirements.

### 8.3 Contact

Security issues should be reported to the development team via the internal issue tracker. No public bug bounty program is currently active.

---

## 9. Compliance Considerations

| Framework | Status | Notes |
|---|---|---|
| POPIA (South Africa) | In scope | Minimal PII collection; data residency via Heroku region selection |
| GDPR | Aware | Applicable if EU users onboarded; data export/deletion endpoints planned |
| SOC 2 | Not yet | Evidence pack generation supports future audit readiness |
| ISO 27001 | Not yet | RBAC + audit trail provide foundational controls |

---

## 10. Known Limitations & Roadmap

| Gap | Severity | Planned Resolution |
|---|---|---|
| No field-level encryption for PII | Medium | Database-level encryption covers current needs |
| No WAF beyond middleware | Medium | Evaluate Cloudflare/AWS WAF before enterprise tier |
| Single-region deployment | Low | Heroku multi-region or AWS ECS migration path documented |
| No automated pen testing | Medium | Integrate DAST tooling in CI pipeline |
| Rate limit bypass via header spoofing | Low | Heroku edge strips `X-Forwarded-For` manipulation |
