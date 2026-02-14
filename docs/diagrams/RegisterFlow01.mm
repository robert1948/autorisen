<map version="1.0.1">
<node TEXT="CapeControl&#xa;Registration Flow &amp;&#xa;Database Interaction&#xa;(Improved)" FOLDED="false" COLOR="#000000">
<font NAME="SansSerif" SIZE="14" BOLD="true"/>

<!-- 1) Entry Point -->
<node TEXT="1) Entry Point &#x2013; Landing Page" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>
  <node TEXT="User clicks &#x201c;Create free account&#x201d; (global CTA)"/>
  <node TEXT="Route to /auth/register"/>
  <node TEXT="Preserve context (optional)">
    <node TEXT="ref / utm / interest trail stored in session or cookie"/>
    <node TEXT="Sanitize and validate tracking params before storage"/>
  </node>
</node>

<!-- 2) Register Form -->
<node TEXT="2) Register Form (Frontend)" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>
  <node TEXT="User inputs">
    <node TEXT="Name (optional or required per spec)"/>
    <node TEXT="Email"/>
    <node TEXT="Password"/>
    <node TEXT="Confirm password"/>
    <node TEXT="Accept Terms/Privacy checkbox"/>
  </node>
  <node TEXT="Bot protection">
    <node TEXT="Honeypot hidden field (low friction)"/>
    <node TEXT="CAPTCHA (reCAPTCHA v3 / Turnstile) on suspicious signals"/>
  </node>
  <node TEXT="CSRF token">
    <node TEXT="Include CSRF token in form (rendered server-side or fetched)"/>
    <node TEXT="Validate on backend before processing"/>
  </node>
  <node TEXT="Client-side validation">
    <node TEXT="Email format (RFC 5322 basic)"/>
    <node TEXT="Password rules (length &#x2265; 12, complexity optional)"/>
    <node TEXT="Password match (confirm_password)"/>
    <node TEXT="Terms checkbox required"/>
  </node>
  <node TEXT="If validation fails">
    <node TEXT="Show inline errors per field"/>
    <node TEXT="Do not submit"/>
  </node>
  <node TEXT="Submit UX">
    <node TEXT="Disable button + show loading spinner"/>
    <node TEXT="Prevent double-submit (debounce + flag)"/>
    <node TEXT="Strip confirm_password &#x2014; do NOT send to backend"/>
  </node>
</node>

<!-- 3) API Call -->
<node TEXT="3) API Call to Backend" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>
  <node TEXT="Request">
    <node TEXT="POST /api/auth/register"/>
    <node TEXT="Headers: CSRF token, Content-Type: application/json"/>
  </node>
  <node TEXT="Payload">
    <node TEXT="name, email, password, termsAccepted (boolean)"/>
    <node TEXT="confirm_password is NOT sent (frontend-only concern)"/>
    <node TEXT="honeypot field (should be empty)"/>
  </node>
  <node TEXT="Response handling">
    <node TEXT="201 &#x2192; advance to verification screen"/>
    <node TEXT="409 &#x2192; &#x201c;An account with this email may already exist&#x201d; (vague to prevent enumeration)"/>
    <node TEXT="400 &#x2192; show validation errors"/>
    <node TEXT="429 &#x2192; &#x201c;Too many attempts, please wait&#x201d;"/>
    <node TEXT="500 &#x2192; &#x201c;Something went wrong, please try again&#x201d;"/>
  </node>
</node>

<!-- 4) Backend Registration Logic -->
<node TEXT="4) Backend Registration Logic" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>

  <node TEXT="Middleware (before handler)">
    <node TEXT="Rate limiting">
      <node TEXT="Per IP: e.g. 5 requests / minute"/>
      <node TEXT="Global: circuit breaker if registration spike detected"/>
      <node TEXT="Return 429 if exceeded"/>
    </node>
    <node TEXT="CSRF validation">
      <node TEXT="Reject if token missing or invalid &#x2192; 403"/>
    </node>
    <node TEXT="Bot detection">
      <node TEXT="Check honeypot field is empty"/>
      <node TEXT="Verify CAPTCHA token if present"/>
      <node TEXT="Reject silently or return 403"/>
    </node>
  </node>

  <node TEXT="Input processing">
    <node TEXT="Trim all string fields"/>
    <node TEXT="Normalize email (lowercase, trim)"/>
    <node TEXT="Validate schema (required fields, types)"/>
    <node TEXT="Validate password policy (min 12 chars, check against breached password list optional)"/>
    <node TEXT="Validate termsAccepted == true"/>
  </node>

  <node TEXT="Security">
    <node TEXT="Never store plain password"/>
    <node TEXT="Never log password or email in plain text"/>
    <node TEXT="Audit log: registration attempt (IP, timestamp, success/fail, anonymized email hash)"/>
  </node>

  <node TEXT="Database interaction">
    <node TEXT="BEGIN transaction">
      <node TEXT="Spans: users + profile + onboarding_state + verification_tokens"/>
    </node>
    <node TEXT="Enforce unique email (race-safe)">
      <node TEXT="DB UNIQUE constraint: UNIQUE(lower(email)) or CITEXT column"/>
      <node TEXT="Optional fast-path: SELECT by email for friendly error (not authoritative)"/>
      <node TEXT="UNIQUE constraint is final authority"/>
    </node>
    <node TEXT="Hash password">
      <node TEXT="Use argon2id (preferred) or bcrypt (cost &#x2265; 12)"/>
    </node>
    <node TEXT="Insert user">
      <node TEXT="INSERT INTO users (name, email, password_hash, email_verified, created_at) RETURNING id"/>
      <node TEXT="email_verified = false"/>
      <node TEXT="On unique_violation: ROLLBACK &#x2192; return 409"/>
    </node>
    <node TEXT="Create related rows">
      <node TEXT="profile row (if separate table)"/>
      <node TEXT="onboarding_state row (step: &#x2018;registered&#x2019;)"/>
      <node TEXT="terms_acceptance record">
        <node TEXT="user_id, terms_version, accepted_at = now()"/>
      </node>
    </node>
    <node TEXT="Generate verification token">
      <node TEXT="Generate cryptographically random token (32+ bytes)"/>
      <node TEXT="Store HASHED token + expiry (e.g. 24 hours) in verification_tokens table"/>
      <node TEXT="Link to user_id"/>
    </node>
    <node TEXT="COMMIT transaction">
      <node TEXT="ROLLBACK on any error &#x2192; prevents partial rows"/>
    </node>
  </node>

  <node TEXT="Post-commit actions (outside transaction)">
    <node TEXT="Send verification email (async queue preferred)">
      <node TEXT="Include: verification link with raw token"/>
      <node TEXT="Link format: /auth/verify-email?token=xxx&amp;email=yyy"/>
      <node TEXT="Email only sent AFTER successful commit"/>
    </node>
    <node TEXT="Emit event: user.registered (for analytics, webhooks)"/>
    <node TEXT="Structured log: { event: user_registered, user_id, ip, timestamp }"/>
  </node>

  <node TEXT="Response outcomes">
    <node TEXT="201 Created &#x2192; { message: &#x201c;Check your email&#x201d;, userId (optional) }"/>
    <node TEXT="409 Conflict &#x2192; vague message (prevent enumeration)"/>
    <node TEXT="400 Bad Request &#x2192; validation error details"/>
    <node TEXT="429 Too Many Requests &#x2192; retry-after header"/>
    <node TEXT="500 Server Error &#x2192; generic message to user"/>
  </node>
</node>

<!-- 5) Email Verification Flow -->
<node TEXT="5) Email Verification Flow" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>
  <node TEXT="User receives email">
    <node TEXT="Clicks verification link"/>
    <node TEXT="GET /auth/verify-email?token=xxx&amp;email=yyy"/>
  </node>
  <node TEXT="Backend verification logic">
    <node TEXT="Look up hashed token for email"/>
    <node TEXT="Check token not expired"/>
    <node TEXT="Check token not already used"/>
    <node TEXT="If valid: UPDATE users SET email_verified = true, verified_at = now()"/>
    <node TEXT="Delete or mark token as used"/>
    <node TEXT="If invalid/expired: show error + offer resend"/>
  </node>
  <node TEXT="Resend verification flow">
    <node TEXT="POST /api/auth/resend-verification"/>
    <node TEXT="Rate limit: 3 resends per email per hour"/>
    <node TEXT="Invalidate previous tokens"/>
    <node TEXT="Generate new token + send email"/>
  </node>
  <node TEXT="Token expiry cleanup">
    <node TEXT="Scheduled job: delete expired tokens (e.g. daily)"/>
  </node>
</node>

<!-- 6) Auth Session Creation -->
<node TEXT="6) Auth Session Creation" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>
  <node TEXT="Triggered AFTER email verification (not at registration)">
    <node TEXT="Issue JWT or session token"/>
    <node TEXT="Store in httpOnly, Secure, SameSite=Strict cookie"/>
    <node TEXT="Set reasonable expiry (e.g. 1 hour access, 7 day refresh)"/>
  </node>
  <node TEXT="Login before verification">
    <node TEXT="Block with message: &#x201c;Please verify your email first&#x201d;"/>
    <node TEXT="Offer resend link"/>
  </node>
</node>

<!-- 7) Post-Register Routing -->
<node TEXT="7) Post-Register Routing" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>
  <node TEXT="Immediately after registration (pre-verification)">
    <node TEXT="/auth/check-email (&#x201c;We sent you a verification email&#x201d;)"/>
    <node TEXT="Show resend button (with cooldown timer)"/>
  </node>
  <node TEXT="After email verification + login">
    <node TEXT="/onboarding/welcome"/>
    <node TEXT="/onboarding/profile"/>
    <node TEXT="/onboarding/checklist"/>
    <node TEXT="/app/dashboard"/>
  </node>
  <node TEXT="Preserve context">
    <node TEXT="Restore ref/utm/interest from registration"/>
    <node TEXT="Show personalized next-step based on context"/>
  </node>
  <node TEXT="Send welcome email (separate from verification)">
    <node TEXT="Triggered after first successful login or verification"/>
    <node TEXT="Include onboarding tips, support contact"/>
  </node>
</node>

<!-- 8) Terms Gate -->
<node TEXT="8) Terms Gate (if enforced)" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>
  <node TEXT="Data fields">
    <node TEXT="terms_accepted_at (timestamp)"/>
    <node TEXT="terms_version (string, e.g. &#x201c;2025-06-15-v2&#x201d;)"/>
  </node>
  <node TEXT="Version change handling">
    <node TEXT="On terms update: compare user&#x2019;s accepted version vs current"/>
    <node TEXT="If outdated: force re-acceptance on next login"/>
    <node TEXT="Store history: terms_acceptances (user_id, version, accepted_at)"/>
  </node>
  <node TEXT="Frontend guard">
    <node TEXT="If terms not accepted (or outdated): force route to /terms"/>
    <node TEXT="Block /app/* until accepted"/>
  </node>
  <node TEXT="Backend enforcement">
    <node TEXT="Middleware on protected endpoints: verify terms_version is current"/>
    <node TEXT="Return 403 with redirect hint if outdated"/>
  </node>
  <node TEXT="Acceptance flow">
    <node TEXT="User accepts terms"/>
    <node TEXT="UPDATE users SET terms_accepted_at = now(), terms_version = :current"/>
    <node TEXT="INSERT INTO terms_acceptances (user_id, version, accepted_at, ip_address)"/>
    <node TEXT="Allow app access"/>
  </node>
</node>

<!-- 9) Developer Registration -->
<node TEXT="9) Developer Registration" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>

  <node TEXT="Entry Point">
    <node TEXT="Developer portal link or /auth/register?role=developer"/>
    <node TEXT="Marketplace &#x201c;Become a Developer&#x201d; CTA"/>
    <node TEXT="Role param validated against allowlist (developer); reject unknown roles"/>
  </node>

  <node TEXT="Additional Form Fields (beyond standard registration)">
    <node TEXT="Organization / Company name (optional)"/>
    <node TEXT="Developer use-case / intent (dropdown: build agents, publish marketplace, internal tooling)"/>
    <node TEXT="Website / GitHub URL (optional, validated format)"/>
    <node TEXT="Accept Developer Terms &amp; API Usage Policy checkbox"/>
    <node TEXT="All standard fields still required (name, email, password, general terms)"/>
  </node>

  <node TEXT="Backend Logic">
    <node TEXT="Standard user creation (steps 3&#x2013;4 above) within same transaction">
      <node TEXT="All middleware applies: rate limiting, CSRF, bot detection"/>
    </node>
    <node TEXT="Assign role = &#x2018;developer&#x2019;">
      <node TEXT="INSERT INTO user_roles (user_id, role) VALUES (:id, &#x2018;developer&#x2019;)"/>
      <node TEXT="Role assignment within same transaction as user creation"/>
    </node>
    <node TEXT="Provision API credentials (post-verification, not at registration)">
      <node TEXT="Generate API key pair (client_id + client_secret)"/>
      <node TEXT="Store HASHED client_secret in api_credentials table"/>
      <node TEXT="Return client_secret once on developer dashboard (show-once pattern)"/>
      <node TEXT="Credentials only provisioned AFTER email verification completes"/>
    </node>
    <node TEXT="Record developer-specific data">
      <node TEXT="developer_terms_accepted_at + version in terms_acceptances"/>
      <node TEXT="organization, use_case, website in developer_profiles table"/>
    </node>
    <node TEXT="Audit log: developer_registered event (user_id, IP, timestamp)"/>
  </node>

  <node TEXT="Post-Register Routing">
    <node TEXT="Standard email verification flow (section 5) applies first"/>
    <node TEXT="After verification + login:">
      <node TEXT="/onboarding/developer-setup (API key provisioning, docs intro)"/>
      <node TEXT="/developer/dashboard (API keys, usage stats, sandbox)"/>
      <node TEXT="/developer/apps (register and manage applications)"/>
      <node TEXT="/developer/docs (API documentation, SDKs)"/>
    </node>
  </node>

  <node TEXT="Verification Checklist">
    <node TEXT="Role = developer in user_roles table"/>
    <node TEXT="developer_profiles row created with org/use-case data"/>
    <node TEXT="API credentials row created (post-verification only)"/>
    <node TEXT="Developer terms acceptance recorded (separate from general terms)"/>
    <node TEXT="Developer dashboard accessible after login"/>
    <node TEXT="Standard user verification items also pass (section 10)"/>
  </node>
</node>

<!-- 10) Admin Registration -->
<node TEXT="10) Admin Registration" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>

  <node TEXT="Entry Point (invite-only)">
    <node TEXT="No public self-registration for Admin role"/>
    <node TEXT="Existing Admin sends invite via POST /api/admin/invite">
      <node TEXT="Requires authenticated admin session + MFA confirmation"/>
      <node TEXT="Payload: target_email, optional: role_scope, expiry_hours"/>
    </node>
    <node TEXT="Generates signed invite token (cryptographically random, 32+ bytes)"/>
    <node TEXT="Invite email sent with one-time registration URL">
      <node TEXT="Link: /auth/register?invite=xxx&amp;email=yyy"/>
      <node TEXT="Email sent async (queue) after invite record committed"/>
    </node>
  </node>

  <node TEXT="Invite Token Handling">
    <node TEXT="Token stored HASHED in admin_invites table">
      <node TEXT="Fields: id, hashed_token, target_email, invited_by, created_at, expires_at, used_at, used_by"/>
    </node>
    <node TEXT="Expiry: configurable (default 48h), single-use, revocable"/>
    <node TEXT="Validate token before rendering register form">
      <node TEXT="Check: exists, not expired, not used, email matches"/>
      <node TEXT="Expired/invalid/used token &#x2192; 403 + friendly message + contact admin"/>
    </node>
    <node TEXT="Scheduled cleanup: delete expired invite tokens (e.g. daily job)"/>
  </node>

  <node TEXT="Register Form">
    <node TEXT="Same base fields as standard registration (name, email, password)"/>
    <node TEXT="Email pre-filled from invite (read-only, must match invite)"/>
    <node TEXT="MFA setup REQUIRED at registration">
      <node TEXT="TOTP app enrollment (show QR code + manual key)"/>
      <node TEXT="User must confirm with valid TOTP code before proceeding"/>
    </node>
    <node TEXT="Accept Admin Terms &amp; Responsibilities checkbox"/>
    <node TEXT="All standard protections apply (CSRF, bot detection, rate limiting)"/>
  </node>

  <node TEXT="Backend Logic">
    <node TEXT="Validate invite token (exists, not expired, not used, email matches)">
      <node TEXT="Reject with 403 if invalid"/>
    </node>
    <node TEXT="Standard user creation (steps 3&#x2013;4 above) within same transaction">
      <node TEXT="All middleware applies"/>
    </node>
    <node TEXT="Assign role = &#x2018;admin&#x2019;">
      <node TEXT="INSERT INTO user_roles (user_id, role) VALUES (:id, &#x2018;admin&#x2019;)"/>
      <node TEXT="Role assignment within same transaction"/>
    </node>
    <node TEXT="Mark invite token as consumed">
      <node TEXT="UPDATE admin_invites SET used_at = now(), used_by = :user_id"/>
      <node TEXT="Within same transaction (prevents race condition)"/>
    </node>
    <node TEXT="Enforce MFA enrollment">
      <node TEXT="Generate TOTP secret, store encrypted in mfa_credentials table"/>
      <node TEXT="Require TOTP confirmation code before account activation"/>
      <node TEXT="Account not fully active until MFA confirmed"/>
    </node>
    <node TEXT="Skip email verification (invite email already proves ownership)">
      <node TEXT="Set email_verified = true at creation"/>
      <node TEXT="Or: still require verification for defense-in-depth (configurable)"/>
    </node>
    <node TEXT="Audit log: admin_created event">
      <node TEXT="Fields: inviter_id, invitee_id, IP, timestamp"/>
      <node TEXT="Notify existing admins of new admin account creation"/>
    </node>
  </node>

  <node TEXT="Post-Register Routing">
    <node TEXT="/admin/mfa-setup (complete MFA enrollment if not done inline)"/>
    <node TEXT="/admin/dashboard (user management, system configuration)"/>
    <node TEXT="/admin/audit-log (review system activity)"/>
    <node TEXT="/admin/invites (manage pending invitations)"/>
  </node>

  <node TEXT="Security Controls">
    <node TEXT="Only existing admins with MFA can create invites"/>
    <node TEXT="MFA mandatory for all admin accounts (enforced at login)"/>
    <node TEXT="Admin actions logged to immutable audit trail"/>
    <node TEXT="Session timeout shorter than standard users (e.g. 15 min idle)"/>
    <node TEXT="IP allowlist (optional, configurable per deployment)"/>
    <node TEXT="Admin role cannot be self-assigned or escalated via API"/>
    <node TEXT="Invite revocation: DELETE or expire pending invites"/>
  </node>

  <node TEXT="Verification Checklist">
    <node TEXT="Role = admin in user_roles table"/>
    <node TEXT="Invite token marked as used (used_at, used_by populated)"/>
    <node TEXT="MFA enrolled and confirmed (mfa_credentials row, verified = true)"/>
    <node TEXT="Audit log entry for admin creation (inviter + invitee)"/>
    <node TEXT="Admin dashboard accessible after MFA verification"/>
    <node TEXT="Existing admins notified of new admin account"/>
    <node TEXT="Standard user verification items also pass (section 12)"/>
  </node>
</node>

<!-- 11) Observability & Monitoring -->
<node TEXT="11) Observability &amp; Monitoring" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>
  <node TEXT="Metrics to track">
    <node TEXT="Registration attempts (total, success, failure by type)"/>
    <node TEXT="Verification email sent vs verified (conversion rate)"/>
    <node TEXT="Time from registration to verification"/>
    <node TEXT="409 rate (potential enumeration attacks)"/>
    <node TEXT="429 rate (rate limit effectiveness)"/>
  </node>
  <node TEXT="Alerts">
    <node TEXT="Spike in registration attempts from single IP"/>
    <node TEXT="Spike in 409 responses (enumeration attack)"/>
    <node TEXT="Verification email delivery failures"/>
    <node TEXT="Transaction rollback rate increase"/>
  </node>
  <node TEXT="Structured logging">
    <node TEXT="Every registration: event type, anonymized data, IP, status code, duration"/>
    <node TEXT="Never log passwords, tokens, or full email addresses"/>
  </node>
</node>

<!-- 12) Verification Checklist -->
<node TEXT="12) Verification Checklist (Evidence)" POSITION="right" FOLDED="false">
  <font NAME="SansSerif" SIZE="12" BOLD="true"/>
  <node TEXT="Frontend">
    <node TEXT="Routes: landing &#x2192; register &#x2192; check-email &#x2192; verify &#x2192; onboarding"/>
    <node TEXT="Validation errors render correctly (inline, per field)"/>
    <node TEXT="Loading state works"/>
    <node TEXT="409/400/429 messages mapped cleanly (no information leakage)"/>
    <node TEXT="Auth stored securely (httpOnly cookie)"/>
    <node TEXT="CSRF token included in form submission"/>
    <node TEXT="Bot protection active"/>
    <node TEXT="Resend verification flow works"/>
  </node>
  <node TEXT="Backend">
    <node TEXT="User created in DB with email_verified = false"/>
    <node TEXT="Password hashed (argon2id/bcrypt)"/>
    <node TEXT="Duplicate email blocked (409, vague message)"/>
    <node TEXT="Rate limiting active and returning 429"/>
    <node TEXT="CSRF validation active"/>
    <node TEXT="Verification email sent after commit"/>
    <node TEXT="Verification token validates correctly"/>
    <node TEXT="Expired tokens rejected"/>
    <node TEXT="Logs show expected status codes (no sensitive data)"/>
  </node>
  <node TEXT="Database">
    <node TEXT="users row present with email_verified = false initially"/>
    <node TEXT="verification_tokens row with hashed token and expiry"/>
    <node TEXT="profile / onboarding rows created (if used)"/>
    <node TEXT="terms_accepted_at and terms_version set"/>
    <node TEXT="terms_acceptances history row (if versioned)"/>
    <node TEXT="No plain text passwords or tokens stored"/>
  </node>
  <node TEXT="Security">
    <node TEXT="No user enumeration via registration or verification"/>
    <node TEXT="Rate limiting prevents brute force"/>
    <node TEXT="CSRF prevents cross-site submission"/>
    <node TEXT="Bot protection prevents automated signups"/>
    <node TEXT="Tokens are single-use and time-limited"/>
  </node>
</node>

</node>
</map>
