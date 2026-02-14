<map version="1.0.1">
<!--
    Improved Dashboard Content Requirements - Dynamic & Role-Aware
    With error handling, feedback loops, and cross-cutting concerns
-->
<node TEXT="Dashboard Content Requirements – Dynamic &amp; Role-Aware" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#2196F3" STYLE="rectangle">
<font SIZE="16" BOLD="true"/>

<!-- ===== CROSS-CUTTING: SECURITY ===== -->
<node TEXT="Cross-Cutting: Security Posture" POSITION="left" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#E53935" STYLE="rectangle">
<font SIZE="13" BOLD="true"/>
    <node TEXT="Applies to ALL layers" STYLE="fork">
        <icon BUILTIN="messagebox_warning"/>
    </node>
    <node TEXT="Audit logging for auth events">
        <node TEXT="Login success/failure"/>
        <node TEXT="Role escalation attempts"/>
        <node TEXT="Password changes"/>
        <node TEXT="Session invalidations"/>
    </node>
    <node TEXT="Rate limits on auth endpoints">
        <node TEXT="Login: max 5 attempts / 15 min"/>
        <node TEXT="Profile fetch: max 60 req / min"/>
        <node TEXT="Password reset: max 3 / hour"/>
    </node>
    <node TEXT="Input sanitization + CSRF policy">
        <node TEXT="All form inputs sanitized server-side"/>
        <node TEXT="CSRF tokens on state-changing requests"/>
        <node TEXT="XSS protection headers"/>
    </node>
    <node TEXT="Principle of least privilege">
        <node TEXT="JWT contains minimal claims (role, userId)"/>
        <node TEXT="Backend re-validates role on every protected endpoint"/>
        <node TEXT="No client-side-only role enforcement"/>
    </node>
    <node TEXT="Token security">
        <node TEXT="Short-lived access tokens (15 min)"/>
        <node TEXT="Refresh tokens in httpOnly secure cookies"/>
        <node TEXT="Token rotation on refresh"/>
    </node>
</node>

<!-- ===== CROSS-CUTTING: OBSERVABILITY ===== -->
<node TEXT="Cross-Cutting: Observability &amp; Quality" POSITION="left" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#FF9800" STYLE="rectangle">
<font SIZE="13" BOLD="true"/>
    <node TEXT="Applies to ALL layers" STYLE="fork">
        <icon BUILTIN="messagebox_warning"/>
    </node>
    <node TEXT="Monitoring and error tracking">
        <node TEXT="Frontend: error boundary reporting"/>
        <node TEXT="Backend: structured logging (JSON)"/>
        <node TEXT="APM integration (latency, error rates)"/>
    </node>
    <node TEXT="Health/status signals">
        <node TEXT="GET /api/health (public)"/>
        <node TEXT="GET /api/health/detailed (admin-only)"/>
        <node TEXT="Dependency checks (DB, cache, external APIs)"/>
    </node>
    <node TEXT="Deployment gates">
        <node TEXT="Staging only unless explicitly approved"/>
        <node TEXT="Smoke tests post-deploy"/>
        <node TEXT="Feature flags for gradual rollout"/>
    </node>
    <node TEXT="Alerting">
        <node TEXT="Auth failure spike detection"/>
        <node TEXT="Latency threshold breaches"/>
        <node TEXT="Error rate thresholds per endpoint"/>
    </node>
</node>

<!-- ===== STEP 1: AUTHENTICATION ===== -->
<node TEXT="1. Authentication &amp; Profile Fetching" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#37474F" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>

    <node TEXT="1.1 User submits credentials" FOLDED="false">
        <node TEXT="Email + Password"/>
        <node TEXT="SSO / OAuth provider"/>
        <node TEXT="Frontend validates input format before submission">
            <icon BUILTIN="idea"/>
        </node>
    </node>

    <node TEXT="1.2 Backend validates credentials" FOLDED="false">
        <node TEXT="&#x2705; Success path" COLOR="#2E7D32">
            <node TEXT="Issue JWT access token"/>
            <node TEXT="Issue refresh token (httpOnly cookie)"/>
            <node TEXT="Log: auth.login.success"/>
            <node TEXT="Proceed to 1.3 MFA Check"/>
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
                <node TEXT="Alert: auth.ratelimit.triggered"/>
            </node>
            <node TEXT="Frontend shows contextual error UI">
                <icon BUILTIN="messagebox_warning"/>
            </node>
        </node>
    </node>

    <node TEXT="1.3 MFA Check (if enabled)" FOLDED="false">
        <node TEXT="MFA not enabled → skip to 1.4"/>
        <node TEXT="MFA enabled">
            <node TEXT="Prompt for TOTP / SMS code"/>
            <node TEXT="&#x2705; Valid → proceed to 1.4"/>
            <node TEXT="&#x274C; Invalid → return to MFA prompt (max 3 attempts)"/>
            <node TEXT="&#x274C; Exceeded attempts → lock + notify"/>
        </node>
    </node>

    <node TEXT="1.4 Fetch profile" FOLDED="false">
        <node TEXT="GET /api/auth/me" STYLE="bubble">
            <font BOLD="true"/>
        </node>
        <node TEXT="Rate-limited endpoint (protects abuse)"/>
        <node TEXT="&#x2705; Success → parse response" COLOR="#2E7D32">
            <node TEXT="Required fields in response">
                <node TEXT="userId (unique, immutable)"/>
                <node TEXT="email (verified flag)"/>
                <node TEXT="role enum: Customer | Developer | Admin"/>
                <node TEXT="name / displayName"/>
                <node TEXT="createdAt"/>
                <node TEXT="lastLogin"/>
                <node TEXT="mfaEnabled (boolean)"/>
                <node TEXT="emailVerified (boolean)"/>
            </node>
        </node>
        <node TEXT="&#x274C; Failure → retry with backoff" COLOR="#C62828">
            <node TEXT="Retry up to 3 times (exponential backoff)"/>
            <node TEXT="If still failing → show degraded state UI"/>
            <node TEXT="Log: profile.fetch.failure"/>
            <node TEXT="Allow logout even in degraded state"/>
        </node>
    </node>

    <node TEXT="1.5 First-login / onboarding detection" FOLDED="false">
        <icon BUILTIN="idea"/>
        <node TEXT="If createdAt ≈ lastLogin (first session)">
            <node TEXT="Redirect to onboarding flow"/>
            <node TEXT="Set profile defaults"/>
            <node TEXT="Welcome notification"/>
        </node>
        <node TEXT="If email not verified">
            <node TEXT="Show verification banner"/>
            <node TEXT="Restrict certain actions until verified"/>
        </node>
    </node>

    <node TEXT="1.6 Store auth state (frontend SSOT)" FOLDED="false">
        <node TEXT="Auth context / store (React Context, Zustand, etc.)"/>
        <node TEXT="Profile data cached in memory (not localStorage for tokens)"/>
        <node TEXT="Auth state: authenticated | unauthenticated | loading | error"/>
    </node>

</node>

<!-- ===== STEP 2: ROLE RESOLUTION & ROUTING ===== -->
<node TEXT="2. Role Resolution &amp; Routing" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#37474F" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>

    <node TEXT="2.1 Role determines navigation &amp; modules" FOLDED="false">

        <node TEXT="Customer role" COLOR="#1565C0">
            <font BOLD="true"/>
            <node TEXT="Show user dashboard modules"/>
            <node TEXT="Hide developer/admin-only tools"/>
            <node TEXT="Accessible routes: /dashboard, /profile, /agents, /billing"/>
        </node>

        <node TEXT="Developer role" COLOR="#6A1B9A">
            <font BOLD="true"/>
            <node TEXT="Show developer console/modules"/>
            <node TEXT="Access dev-only endpoints (scoped by API key)"/>
            <node TEXT="Manage API credentials (client_id / client_secret pairs)"/>
            <node TEXT="View developer profile (organization, use-case, terms)"/>
            <node TEXT="Inherits Customer-level access"/>
            <node TEXT="Accessible routes: + /dev/console, /dev/api-keys, /dev/logs, /dev/profile"/>
        </node>

        <node TEXT="Admin role" COLOR="#C62828">
            <font BOLD="true"/>
            <node TEXT="Show admin controls (users, audits, system)"/>
            <node TEXT="Manage admin invites (create, list, revoke)"/>
            <node TEXT="Strong gating + additional logging on all actions"/>
            <node TEXT="Inherits Developer + Customer access"/>
            <node TEXT="Accessible routes: + /admin/users, /admin/audits, /admin/system, /admin/invites"/>
        </node>

        <node TEXT="unknown / unrecognized role (FALLBACK)" COLOR="#E65100">
            <font BOLD="true"/>
            <icon BUILTIN="messagebox_warning"/>
            <node TEXT="Default to minimal Customer permissions"/>
            <node TEXT="Log: role.unknown.detected (alert)"/>
            <node TEXT="Show banner: &apos;Contact support if features are missing&apos;"/>
        </node>

    </node>

    <node TEXT="2.2 Route guards" FOLDED="false">
        <node TEXT="RequireAuth wrapper (redirects unauthenticated → /login)"/>
        <node TEXT="RequireRole(role) wrapper (403 page if insufficient)"/>
        <node TEXT="Backend re-validates role on every API call (never trust client)">
            <icon BUILTIN="messagebox_warning"/>
        </node>
        <node TEXT="Redirect logic after login (return to intended URL)"/>
    </node>

</node>

<!-- ===== STEP 3: ROLE-SCOPED DATA FETCHING ===== -->
<node TEXT="3. Role-Scoped Data Fetching" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#37474F" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>

    <node TEXT="3.1 Fetch only what the role needs" FOLDED="false">
        <node TEXT="Principle: minimal data transfer per role"/>

        <node TEXT="Customer data set" COLOR="#1565C0">
            <node TEXT="GET /api/user/subscription → plan, status, renewal"/>
            <node TEXT="GET /api/user/agents → agent list, statuses"/>
            <node TEXT="GET /api/user/activity → recent actions (paginated)"/>
        </node>

        <node TEXT="Developer data set" COLOR="#6A1B9A">
            <node TEXT="GET /api/dev/api-keys → active keys, scopes (from api_credentials table)"/>
            <node TEXT="GET /api/dev/profile → developer profile (organization, use-case, terms)"/>
            <node TEXT="GET /api/dev/usage → API call counts, quotas"/>
            <node TEXT="GET /api/dev/logs → recent logs (filterable)"/>
            <node TEXT="GET /api/dev/sandbox → test environment status"/>
            <node TEXT="POST /api/dev/api-keys → provision new API credential (show-once secret)"/>
            <node TEXT="DELETE /api/dev/api-keys/{id} → revoke API credential"/>
        </node>

        <node TEXT="Admin data set" COLOR="#C62828">
            <node TEXT="GET /api/admin/users → user list (paginated, searchable)"/>
            <node TEXT="GET /api/admin/audits → audit log (filterable)"/>
            <node TEXT="GET /api/admin/system → health, metrics, config"/>
            <node TEXT="GET /api/admin/invites → list admin invites (pending, used, revoked)"/>
            <node TEXT="POST /api/admin/invite → create admin invite (generates token, sends email)"/>
            <node TEXT="DELETE /api/admin/invite/{id} → revoke pending invite"/>
        </node>
    </node>

    <node TEXT="3.2 Loading &amp; error states" FOLDED="false">
        <node TEXT="Skeleton loaders during fetch (no blank screens)"/>
        <node TEXT="Error state per module (not global crash)">
            <node TEXT="Retry button per failed module"/>
            <node TEXT="Partial dashboard render (working modules still show)"/>
        </node>
        <node TEXT="Empty states with helpful CTAs"/>
    </node>

    <node TEXT="3.3 Caching &amp; freshness" FOLDED="false">
        <icon BUILTIN="idea"/>
        <node TEXT="SWR / React Query with stale-while-revalidate"/>
        <node TEXT="Cache invalidation on user actions"/>
        <node TEXT="Background refresh intervals per data criticality"/>
    </node>

</node>

<!-- ===== STEP 4: ACCOUNT MANAGEMENT ===== -->
<node TEXT="4. Account Management (Authenticated Context)" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#37474F" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>

    <node TEXT="4.1 Profile view / edit" FOLDED="false">
        <node TEXT="Editable: displayName, avatar, preferences"/>
        <node TEXT="Read-only: userId, email (change requires verification), role"/>
        <node TEXT="Optimistic UI update + server confirmation"/>
    </node>

    <node TEXT="4.2 Password management" FOLDED="false">
        <node TEXT="Change password (requires current password)"/>
        <node TEXT="Reset password (email-based flow)">
            <node TEXT="Time-limited reset token (30 min)"/>
            <node TEXT="Single-use token"/>
        </node>
        <node TEXT="Password strength validation (client + server)"/>
    </node>

    <node TEXT="4.3 Session management" FOLDED="false">
        <node TEXT="View active sessions (device, IP, last active)"/>
        <node TEXT="Logout current session"/>
        <node TEXT="Logout all sessions (panic button)"/>
        <node TEXT="Token refresh cycle" COLOR="#E65100">
            <font BOLD="true"/>
            <icon BUILTIN="revision"/>
            <node TEXT="Access token expires → auto-refresh via refresh token"/>
            <node TEXT="Refresh token expires → redirect to login"/>
            <node TEXT="Refresh failure → clear auth state + redirect"/>
            <node TEXT="Feeds back into Step 1 (re-authentication)"/>
        </node>
    </node>

    <node TEXT="4.4 MFA management" FOLDED="false">
        <icon BUILTIN="idea"/>
        <node TEXT="Enable / disable MFA"/>
        <node TEXT="View recovery codes"/>
        <node TEXT="Regenerate recovery codes"/>
    </node>

    <node TEXT="4.5 Notification preferences" FOLDED="false">
        <icon BUILTIN="idea"/>
        <node TEXT="Email notification toggles"/>
        <node TEXT="In-app notification settings"/>
    </node>

    <node TEXT="4.6 Developer credential management (Developer role)" FOLDED="false" COLOR="#6A1B9A">
        <font BOLD="true"/>
        <node TEXT="View active API credentials (client_id, label, created_at)"/>
        <node TEXT="Provision new API key pair (client_id + client_secret)">
            <node TEXT="client_secret shown once at creation (show-once pattern)"/>
            <node TEXT="client_secret_hash stored in api_credentials table"/>
            <node TEXT="Requires email verification before provisioning"/>
        </node>
        <node TEXT="Revoke API credential (sets revoked_at, is_active = false)"/>
        <node TEXT="Label / rename credentials"/>
        <node TEXT="Developer profile view (organization, use-case, GitHub URL)"/>
    </node>

    <node TEXT="4.7 Admin invite management (Admin role)" FOLDED="false" COLOR="#C62828">
        <font BOLD="true"/>
        <node TEXT="Create admin invite (target_email, expiry_hours)">
            <node TEXT="POST /api/admin/invite → generates signed invite token"/>
            <node TEXT="Token stored hashed in admin_invites table"/>
            <node TEXT="Invite email sent with one-time registration URL"/>
        </node>
        <node TEXT="List all invites (pending, used, expired, revoked)"/>
        <node TEXT="Revoke pending invite (DELETE /api/admin/invite/{id})"/>
        <node TEXT="View invite audit trail (invited_by, used_by, timestamps)"/>
    </node>

</node>

<!-- ===== STEP 5: SESSION LIFECYCLE (FEEDBACK LOOP) ===== -->
<node TEXT="5. Session Lifecycle &amp; Re-auth Loop" POSITION="right" FOLDED="false" COLOR="#ffffff" BACKGROUND_COLOR="#00695C" STYLE="rectangle">
<font SIZE="14" BOLD="true"/>
    <icon BUILTIN="revision"/>

    <node TEXT="5.1 Active session monitoring" FOLDED="false">
        <node TEXT="Periodic token validity check (silent)"/>
        <node TEXT="Detect token expiry before API call fails"/>
    </node>

    <node TEXT="5.2 Auto-refresh flow" FOLDED="false">
        <node TEXT="Intercept 401 responses globally"/>
        <node TEXT="Attempt token refresh"/>
        <node TEXT="Retry original request on success"/>
        <node TEXT="Redirect to login on refresh failure"/>
    </node>

    <node TEXT="5.3 Forced re-authentication triggers" FOLDED="false">
        <node TEXT="Role change detected (admin action)"/>
        <node TEXT="Password changed from another session"/>
        <node TEXT="Security event (suspicious activity)"/>
        <node TEXT="Account disabled by admin"/>
    </node>

    <node TEXT="5.4 Graceful logout" FOLDED="false">
        <node TEXT="Clear tokens (access + refresh)"/>
        <node TEXT="Clear cached profile/data"/>
        <node TEXT="POST /api/auth/logout (invalidate server-side)"/>
        <node TEXT="Redirect to login with optional message"/>
    </node>

</node>

</node>
</map>
