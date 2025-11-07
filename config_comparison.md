# Heroku Config Comparison: autorisen (dev) vs capecraft (prod)

## 🔍 Configuration Analysis

### ✅ Variables Present in BOTH Apps
- ADMIN_EMAIL ✅
- AWS_ACCESS_KEY_ID ✅ (different values)
- AWS_S3_REGION_NAME ✅ 
- AWS_SECRET_ACCESS_KEY ✅ (different values)
- AWS_STORAGE_BUCKET_NAME ✅ (different values)
- CLIENT_URL ✅ (different values - expected)
- DATABASE_URL ✅ (different databases - expected)
- DB_HOST ✅
- DB_NAME ✅
- DB_PASSWORD ✅
- DB_PORT ✅
- DB_USER ✅
- DEBUG ✅
- DISABLE_COLLECTSTATIC ✅
- EMAIL_TOKEN_SECRET ✅
- ENABLE_PAYFAST ✅
- ENV ✅
- FROM_EMAIL ✅
- GEMINI_API_KEY ✅
- GOOGLE_CALLBACK_URL ✅ (different URLs - expected)
- GOOGLE_CLIENT_ID ✅
- GOOGLE_CLIENT_SECRET ✅
- JWT_SECRET ✅
- LINKEDIN_CALLBACK_URL ✅ (different URLs - expected)
- LINKEDIN_CLIENT_ID ✅
- LINKEDIN_CLIENT_SECRET ✅
- NODE_ENV ✅
- OPENAI_API_KEY ✅ (different keys)
- SECRET_KEY ✅ (different keys - expected)
- SMTP_HOST ✅
- SMTP_PASSWORD ✅ (different passwords)
- SMTP_PORT ✅
- SMTP_USERNAME ✅ (different usernames)

### ❌ Variables MISSING from Production (capecraft)
- ALEMBIC_DATABASE_URL
- ALLOWED_HOSTS (different format)
- AUTH_HARDEN_LOGIN
- AUTH_REQUIRE_EMAIL_VERIFICATION
- CORS_ALLOWED_ORIGINS
- CORS_ORIGINS
- DISABLE_RECAPTCHA
- EMAIL_FROM
- ENABLE_PERF_SAMPLER
- ENABLE_STRIPE
- FEATURE_EMAIL
- FRONTEND_ORIGIN
- HEROKU_API_KEY
- HEROKU_EMAIL
- HEROKU_POSTGRESQL_GREEN_URL
- OPENAI_MODEL
- PAYFAST_MERCHANT_KEY
- PAYFAST_MODE
- PAYFAST_NOTIFY_URL
- PAYFAST_PASSPHRASE
- PAYFAST_RETURN_URL
- PERF_SAMPLE_SECONDS
- PYTHONPATH
- REACT_APP_API_URL
- STRIPE_PUBLISHABLE_KEY
- STRIPE_SECRET_KEY
- VITE_GOOGLE_CLIENT_ID
- VITE_LINKEDIN_CLIENT_ID
- VITE_RECAPTCHA_SITE_KEY
- WEBHOOK
- WEB_CONCURRENCY

### ⚠️ Variables ONLY in Production (capecraft)
- SENDGRID_API_KEY
- SMTP_TLS

### 🚨 Critical Issues Found

1. **ALLOWED_HOSTS Mismatch**:
   - Dev: `autorisen-dac8e65796e7.herokuapp.com,dev.cape-control.com`
   - Prod: `*` (too permissive for production)

2. **Missing Critical Variables in Production**:
   - ALEMBIC_DATABASE_URL (needed for migrations)
   - CORS configuration (CORS_ALLOWED_ORIGINS, CORS_ORIGINS)
   - PYTHONPATH (needed for Python imports)
   - REACT_APP_API_URL (frontend needs this)
   - Stripe configuration (if payments are needed)
   - Performance monitoring (ENABLE_PERF_SAMPLER, PERF_SAMPLE_SECONDS)

3. **PayFast Configuration Issues**:
   - Prod has incorrect PAYFAST_CANCEL_URL pointing to ITN endpoint
   - Missing PAYFAST_MERCHANT_KEY, PAYFAST_MODE, etc.

4. **Security Concerns**:
   - Production SECRET_KEY appears to be a Django default (should be unique)
   - Different AWS credentials (might be intentional)
   - Different OpenAI API keys (might be intentional)

## 🛠️ Recommendations

1. **Sync Critical Missing Variables**
2. **Fix ALLOWED_HOSTS for production security**
3. **Correct PayFast configuration**
4. **Ensure proper CORS settings**
5. **Verify AWS and API key intentional differences**