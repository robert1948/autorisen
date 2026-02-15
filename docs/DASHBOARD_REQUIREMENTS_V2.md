# Dashboard Content Requirements — Dynamic & Role-Aware

**Document version:** 2.0 — Revised and expanded  
**Last updated:** 2026-02-15  
**Status:** Implementation in progress

---

## Revision Changelog

| Area | Issue Found | Action Taken |
|------|-------------|--------------|
| Structure | Inconsistent heading hierarchy and formatting | Standardised all sections with clear numbering |
| Security | Missing CORS, CSP, and token rotation guidance | Added detailed security hardening subsection |
| Data Contract | Role table lacked granularity on field-level access | Expanded with field-level permissions |
| Error Handling | Generic failure handling described | Added specific error codes and recovery flows |
| Accessibility | Mentioned but underspecified | Expanded to WCAG 2.1 AA compliance checklist |
| Performance | No mention of caching strategy beyond client state | Added CDN, stale-while-revalidate, and TTL guidance |
| GDPR/Privacy | Mentioned briefly; incomplete | Added dedicated compliance subsection |
| Code Example | Functional but missing error boundaries and suspense | Improved with production-grade patterns |
| Mobile | Vague "test on phone" instruction | Added specific breakpoint and interaction targets |
| API Design | Endpoint examples lacked versioning rationale | Added API design principles section |

---

## 1. Authentication and Profile Fetching (Core Trigger)

### 1.1 Authentication Flow

On successful login (JWT or session validated), the client must immediately fetch the full user profile from a dedicated, rate-limited endpoint.

- **Primary Endpoint:** `GET /api/v1/auth/me`
- **Fallback Endpoint:** `GET /api/v1/profile/{userId}`

### 1.2 Profile Response Schema

```json
{
  "userId": "uuid-v4",
  "email": "user@example.com",
  "emailVerified": true,
  "role": "user | developer | admin",
  "name": "string",
  "displayName": "string",
  "avatarUrl": "string | null",
  "createdAt": "ISO-8601",
  "lastLogin": "ISO-8601",
  "status": "active | suspended | pending_verification | deactivated",
  "preferences": {
    "timezone": "string",
    "locale": "string",
    "notificationsEnabled": true
  },
  "account": {
    "balance": 0.00,
    "currency": "USD",
    "subscriptionTier": "free | pro | enterprise"
  },
  "developerProfile": null
}
```

**Conditional Developer Fields** (returned only when `role === "developer"` or `role === "admin"`):

```json
{
  "developerProfile": {
    "developerId": "uuid-v4",
    "apiKeyStatus": "active | revoked | expired",
    "apiKeysCount": 2,
    "approvedWorkflowsCount": 5,
    "webhookEndpoints": [],
    "usageQuota": {
      "apiCallsUsed": 1200,
      "apiCallsLimit": 10000,
      "resetDate": "ISO-8601"
    }
  }
}
```

### 1.3 Client-Side State Management

- Cache the profile in a client-side state manager (React Context, Zustand, or Redux) for the duration of the session.
- **Refresh triggers:** Profile edit saved, role change detected, manual refresh action, re-authentication.
- **TTL:** Profile cache should be considered stale after 5 minutes. Use stale-while-revalidate pattern.
- **Token rotation:** If using JWTs, implement silent refresh via refresh tokens stored in HTTP-only cookies. Access tokens max TTL: 15 minutes.

### 1.4 Failure Handling

| Scenario | HTTP Code | Client Behaviour |
|----------|-----------|------------------|
| Token expired | 401 | Attempt silent refresh; if failed, redirect to login with toast |
| Token invalid/tampered | 403 | Redirect to login immediately. Log server-side. |
| Profile service unavailable | 503 | Retry with exponential backoff (max 3 attempts) |
| Account suspended | 200 (status: suspended) | Show restricted dashboard with suspension notice |
| Rate limited | 429 | Display rate-limit message. Respect `Retry-After` header. |

---

## 2. Role-Aware Rendering and Data Contract

### 2.1 Rendering Principles

- Use fetched role to conditionally render entire modules, not merely hide with CSS.
- Bundle size: unused modules not loaded (dynamic imports / lazy loading).
- Security: irrelevant data never fetched or transmitted.
- Backend must enforce same role restrictions at API level.

### 2.2 Data Contract by Role

| Role | Visible Modules | Security Posture |
|------|----------------|------------------|
| User | Account Details, Personal Info, Project Status, Account Balance, Delete Account | Minimal data surface. Standard auth. |
| Developer | All User + Developer Hub (API keys, webhooks, usage), Workflow Management, Advanced Project Status | Elevated. Mutations audit-logged. API key ops require re-auth. |
| Admin (future) | All Developer + Global metrics, User management, Feature flags, System health | MFA mandatory. All actions logged. 10-min session timeout. |

### 2.3 Field-Level Access Matrix

| Field / Action | User | Developer | Admin |
|----------------|------|-----------|-------|
| View own profile | ✅ | ✅ | ✅ |
| Edit own profile | ✅ | ✅ | ✅ |
| View own projects | ✅ | ✅ | ✅ |
| Create project | ✅ | ✅ | ✅ |
| View project audit trail | ❌ | ✅ | ✅ |
| Manage API keys | ❌ | ✅ | ✅ |
| Manage workflows | ❌ | ✅ | ✅ |
| View other users' profiles | ❌ | ❌ | ✅ |
| Suspend/modify user accounts | ❌ | ❌ | ✅ |
| Manage feature flags | ❌ | ❌ | ✅ |

### 2.4 Implementation Pattern

```tsx
{user.role === 'developer' && <DeveloperHubSection user={user} />}
{user.role === 'admin' && <AdminPanel user={user} />}

// Permission utility:
import { hasPermission } from '@/utils/permissions';
{hasPermission(user, 'workflows:manage') && <WorkflowManagement />}
```

---

## 3. Required Dashboard Modules (MVP Set)

**Design Principles:**
- Load progressively using skeleton loaders (not spinners)
- Handle empty states with clear messaging and CTA
- Under-two-minute onboarding goal
- All text internationalisation-ready

### 3.1 Welcome and Quick Overview
- Position: top of dashboard, always visible
- Greeting with displayName fallback chain
- Role-aware quick stat cards
- System status badge
- Empty state CTA for new users

### 3.2 Account Details
- View/edit core account information
- Fields: Email, Display Name, Password (change flow), 2FA toggle, Login History
- Optimistic UI updates on save
- Security: password changes require current password; email changes require re-verification

### 3.3 Personal Information
- GDPR-friendly minimal section
- Fields: Full Name, Avatar, Timezone, Locale, Notification Preferences
- Data Export Request button (GDPR Article 15)
- Privacy Policy link

### 3.4 Project Status
- Core value area — paginated project list
- Columns: Project Name, Status badge, Next Gate, Last Updated, Quick Actions
- Empty state with "Create Project" CTA
- Deletion with confirmation (type project name)

### 3.5 Account Balance and Usage
- Current balance in user's currency
- Usage breakdown with progress bars
- Low balance alert at 80% threshold
- Top-up / upgrade links

### 3.6 Developer-Specific Modules
- **API Key Management:** List, create (max 5), revoke, usage stats
- **Workflow Management:** List, create wizard, edit, test/dry-run, soft-delete
- **Developer Quick Links:** Docs, quick-start guide, support/community

### 3.7 Delete Account
- Position: bottom, visually separated "Danger Zone"
- 6-step flow: Information → Acknowledgement → Verification → Confirmation → Grace Period (7 days) → Post-Deletion
- Audit-log all attempts
- GDPR Article 17 / CCPA compliant

---

## 4. Technical and Operational Requirements

### 4.1 Loading and Error States

| State | Implementation |
|-------|---------------|
| Initial page load | Full-page skeleton loader |
| Module-level loading | Per-section skeleton loaders |
| API error (non-auth) | Inline error with "Retry" button |
| API error (auth) | Full-page redirect to login |
| Network offline | Banner: "You appear to be offline" |

### 4.2 Security

| Requirement | Detail |
|-------------|--------|
| Mutation authorisation | JWT must be recent (15 min for sensitive actions), CSRF tokens |
| Rate limiting | Profile: 30/min, Mutations: 10/min, 429 with Retry-After |
| Audit logging | Actor, action, target, timestamp (UTC), IP, user agent |
| CORS policy | Restrict to app domains only, no wildcard in production |
| CSP | Strict headers, no inline scripts, restrict connect-src |
| Input sanitisation | Server-side sanitisation, parameterised queries, XSS prevention |
| Sensitive data | Never return passwords, full API keys, or 2FA secrets |

### 4.3 Accessibility (WCAG 2.1 AA)

- All interactive elements: descriptive ARIA labels
- Full keyboard navigation with logical focus order
- Colour contrast ≥ 4.5:1 (normal), ≥ 3:1 (large text)
- Screen reader compatibility (VoiceOver, NVDA)
- Respect `prefers-reduced-motion` media query
- Touch targets: minimum 44×44px

### 4.4 Analytics and Instrumentation

Track: `dashboard.viewed`, `project.created`, `project.deleted`, `profile.edited`, `account.delete_initiated`, `account.delete_completed`, `apikey.created`, `workflow.created`, `error.displayed`

Privacy: use anonymised user IDs only.

### 4.5 Mobile Responsiveness

| Breakpoint | Layout |
|------------|--------|
| ≥ 1024px | Multi-column grid (2–3 columns) |
| 768px–1023px | Two-column, hamburger nav |
| < 768px | Single-column stacked, bottom/hamburger nav |

### 4.6 Performance Targets

| Metric | Target |
|--------|--------|
| FCP | < 1.5s |
| TTI | < 3.0s |
| LCP | < 2.5s |
| CLS | < 0.1 |
| Profile API p95 | < 300ms |

### 4.7 Rollback and Feature Flagging

- Dashboard behind `VITE_FF_DASHBOARD_V2` feature flag
- Per-user, per-role, per-environment evaluation
- Fallback page on disable
- Previous version maintained for one release cycle

---

## 5. Implementation Reference

### 5.1 Files Created/Modified

| File | Purpose |
|------|---------|
| `client/src/types/user.ts` | UserProfile, UserRole, DeveloperProfile types |
| `client/src/constants/roles.ts` | ROLE_PERMISSIONS, ROLE_LABELS, SESSION_TIMEOUT |
| `client/src/utils/permissions.ts` | hasPermission(), hasAllPermissions(), isAtLeast() |
| `client/src/hooks/useProfile.ts` | Profile fetch with stale-while-revalidate caching |
| `client/src/components/skeletons/DashboardSkeleton.tsx` | Full-page and per-section skeleton loaders |
| `client/src/components/errors/SessionExpired.tsx` | Auth error redirect component |
| `client/src/components/errors/DashboardErrorFallback.tsx` | Error boundary fallback |
| `client/src/components/dashboard/WelcomeHeader.tsx` | Greeting, stats, system status |
| `client/src/components/dashboard/DeveloperHubSection.tsx` | API keys, workflows, quick links |
| `client/src/components/dashboard/AdminPanel.tsx` | Admin-only panel (stub) |
| `client/src/components/dashboard/AccountDetailsModule.tsx` | UPGRADED: ARIA, skeleton, user prop |
| `client/src/components/dashboard/PersonalInfoModule.tsx` | UPGRADED: ARIA, skeleton, GDPR links |
| `client/src/components/dashboard/ProjectStatusModule.tsx` | UPGRADED: empty state CTA, skeleton |
| `client/src/components/dashboard/AccountBalanceModule.tsx` | UPGRADED: skeleton, low-balance alert |
| `client/src/components/dashboard/DeleteAccountModule.tsx` | UPGRADED: 6-step flow, danger zone |
| `client/src/pages/app/DashboardPage.tsx` | REBUILT: role-aware, ErrorBoundary, lazy loading |
| `client/src/config/features.ts` | Added `dashboardV2` feature flag |

### 5.2 Dependencies Added

- `react-error-boundary` ^6.1.1

---

## 6. Private Beta Exit Criteria

| Criterion | Measurement |
|-----------|-------------|
| New user onboarding flow completable without assistance | Usability test ≥ 5 participants, 80% success |
| Skeleton states on all modules (no blank screens) | Manual QA + Lighthouse CLS < 0.1 |
| Role-based rendering correct for User and Developer | Automated integration tests |
| Account deletion 6-step flow completes | End-to-end test |
| WCAG 2.1 AA accessibility checks pass | axe-core audit: zero violations |
| Dashboard functional on mobile (< 768px) | Manual QA on iOS Safari + Android Chrome |
| Profile API < 300ms p95 under beta load | Load test confirmation |
| Feature flag disables dashboard within 60s | Deployment runbook test |

---

## 7. Open Questions and Next Steps

| Item | Owner | Status |
|------|-------|--------|
| Finalise backend profile endpoint schema | Backend | Pending |
| Confirm monetisation model | Product | Pending |
| Design Admin role permission set + MFA | Security/Product | Pending |
| Create work order WO-UX-00X | Project lead | Ready to draft |
| Build React component stubs (ProjectStatusSection) | Frontend | **Completed** |
| Integrate dashboard with footer component | Frontend | Blocked on dashboard shell |
