# AutoLocal/CapeControl PR Template

<!-- Production-ready FastAPI + React SaaS platform -->
<!-- Updated: November 14, 2025 -->

## 📌 Summary

**Type:** <!-- feat | fix | chore | docs | refactor | perf | test | ci -->
**Component:** <!-- backend | frontend | infra | docs | workflows -->
**Impact:** <!-- breaking | feature | patch | internal -->

**Description:**
<!-- Brief description of changes made -->

## 🔄 Changes Made

### Backend Changes
- [ ] Core API modifications
- [ ] Database schema changes
- [ ] Agent/module updates
- [ ] Security/auth changes
- [ ] Performance improvements

### Frontend Changes
- [ ] UI/UX improvements
- [ ] Component updates
- [ ] Style/layout changes
- [ ] Asset updates
- [ ] Build configuration

### Infrastructure Changes
- [ ] Docker/deployment updates
- [ ] CI/CD workflow changes
- [ ] Environment configuration
- [ ] Dependencies updates

## 🧪 Testing & Validation

**Pre-submission Checklist:**
- [ ] Local tests pass (`make codex-test`)
- [ ] Docker build successful (`make docker-build`)
- [ ] Frontend builds without errors
- [ ] Linting passes (Python & TypeScript)
- [ ] No security vulnerabilities introduced
- [ ] Project plan synced if tasks changed (`scripts/plan_sync.py --apply` + `make project-info`)

**Manual Testing:**
- [ ] Authentication flow tested
- [ ] Core features functional
- [ ] UI responsive on mobile/desktop
- [ ] Error handling verified

## 📁 Files Modified

**Count:** <!-- number of files changed -->

**Key Files:**
<!-- List important files or use patterns like backend/src/modules/*/router.py -->

## 🔍 Deployment Considerations

**Database Changes:**
- [ ] Migrations included
- [ ] Backward compatibility maintained
- [ ] Migration tested locally

**Environment Variables:**
- [ ] New variables documented
- [ ] Heroku config updated (if needed)
- [ ] Sensitive data properly handled

**Breaking Changes:**
- [ ] No breaking changes
- [ ] Breaking changes documented below

## 📋 Additional Notes

<!-- Any additional context, concerns, or follow-up items -->