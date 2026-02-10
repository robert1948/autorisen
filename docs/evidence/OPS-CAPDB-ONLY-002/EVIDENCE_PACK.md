# OPS-CAPDB-ONLY-002 Evidence Pack
## Summary
- Goal: Use capecraft Postgres as the single DB until LinkedIn release; autorisen connects to capecraft DB in read-only mode.
- Change: Added backend middleware to block write methods when READ_ONLY_MODE=1.
- Verification: Initial 503s were due to maintenance mode ON; post-maintenance retry returned 200s; write attempt returned 403 on autorisen.

## Key Evidence Index
- Middleware code: backend/src/middleware/read_only.py
- App wiring: backend/src/app.py
- Test: backend/tests/test_read_only_mode.py

## Phase 3 — Implement read-only middleware + test
- Test run: logs/phase3_pytest.txt
- Client build: logs/phase3_npm_ci.txt, logs/phase3_npm_build.txt

## Phase 4 — Deploy to autorisen
- Config set: logs/phase4_set_readonly_autorisen.txt
- Container push/release: logs/phase4_aut_container_push.txt, logs/phase4_aut_container_release.txt

## Phase 5 — Verification
### Phase 5 initial (maintenance mode ON)
- autorisen health/version: logs/phase5_aut_health_http.txt, logs/phase5_aut_version_http.txt
- capecraft health/version: logs/phase5_cap_health_http.txt, logs/phase5_cap_version_http.txt
Note: HTTP 503 expected when maintenance mode is ON.

### Maintenance OFF proof
- autorisen: logs/phase6_aut_maint_off.txt, logs/phase6_aut_maint_status.txt
- capecraft: logs/phase6_cap_maint_off.txt, logs/phase6_cap_maint_status.txt

### Phase 5 retry (post-maintenance) — clean checks
- autorisen health/version: logs/phase5r_aut_health_http.txt, logs/phase5r_aut_version_http.txt (200/200)
- capecraft health/version: logs/phase5r_cap_health_http.txt, logs/phase5r_cap_version_http.txt (200/200)

### Read-only proof (autorisen)
- POST blocked: logs/phase5r_aut_post_block_http.txt (403)

## Notes / Safety
- No DB credentials printed.
- No production deploy actions were performed in this step beyond the already-recorded autorisen deploy.
- Maintenance-mode 503s were handled by turning maintenance off and re-checking.
