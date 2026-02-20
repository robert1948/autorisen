<map version="1.0.1">
<!--
    CapeControl Dashboard Architecture - Dynamic & Role-Aware
    Updated: 2026-02-20 (aligned with actual codebase)

    MATURITY LEGEND (used in node TEXT prefixes):
      PROD   = Production - deployed and processing real traffic/payments
      LIVE   = Live - implemented end-to-end, deployed
      PARTIAL = Partial - backend or frontend exists, not fully wired
      STUB   = Stub - UI shell only, no real data
      PLANNED = Planned - design only, no implementation yet
-->
<node TEXT="CapeControl Dashboard Architecture - Dynamic &amp; Role-Aware" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#2196F3" STYLE="rectangle">
<font SIZE="16" BOLD="true"/>

<!-- ===== MATURITY LEGEND ===== -->
<node TEXT="Feature Maturity Legend" POSITION="left" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#455A64" STYLE="rectangle">
<font SIZE="13" BOLD="true"/>
    <node TEXT="[PROD] Production - real traffic/payments" COLOR="#2E7D32">
        <font BOLD="true"/>
        <icon BUILTIN="button_ok"/>
    </node>
    <node TEXT="[LIVE] Live - implemented end-to-end" COLOR="#1565C0">
        <font BOLD="true"/>
        <icon BUILTIN="button_ok"/>
    </node>
    <node TEXT="[PARTIAL] Backend or frontend exists, not fully wired" COLOR="#F57F17">
        <font BOLD="true"/>
        <icon BUILTIN="messagebox_warning"/>
    </node>
    <node TEXT="[STUB] UI shell only, no real data" COLOR="#E65100">
        <font BOLD="true"/>
        <icon BUILTIN="stop-sign"/>
    </node>
    <node TEXT="[PLANNED] Design only, no implementation" COLOR="#9E9E9E">
        <font BOLD="true"/>
        <icon BUILTIN="help"/>
    </node>
</node>

<!-- ===== CROSS-CUTTING: SECURITY ===== -->
<node TEXT="Cross-Cutting: Security Posture [LIVE]" POSITION="left" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#E53935" STYLE="rectangle">
<font SIZE="13" BOLD="true"/>
    <node TEXT="Applies to ALL layers" STYLE="fork">
        <icon BUILTIN="messagebox_warning"/>
    </node>
    <node TEXT="[LIVE] Audit logging for auth events">
        <node TEXT="Login success/failure (AuditLoggingMiddleware)"/>
        <node TEXT="Role escalation attempts"/>
        <node TEXT="Password changes"/>
        <node TEXT="Session invalidations"/>
    </node>
    <node TEXT="[LIVE] Rate limits on auth endpoints">
        <node TEXT="Login: max 5 attempts / 5 min (300s sliding window, 300s block)"/>
        <node TEXT="Auth endpoints: 5 req / min per IP (SlowAPI)"/>
        <node TEXT="Global API: 200 req / min per IP (DDoS middleware)"/>
        <node TEXT="Password reset token: single-use, 30 min TTL"/>
    </node>
    <node TEXT="[LIVE] Input sanitization + CSRF policy">
        <node TEXT="All form inputs sanitized server-side (InputSanitizationMiddleware)"/>
        <node TEXT="CSRF tokens on all POST requests (CSRFMiddleware)"/>
        <node TEXT="Exempt: POST /api/payments/payfast/itn (external callback)"/>
        <node TEXT="XSS protection headers"/>
    </node>
    <node TEXT="[LIVE] Principle of least privilege">
        <node TEXT="JWT contains minimal claims (role, userId)"/>
        <node TEXT="Backend re-validates role via require_roles() dependency"/>
        <node TEXT="No client-side-only role enforcement"/>
    </node>
    <node TEXT="[LIVE] Token security">
        <node TEXT="Short-lived access tokens (15 min)"/>
        <node TEXT="Refresh tokens in httpOnly secure cookies"/>
        <node TEXT="[PLANNED] Token rotation on refresh"/>
    </node>
</node>

<!-- ===== CROSS-CUTTING: OBSERVABILITY ===== -->
<node TEXT="Cross-Cutting: Observability &amp; Quality [PARTIAL]" POSITION="left" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#FF9800" STYLE="rectangle">
<font SIZE="13" BOLD="true"/>
    <node TEXT="Applies to ALL layers" STYLE="fork">
        <icon BUILTIN="messagebox_warning"/>
    </node>
    <node TEXT="Monitoring and error tracking">
        <node TEXT="[LIVE] Frontend: React error boundaries in AppShell"/>
        <node TEXT="[LIVE] Backend: Python logging module"/>
        <node TEXT="[PLANNED] Structured JSON logging"/>
        <node TEXT="[PLANNED] APM integration (latency, error rates)"/>
    </node>
    <node TEXT="Health/status signals">
        <node TEXT="[LIVE] GET /api/health (public, includes DB check)"/>
        <node TEXT="[LIVE] GET /api/version (build info)"/>
        <node TEXT="[LIVE] GET /api/security/stats (security systems status)"/>
        <node TEXT="[PLANNED] GET /api/health/detailed (admin-only)"/>
        <node TEXT="[PLANNED] Dependency checks (cache, external APIs)"/>
    </node>
    <node TEXT="Deployment workflow">
        <node TEXT="[LIVE] Staging (autorisen) vs Production (capecraft) separation"/>
        <node TEXT="[LIVE] Heroku container deploy with retry logic"/>
        <node TEXT="[LIVE] Post-deploy health check verification"/>
        <node TEXT="[PLANNED] Smoke tests post-deploy"/>
        <node TEXT="[PLANNED] Feature flags for gradual rollout"/>
    </node>
    <node TEXT="[PLANNED] Alerting">
        <node TEXT="Auth failure spike detection"/>
        <node TEXT="Latency threshold breaches"/>
        <node TEXT="Error rate thresholds per endpoint"/>
    </node>
</node>

<!-- ===== STEP 1: AUTHENTICATION ===== -->
<node TEXT="1. Authentication &amp; Profile Fetching [PROD]" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#37474F" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>

    <node TEXT="1.1 [LIVE] User submits credentials" FOLDED="false">
        <node TEXT="Email + Password (POST /api/auth/login)"/>
        <node TEXT="[LIVE] Google OAuth (GET /api/auth/oauth/google/start → callback)"/>
        <node TEXT="[LIVE] LinkedIn OAuth (GET /api/auth/oauth/linkedin/start → callback)"/>
        <node TEXT="[LIVE] reCAPTCHA v3 verification (production mode)"/>
        <node TEXT="Frontend validates input format before submission">
            <icon BUILTIN="idea"/>
        </node>
    </node>

    <node TEXT="1.2 [LIVE] Backend validates credentials" FOLDED="false">
        <node TEXT="&#x2705; Success path" COLOR="#2E7D32">
            <node TEXT="Issue JWT access token (Authorization header)"/>
            <node TEXT="Issue refresh token (httpOnly secure cookie)"/>
            <node TEXT="Return CSRF token (csrftoken cookie)"/>
            <node TEXT="Log: auth.login.success"/>
        </node>
        <node TEXT="&#x274C; Failure path" COLOR="#C62828">
            <node TEXT="Invalid credentials">
                <node TEXT="Return 401 + generic message"/>
                <node TEXT="Increment rate limit counter"/>
                <node TEXT="Log: auth.login.failure (no PII in logs)"/>
            </node>
            <node TEXT="Account locked / disabled">
                <node TEXT="Return 403 + account status message"/>
                <node TEXT="Log: auth.login.blocked"/>
            </node>
            <node TEXT="Rate limit exceeded">
                <node TEXT="Return 429 + retry-after header"/>
            </node>
            <node TEXT="Frontend shows contextual error UI">
                <icon BUILTIN="messagebox_warning"/>
            </node>
        </node>
    </node>

    <node TEXT="1.3 [STUB] MFA Check (if enabled)" FOLDED="false" COLOR="#E65100">
        <icon BUILTIN="stop-sign"/>
        <node TEXT="NOTE: Frontend stubs exist (MfaChallengePage, MfaEnrollPage)"/>
        <node TEXT="Simulated only - accepts hardcoded code &apos;123456&apos;"/>
        <node TEXT="No backend TOTP/MFA implementation"/>
        <node TEXT="Routes: /auth/mfa, /account/mfa-enroll"/>
        <node TEXT="[PLANNED] Real TOTP verification"/>
        <node TEXT="[PLANNED] Recovery codes"/>
        <node TEXT="[PLANNED] SMS fallback"/>
    </node>

    <node TEXT="1.4 [LIVE] Fetch profile" FOLDED="false">
        <node TEXT="GET /api/auth/me" STYLE="bubble">
            <font BOLD="true"/>
        </node>
        <node TEXT="&#x2705; Success → MeResponse" COLOR="#2E7D32">
            <node TEXT="Actual response shape (MeResponse)">
                <node TEXT="role: string (Customer | Developer | Admin)"/>
                <node TEXT="profile.id, profile.email, profile.display_name"/>
                <node TEXT="profile.status, profile.created_at, profile.last_login"/>
                <node TEXT="profile.first_name, profile.last_name, profile.company_name"/>
                <node TEXT="profile.email_verified: boolean"/>
                <node TEXT="summary.projects_count, summary.recent_activity[]"/>
                <node TEXT="summary.system_status"/>
            </node>
        </node>
        <node TEXT="&#x274C; Failure → retry with backoff" COLOR="#C62828">
            <node TEXT="Retry up to 3 times (exponential backoff)"/>
            <node TEXT="If still failing → show degraded state UI"/>
            <node TEXT="Allow logout even in degraded state"/>
        </node>
        <node TEXT="Frontend maps MeResponse → UserProfile via mapMeToProfile()">
            <node TEXT="Some fields filled with defaults (avatar, balance, quotas)"/>
            <node TEXT="[PLANNED] Real avatar, balance, usage quota from backend"/>
        </node>
    </node>

    <node TEXT="1.5 [LIVE] Onboarding detection" FOLDED="false">
        <icon BUILTIN="button_ok"/>
        <node TEXT="Full onboarding module implemented (feature-flagged: VITE_FF_ONBOARDING)">
            <node TEXT="Backend: OnboardingSession, OnboardingStep, UserOnboardingStepState models"/>
            <node TEXT="Backend: 12 API endpoints (/api/onboarding/*)"/>
            <node TEXT="Frontend: 8+ page components in pages/onboarding/"/>
            <node TEXT="Routes: /onboarding/*, /app/onboarding/*"/>
        </node>
        <node TEXT="[LIVE] Email verification banner if not verified"/>
        <node TEXT="[LIVE] Restrict certain actions until verified"/>
    </node>

    <node TEXT="1.6 [LIVE] Store auth state (frontend SSOT)" FOLDED="false">
        <node TEXT="React Context (AuthContext) - not Zustand"/>
        <node TEXT="Profile data cached in memory via useProfile() hook"/>
        <node TEXT="Actual AuthState shape:">
            <node TEXT="status: &apos;unknown&apos; | &apos;authenticated&apos; | &apos;unauthenticated&apos;"/>
            <node TEXT="accessToken: string | null"/>
            <node TEXT="refreshToken: string | null"/>
            <node TEXT="expiresAt: string | null"/>
            <node TEXT="userEmail: string | null"/>
            <node TEXT="isEmailVerified: boolean"/>
            <node TEXT="user: AuthUser | null"/>
        </node>
        <node TEXT="Separate loading and error booleans (not in status enum)"/>
    </node>

    <node TEXT="1.7 [LIVE] Registration flow" FOLDED="false">
        <node TEXT="Two-step registration: POST /api/auth/register/step1 → step2"/>
        <node TEXT="Single-step: POST /api/auth/register"/>
        <node TEXT="[LIVE] Developer self-registration: POST /api/auth/register/developer"/>
        <node TEXT="[LIVE] Admin invite-only registration: POST /api/admin/register"/>
        <node TEXT="[LIVE] Email verification: GET /api/auth/verify?token=..."/>
        <node TEXT="[LIVE] Resend verification: POST /api/auth/verify/resend"/>
    </node>

</node>

<!-- ===== STEP 2: ROLE RESOLUTION & ROUTING ===== -->
<node TEXT="2. Role Resolution &amp; Routing [LIVE]" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#37474F" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>

    <node TEXT="2.1 Role determines navigation &amp; modules" FOLDED="false">

        <node TEXT="Role definition" COLOR="#455A64">
            <font BOLD="true"/>
            <node TEXT="Backend enum (UserRole): Customer | Developer | Admin"/>
            <node TEXT="Frontend type: &apos;user&apos; | &apos;developer&apos; | &apos;admin&apos; (lowercase)"/>
            <node TEXT="Normalization: AuthContext .toLowerCase() on backend role"/>
            <node TEXT="NOTE: Backend &apos;Customer&apos; maps to frontend &apos;user&apos;"/>
        </node>

        <node TEXT="[LIVE] Customer (user) role" COLOR="#1565C0">
            <font BOLD="true"/>
            <node TEXT="Permissions: profile:read, profile:edit, projects:read, projects:create, account:billing, account:delete"/>
            <node TEXT="Dashboard modules: WelcomeHeader, QuickActions, UsageProgress, ActivityFeed, AccountDetails, PersonalInfo, ProjectStatus"/>
            <node TEXT="Actual routes: /app/dashboard, /app/settings, /app/marketplace, /app/pricing, /app/billing"/>
        </node>

        <node TEXT="[PARTIAL] Developer role" COLOR="#6A1B9A">
            <font BOLD="true"/>
            <node TEXT="Additional permissions: projects:audit, apikeys:manage, workflows:manage"/>
            <node TEXT="Inherits all Customer permissions"/>
            <node TEXT="[PARTIAL] DeveloperHubSection on dashboard (UI shell, API calls are TODO)"/>
            <node TEXT="[PARTIAL] DeveloperPage at /app/developer (feature-flagged: agentsShell)"/>
            <node TEXT="Actual routes: + /app/developer"/>
        </node>

        <node TEXT="[PARTIAL] Admin role" COLOR="#C62828">
            <font BOLD="true"/>
            <node TEXT="Permissions: * (wildcard)"/>
            <node TEXT="Inherits Developer + Customer access"/>
            <node TEXT="[STUB] AdminPanel component (&apos;Full admin panel coming soon&apos;)"/>
            <node TEXT="[LIVE] Backend: invite management endpoints (POST/GET/DELETE /api/admin/invite*)"/>
            <node TEXT="No dedicated /admin/* frontend routes yet"/>
        </node>

        <node TEXT="unknown / unrecognized role (FALLBACK)" COLOR="#E65100">
            <font BOLD="true"/>
            <icon BUILTIN="messagebox_warning"/>
            <node TEXT="Default to minimal Customer permissions"/>
            <node TEXT="Show banner: &apos;Contact support if features are missing&apos;"/>
        </node>

    </node>

    <node TEXT="2.2 [LIVE] Route guards &amp; navigation" FOLDED="false">
        <node TEXT="ProtectedRoute wrapper (redirects unauthenticated → /auth/login)"/>
        <node TEXT="Permission checks via hasPermission(user, permission) inline"/>
        <node TEXT="Backend re-validates role via require_roles() on every API call">
            <icon BUILTIN="messagebox_warning"/>
        </node>
        <node TEXT="AppShell sidebar navigation:">
            <node TEXT="Always: Dashboard, Projects, Marketplace, Settings"/>
            <node TEXT="Feature-flagged: Agents, Chat (VITE_FF_AGENTS_SHELL)"/>
            <node TEXT="Feature-flagged: Pricing, Billing (VITE_FF_PAYMENTS)"/>
        </node>
    </node>

</node>

<!-- ===== STEP 3: ROLE-SCOPED DATA FETCHING ===== -->
<node TEXT="3. Role-Scoped Data Fetching [PARTIAL]" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#37474F" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>

    <node TEXT="3.1 Fetch only what the role needs" FOLDED="false">
        <node TEXT="Principle: minimal data transfer per role"/>

        <node TEXT="[LIVE] Customer data set" COLOR="#1565C0">
            <node TEXT="GET /api/auth/me → profile, summary, projects_count"/>
            <node TEXT="GET /api/payments/subscription → plan, status (if payments enabled)"/>
            <node TEXT="GET /api/payments/plans → available plans"/>
            <node TEXT="GET /api/payments/invoices → billing history"/>
        </node>

        <node TEXT="[PARTIAL] Developer data set" COLOR="#6A1B9A">
            <node TEXT="[LIVE] GET /api/dev/api-keys → active keys (from api_credentials table)"/>
            <node TEXT="[LIVE] GET /api/dev/profile → developer profile (organization, use-case)"/>
            <node TEXT="[LIVE] PATCH /api/dev/profile → update developer profile"/>
            <node TEXT="[LIVE] GET /api/dev/usage → API call counts, quotas"/>
            <node TEXT="[LIVE] POST /api/dev/api-keys → provision new API credential (show-once secret)"/>
            <node TEXT="[LIVE] DELETE /api/dev/api-keys/{id} → revoke API credential"/>
            <node TEXT="NOTE: Backend endpoints exist but dashboard DeveloperHubSection does not call them yet"/>
        </node>

        <node TEXT="[PARTIAL] Admin data set" COLOR="#C62828">
            <node TEXT="[LIVE] GET /api/admin/invites → list admin invites (pending, used, revoked)"/>
            <node TEXT="[LIVE] POST /api/admin/invite → create admin invite (generates token, sends email)"/>
            <node TEXT="[LIVE] DELETE /api/admin/invite/{id} → revoke pending invite"/>
            <node TEXT="[PLANNED] GET /api/admin/users → user list (paginated, searchable)"/>
            <node TEXT="[PLANNED] GET /api/admin/audits → audit log (filterable)"/>
            <node TEXT="[PLANNED] GET /api/admin/system → health, metrics, config"/>
        </node>
    </node>

    <node TEXT="3.2 [LIVE] Loading &amp; error states" FOLDED="false">
        <node TEXT="Skeleton loaders during fetch (Tailwind animate-pulse)"/>
        <node TEXT="Error state per dashboard module (not global crash)">
            <node TEXT="Retry button per failed module"/>
            <node TEXT="Partial dashboard render (working modules still show)"/>
        </node>
        <node TEXT="Empty states with helpful CTAs"/>
    </node>

    <node TEXT="3.3 [PLANNED] Caching &amp; freshness" FOLDED="false">
        <icon BUILTIN="help"/>
        <node TEXT="Currently: useEffect + useState (manual fetch)"/>
        <node TEXT="[PLANNED] Migrate to React Query / SWR"/>
        <node TEXT="[PLANNED] Cache invalidation on user actions"/>
        <node TEXT="[PLANNED] Background refresh intervals per data criticality"/>
    </node>

</node>

<!-- ===== STEP 4: ACCOUNT MANAGEMENT ===== -->
<node TEXT="4. Account Management [LIVE]" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#37474F" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>

    <node TEXT="4.1 [LIVE] Profile view / edit" FOLDED="false">
        <node TEXT="PersonalInfoModule on dashboard"/>
        <node TEXT="Editable: displayName, first_name, last_name"/>
        <node TEXT="Read-only: userId, email (change requires verification), role"/>
        <node TEXT="[PLANNED] Avatar upload"/>
    </node>

    <node TEXT="4.2 [LIVE] Password management" FOLDED="false">
        <node TEXT="[LIVE] Forgot password: POST /api/auth/password/forgot → email flow"/>
        <node TEXT="[LIVE] Reset password: POST /api/auth/password/reset (token-based)"/>
        <node TEXT="[LIVE] Also: POST /api/auth/password-reset/request → /confirm (legacy endpoints)"/>
        <node TEXT="Time-limited reset token (30 min), single-use"/>
        <node TEXT="Password strength validation (client + server)"/>
    </node>

    <node TEXT="4.3 Session management" FOLDED="false">
        <node TEXT="[LIVE] Logout current session: POST /api/auth/logout"/>
        <node TEXT="[LIVE] Token refresh: POST /api/auth/refresh (httpOnly cookie)"/>
        <node TEXT="[LIVE] Token refresh cycle" COLOR="#E65100">
            <font BOLD="true"/>
            <icon BUILTIN="revision"/>
            <node TEXT="Access token expires → auto-refresh via refresh token cookie"/>
            <node TEXT="401 interceptor retries with refreshed token"/>
            <node TEXT="Refresh failure → clear auth state + redirect to /auth/login"/>
            <node TEXT="Feeds back into Step 1 (re-authentication)"/>
        </node>
        <node TEXT="[PLANNED] View active sessions (device, IP, last active)"/>
        <node TEXT="[PLANNED] Logout all sessions (panic button)"/>
    </node>

    <node TEXT="4.4 [STUB] MFA management" FOLDED="false" COLOR="#E65100">
        <icon BUILTIN="stop-sign"/>
        <node TEXT="Frontend stubs: MfaEnrollPage, MfaChallengePage"/>
        <node TEXT="No backend TOTP implementation"/>
        <node TEXT="[PLANNED] Enable / disable MFA"/>
        <node TEXT="[PLANNED] Recovery codes"/>
    </node>

    <node TEXT="4.5 [PLANNED] Notification preferences" FOLDED="false" COLOR="#9E9E9E">
        <icon BUILTIN="help"/>
        <node TEXT="Email notification toggles"/>
        <node TEXT="In-app notification settings"/>
    </node>

    <node TEXT="4.6 [PARTIAL] Developer credential management (Developer role)" FOLDED="false" COLOR="#6A1B9A">
        <font BOLD="true"/>
        <node TEXT="[LIVE] Backend: full CRUD for API credentials">
            <node TEXT="POST /api/dev/api-keys → provision (client_id + client_secret, show-once)"/>
            <node TEXT="GET /api/dev/api-keys → list active credentials"/>
            <node TEXT="DELETE /api/dev/api-keys/{id} → revoke (sets revoked_at, is_active=false)"/>
            <node TEXT="client_secret_hash stored in api_credentials table"/>
        </node>
        <node TEXT="[STUB] Frontend: DeveloperHubSection shows empty state with TODO comments"/>
    </node>

    <node TEXT="4.7 [PARTIAL] Admin invite management (Admin role)" FOLDED="false" COLOR="#C62828">
        <font BOLD="true"/>
        <node TEXT="[LIVE] Backend endpoints:">
            <node TEXT="POST /api/admin/invite → generates signed invite token"/>
            <node TEXT="GET /api/admin/invites → list all (pending, used, expired, revoked)"/>
            <node TEXT="DELETE /api/admin/invite/{id} → revoke pending invite"/>
            <node TEXT="POST /api/admin/register → accept invite + create admin account"/>
        </node>
        <node TEXT="[STUB] Frontend: AdminPanel shows &apos;coming soon&apos; placeholder"/>
    </node>

    <node TEXT="4.8 [LIVE] Account deletion" FOLDED="false">
        <node TEXT="DeleteAccountModule on dashboard"/>
        <node TEXT="Permission-gated: account:delete"/>
    </node>

</node>

<!-- ===== STEP 5: SESSION LIFECYCLE (FEEDBACK LOOP) ===== -->
<node TEXT="5. Session Lifecycle &amp; Re-auth Loop [LIVE]" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#00695C" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>
    <icon BUILTIN="revision"/>

    <node TEXT="5.1 [PLANNED] Active session monitoring" FOLDED="false">
        <node TEXT="[PLANNED] Periodic token validity check (silent)"/>
        <node TEXT="[PLANNED] Detect token expiry before API call fails"/>
    </node>

    <node TEXT="5.2 [LIVE] Auto-refresh flow" FOLDED="false">
        <node TEXT="Intercept 401 responses globally (authApi interceptor)"/>
        <node TEXT="POST /api/auth/refresh with httpOnly cookie"/>
        <node TEXT="Retry original request on success"/>
        <node TEXT="Redirect to /auth/login on refresh failure"/>
    </node>

    <node TEXT="5.3 [PLANNED] Forced re-authentication triggers" FOLDED="false">
        <node TEXT="Role change detected (admin action)"/>
        <node TEXT="Password changed from another session"/>
        <node TEXT="Security event (suspicious activity)"/>
        <node TEXT="Account disabled by admin"/>
    </node>

    <node TEXT="5.4 [LIVE] Graceful logout" FOLDED="false">
        <node TEXT="Clear tokens (access token from state, refresh cookie server-side)"/>
        <node TEXT="Clear cached profile/data from React state"/>
        <node TEXT="POST /api/auth/logout (invalidate server-side)"/>
        <node TEXT="Redirect to /auth/login"/>
    </node>

</node>

<!-- ===== STEP 6: PAYMENTS & BILLING ===== -->
<node TEXT="6. Payments &amp; Billing [PROD]" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#1B5E20" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>
    <icon BUILTIN="button_ok"/>

    <node TEXT="6.1 [PROD] PayFast integration" FOLDED="false">
        <node TEXT="Merchant ID: 12085234 (production)"/>
        <node TEXT="Signature generation: URL-encoded, insertion-order fields"/>
        <node TEXT="Field sanitization: em-dash → hyphen, special chars stripped"/>
    </node>

    <node TEXT="6.2 [LIVE] Subscription plans" FOLDED="false">
        <node TEXT="GET /api/payments/plans → available plans">
            <node TEXT="Free (starter) - R0"/>
            <node TEXT="Pro Monthly - R529"/>
            <node TEXT="Pro Yearly - R4,990"/>
            <node TEXT="Enterprise Monthly - R1,799"/>
            <node TEXT="Enterprise Yearly - R17,190"/>
        </node>
        <node TEXT="GET /api/payments/subscription → current subscription status"/>
        <node TEXT="POST /api/payments/subscription → create/change subscription"/>
        <node TEXT="POST /api/payments/subscription/cancel → cancel"/>
    </node>

    <node TEXT="6.3 [PROD] Checkout flow" FOLDED="false">
        <node TEXT="PricingPage → CheckoutPage → PayFast redirect">
            <node TEXT="Frontend: /app/pricing, /app/checkout"/>
            <node TEXT="CSRF token fetched before subscription POST"/>
            <node TEXT="Auto-checkout waits for authLoading to complete"/>
            <node TEXT="Hidden form POST to PayFast process_url"/>
        </node>
        <node TEXT="POST /api/payments/payfast/checkout → build checkout fields"/>
        <node TEXT="Dark-themed checkout UI with BEM CSS classes"/>
        <node TEXT="Step components: ReviewStep, ProcessingStep, SuccessStep, ErrorStep"/>
    </node>

    <node TEXT="6.4 [LIVE] ITN (Instant Transaction Notification)" FOLDED="false">
        <node TEXT="POST /api/payments/payfast/itn (CSRF-exempt, public)"/>
        <node TEXT="Signature verification: preserves PayFast field order"/>
        <node TEXT="Server-to-server validation with PayFast"/>
        <node TEXT="Updates invoice status (pending → paid)"/>
        <node TEXT="[LIVE] Debug logging on ITN payload and failures"/>
    </node>

    <node TEXT="6.5 [LIVE] Invoices" FOLDED="false">
        <node TEXT="GET /api/payments/invoices → billing history"/>
        <node TEXT="Invoice model: amount, status (pending/paid/cancelled), payment_ref"/>
        <node TEXT="[STUB] BillingPage shows hardcoded placeholder data"/>
    </node>

    <node TEXT="6.6 First real payment processed" FOLDED="false" COLOR="#2E7D32">
        <font BOLD="true"/>
        <icon BUILTIN="button_ok"/>
        <node TEXT="R529 CapeControl Pro Monthly (ref 282159911)"/>
        <node TEXT="PayFast confirmation email received"/>
    </node>

</node>

<!-- ===== STEP 7: MARKETPLACE ===== -->
<node TEXT="7. Marketplace [PARTIAL]" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#4A148C" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>

    <node TEXT="7.1 [LIVE] Backend API" FOLDED="false">
        <node TEXT="GET /api/marketplace/agents → browse agents"/>
        <node TEXT="GET /api/marketplace/agents/{slug} → agent detail"/>
        <node TEXT="GET /api/marketplace/search → search agents"/>
        <node TEXT="GET /api/marketplace/categories → agent categories"/>
        <node TEXT="GET /api/marketplace/trending → trending agents"/>
        <node TEXT="GET /api/marketplace/featured → featured agents"/>
        <node TEXT="POST /api/marketplace/agents/publish → publish agent"/>
        <node TEXT="POST /api/marketplace/agents/validate → validate before publish"/>
        <node TEXT="POST /api/marketplace/agents/{id}/install → install agent"/>
        <node TEXT="GET /api/marketplace/analytics → marketplace analytics"/>
    </node>

    <node TEXT="7.2 [PARTIAL] Frontend" FOLDED="false">
        <node TEXT="MarketplacePage at /app/marketplace"/>
        <node TEXT="[STUB] Stats show hardcoded values (&apos;25+ agents&apos;, &apos;1.2k deployments&apos;)"/>
        <node TEXT="[PLANNED] Wire to real counts from /api/marketplace/analytics"/>
    </node>

</node>

<!-- ===== STEP 8: DASHBOARD MODULES ===== -->
<node TEXT="8. Dashboard Page Modules [LIVE]" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#0D47A1" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>

    <node TEXT="DashboardPage.tsx (203 lines)" FOLDED="false">
        <node TEXT="Role-aware conditional rendering"/>
        <node TEXT="Skeleton loading states"/>
        <node TEXT="Error boundaries"/>
    </node>

    <node TEXT="[LIVE] Core modules (all roles)" FOLDED="false" COLOR="#1565C0">
        <node TEXT="WelcomeHeader - greeting with user name"/>
        <node TEXT="QuickActionsCard - action shortcuts"/>
        <node TEXT="UsageProgressCard - usage metrics"/>
        <node TEXT="ActivityFeedCard - recent activity"/>
        <node TEXT="AccountDetailsModule - account info"/>
        <node TEXT="PersonalInfoModule - editable profile"/>
        <node TEXT="ProjectStatusModule - project overview"/>
    </node>

    <node TEXT="[LIVE] Billing module (permission-gated)" FOLDED="false" COLOR="#2E7D32">
        <node TEXT="AccountBalanceModule - requires account:billing permission"/>
    </node>

    <node TEXT="[LIVE] Account management" FOLDED="false" COLOR="#E65100">
        <node TEXT="DeleteAccountModule - with confirmation dialog"/>
    </node>

    <node TEXT="[STUB] Developer section" FOLDED="false" COLOR="#6A1B9A">
        <icon BUILTIN="stop-sign"/>
        <node TEXT="DeveloperHubSection - UI shell with TODO comments"/>
        <node TEXT="Always renders empty state"/>
        <node TEXT="Comment: &apos;// TODO: Connect to real endpoint: GET /api/v1/developer/api-keys&apos;"/>
    </node>

    <node TEXT="[STUB] Admin section" FOLDED="false" COLOR="#C62828">
        <icon BUILTIN="stop-sign"/>
        <node TEXT="AdminPanel - &apos;Full admin panel coming soon&apos;"/>
        <node TEXT="Hardcoded dash values"/>
        <node TEXT="Gated: hasPermission(user, &apos;admin:users&apos;)"/>
    </node>

</node>

</node>
</map>
