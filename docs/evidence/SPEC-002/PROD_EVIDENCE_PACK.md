# SPEC-002 Production Deploy Evidence Pack (capecraft v783)

## 1) Summary
- Change scope: docs-only (SECURITY_CSRF.md, SYSTEM_SPEC.md)
- Target: capecraft (production)
- Release: v783
- Sanity checks: /api/version, /api/health, / all HTTP 200
- Phase 3 (tests/builds): skipped (docs-only)

## 2) Phase 0 Evidence

### phase0_date.txt
```
Tue 10 Feb 2026 03:08:46 PM UTC
```

### phase0_git_status.txt
```

```

### phase0_branch.txt
```
main
```

### phase0_log_5.txt
```
38638157 docs(security): specify CSRF token/cookie/header policy (SPEC-002)
e3fed5ff docs(plan): record SPEC-001 merged (PR #42)
31813bc2 docs(plan): mark DOC-OPS-DOCKER-001 done (visibility note)
98fc9028 chore(repo): ignore hygiene + Docker Hub publish workflow (manual)
5db1b166 chore(evidence): add ship-autorisen-log make target
```

### phase0_show_last.txt
```
38638157 docs(security): specify CSRF token/cookie/header policy (SPEC-002)
docs/SECURITY_CSRF.md
docs/SYSTEM_SPEC.md
```

## 3) Phase 1 Evidence

### phase1_show_source_0b627d7b.txt
```
0b627d7b docs(security): specify CSRF token/cookie/header policy (SPEC-002)
docs/SECURITY_CSRF.md
docs/SYSTEM_SPEC.md
```

### phase1_show_main_38638157.txt
```
38638157 docs(security): specify CSRF token/cookie/header policy (SPEC-002)
docs/SECURITY_CSRF.md
docs/SYSTEM_SPEC.md
```

### phase1_log_decorate_10.txt
```
38638157 (HEAD -> main, origin/main) docs(security): specify CSRF token/cookie/header policy (SPEC-002)
e3fed5ff docs(plan): record SPEC-001 merged (PR #42)
31813bc2 (backup/main-ahead-20260210-091952) docs(plan): mark DOC-OPS-DOCKER-001 done (visibility note)
98fc9028 chore(repo): ignore hygiene + Docker Hub publish workflow (manual)
5db1b166 chore(evidence): add ship-autorisen-log make target
abe4e1e2 chore(deploy): add ship-autorisen make target
4c8ba53f chore(deploy): add autorisen deploy + verify make targets
617049ca chore(deploy): guardrails to prevent accidental capecraft deploys
9bbb918f Harden version metadata and support ticket mapping
ee587f1c fix(migrations): scope idempotence checks to public schema
```

## 4) Phase 2 Evidence

### phase2_apps_info_capecraft.txt
```
=== capecraft

Addons:         heroku-postgresql:essential-0
Auto Cert Mgmt: true
Dynos:          web: 1
Git URL:        https://git.heroku.com/capecraft.git
Owner:          zeonita@gmail.com
Pipeline:       capecontrol - production
Region:         us
Repo Size:      0 B
Slug Size:      0 B
Stack:          container
Web URL:        https://capecraft-65eeb6ddf78b.herokuapp.com/
```

### phase2_releases_head.txt
```
=== capecraft Releases - Current: v783

 v783 Deployed web (dd20d2272d2b)                  zeonita@gmail.com 2026/02/10 16:52:43 +0200 (~ 16m ago) 
 v782 Rollback to v780                             zeonita@gmail.com 2026/02/10 03:23:04 +0200 (~ 13h ago) 
 v781 Deployed web (bc9fd6d462d3)                  zeonita@gmail.com 2026/02/09 16:37:57 +0200 (~ 24h ago) 
 v780 Deployed web (42508dd5e918)                  zeonita@gmail.com 2026/01/20 04:52:07 +0200             
 v779 Deployed web (9391b9c2a8f2)                  zeonita@gmail.com 2026/01/11 10:39:23 +0200             
 v778 Set RUN_DB_MIGRATIONS_ON_STARTUP config vars zeonita@gmail.com 2026/01/11 10:38:08 +0200             
 v777 Rollback to v775                             zeonita@gmail.com 2026/01/09 03:31:44 +0200             
 v776 Deployed web (54f2294675d8)                  zeonita@gmail.com 2026/01/09 03:23:46 +0200             
 v775 Set PAYFAST_PASSPHRASE config vars           zeonita@gmail.com 2026/01/06 09:37:06 +0200             
 v774 Deployed web (819dd6bbb3f0)                  zeonita@gmail.com 2026/01/06 09:08:21 +0200             
 v773 Deployed web (d03ceecd3b33)                  zeonita@gmail.com 2026/01/06 08:19:14 +0200             
 v772 Set PAYFAST_PASSPHRASE config vars           zeonita@gmail.com 2026/01/06 06:52:10 +0200             
 v771 Set PAYFAST_MERCHANT_KEY config vars         zeonita@gmail.com 2026/01/05 17:09:33 +0200             
 v770 Set PAYFAST_MERCHANT_ID config vars          zeonita@gmail.com 2026/01/05 17:09:05 +0200             
 v769 Deployed web (fc1fff254b5d)                  zeonita@gmail.com 2026/01/04 09:17:00 +0200             
```

### capecraft URL proof
- https://capecraft-65eeb6ddf78b.herokuapp.com

### phase2_apps_info_autorisen.txt (optional corroboration)
```
=== autorisen

Addons:         heroku-postgresql:essential-0
Auto Cert Mgmt: true
Dynos:          web: 1, worker: 1
Git URL:        https://git.heroku.com/autorisen.git
Owner:          zeonita@gmail.com
Pipeline:       capecontrol - development
Region:         us
Repo Size:      8 MB
Slug Size:      0 B
Stack:          container
Web URL:        https://autorisen-dac8e65796e7.herokuapp.com/
```

## 5) Phase 3 Deviation

### phase3_skipped.txt
```
Phase 3 (tests/builds) intentionally skipped: docs-only change (SECURITY_CSRF.md, SYSTEM_SPEC.md).
```

## 6) Phase 4 Evidence

### phase4_releases_head.txt
```
=== capecraft Releases - Current: v783

 v783 Deployed web (dd20d2272d2b)                  zeonita@gmail.com 2026/02/10 16:52:43 +0200 (~ 17m ago) 
 v782 Rollback to v780                             zeonita@gmail.com 2026/02/10 03:23:04 +0200 (~ 13h ago) 
 v781 Deployed web (bc9fd6d462d3)                  zeonita@gmail.com 2026/02/09 16:37:57 +0200 (~ 24h ago) 
 v780 Deployed web (42508dd5e918)                  zeonita@gmail.com 2026/01/20 04:52:07 +0200             
 v779 Deployed web (9391b9c2a8f2)                  zeonita@gmail.com 2026/01/11 10:39:23 +0200             
 v778 Set RUN_DB_MIGRATIONS_ON_STARTUP config vars zeonita@gmail.com 2026/01/11 10:38:08 +0200             
 v777 Rollback to v775                             zeonita@gmail.com 2026/01/09 03:31:44 +0200             
 v776 Deployed web (54f2294675d8)                  zeonita@gmail.com 2026/01/09 03:23:46 +0200             
 v775 Set PAYFAST_PASSPHRASE config vars           zeonita@gmail.com 2026/01/06 09:37:06 +0200             
 v774 Deployed web (819dd6bbb3f0)                  zeonita@gmail.com 2026/01/06 09:08:21 +0200             
 v773 Deployed web (d03ceecd3b33)                  zeonita@gmail.com 2026/01/06 08:19:14 +0200             
 v772 Set PAYFAST_PASSPHRASE config vars           zeonita@gmail.com 2026/01/06 06:52:10 +0200             
 v771 Set PAYFAST_MERCHANT_KEY config vars         zeonita@gmail.com 2026/01/05 17:09:33 +0200             
 v770 Set PAYFAST_MERCHANT_ID config vars          zeonita@gmail.com 2026/01/05 17:09:05 +0200             
 v769 Deployed web (fc1fff254b5d)                  zeonita@gmail.com 2026/01/04 09:17:00 +0200             
```

### phase4_release_v783_info.txt
```
=== Release v783

Add-ons:                heroku-postgresql:essential-0
By:                     zeonita@gmail.com
Change:                 Deployed web (dd20d2272d2b)
Eligible for Rollback?: Yes
When:                   2026-02-10T14:52:43Z
```

### phase4_layer_reuse_note.txt
```
Note: "Mounted from autorisen/web" indicates container registry layer reuse, not a deploy to autorisen.
```

## 7) Phase 5 Evidence

### phase5_version_headers.txt
```
HTTP/1.1 200 OK
Cache-Control: no-store
Content-Length: 70
Content-Type: application/json
Date: Tue, 10 Feb 2026 15:10:51 GMT
Nel: {"report_to":"heroku-nel","response_headers":["Via"],"max_age":3600,"success_fraction":0.01,"failure_fraction":0.1}
Report-To: {"group":"heroku-nel","endpoints":[{"url":"https://nel.heroku.com/reports?s=wcR8t89XBRpWDnH7X8QSc0k%2B7bk%2B7HBM%2BSdKqhD4lc0%3D\u0026sid=c46efe9b-d3d2-4a0c-8c76-bfafa16c5add\u0026ts=1770736252"}],"max_age":3600}
Reporting-Endpoints: heroku-nel="https://nel.heroku.com/reports?s=wcR8t89XBRpWDnH7X8QSc0k%2B7bk%2B7HBM%2BSdKqhD4lc0%3D&sid=c46efe9b-d3d2-4a0c-8c76-bfafa16c5add&ts=1770736252"
Server: Heroku
Via: 1.1 heroku-router
X-Ratelimit-Limit: 100
X-Ratelimit-Remaining: 99
X-Ratelimit-Reset: 1770736076
```

### phase5_version_body.json
```json
{"buildVersion":"488","version":"488","gitSha":null,"buildEpoch":null}
```

### phase5_version_httpcode.txt
```
200
```

### phase5_health_headers.txt
```
HTTP/1.1 200 OK
Cache-Control: no-store
Content-Length: 144
Content-Type: application/json
Date: Tue, 10 Feb 2026 15:11:03 GMT
Nel: {"report_to":"heroku-nel","response_headers":["Via"],"max_age":3600,"success_fraction":0.01,"failure_fraction":0.1}
Report-To: {"group":"heroku-nel","endpoints":[{"url":"https://nel.heroku.com/reports?s=oAyiaeA4gXGq4BMgm9Foari9X3RTa8xHAOWAFv%2BLvzw%3D\u0026sid=c46efe9b-d3d2-4a0c-8c76-bfafa16c5add\u0026ts=1770736264"}],"max_age":3600}
Reporting-Endpoints: heroku-nel="https://nel.heroku.com/reports?s=oAyiaeA4gXGq4BMgm9Foari9X3RTa8xHAOWAFv%2BLvzw%3D&sid=c46efe9b-d3d2-4a0c-8c76-bfafa16c5add&ts=1770736264"
Server: Heroku
Via: 1.1 heroku-router
X-Ratelimit-Limit: 100
X-Ratelimit-Remaining: 99
X-Ratelimit-Reset: 1770736324
```

### phase5_health_body.json
```json
{"status":"healthy","version":"dev","env":"prod","database_connected":true,"input_sanitization":"enabled (Task 1.2.4)","rate_limiting":"active"}
```

### phase5_health_httpcode.txt
```
200
```

### phase5_root_httpcode.txt
```
200
```

## 8) Operator Notes
- cherry-pick 0b627d7b -> 38638157
- "Mounted from autorisen/web" explanation
- /api/version returned 200
- docs-only justification for skipping Phase 3
