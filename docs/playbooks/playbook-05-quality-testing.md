# Playbook 05: Quality & Test Readiness

**Owner**: TestGuardianAgent
**Supporting Agents**: Auth Guardian, DevOps Pilot, Release Captain
**Status**: Planned
**Priority**: P1

---

## 1) Outcome

Guarantee a deterministic, automated testing framework for backend and frontend components, enabling consistent, reproducible results across environments and release pipelines.

**Definition of Done (DoD):**

* Full pytest suite passes without flakiness.
* Deterministic fixtures auto-generated and version-controlled.
* Smoke tests run automatically post-deployment.
* Frontend smoke tests validate key user flows (login, onboarding, dashboard load).
* CI pipeline includes test coverage reporting.

---

## 2) Scope (In / Out)

**In Scope:**

* Backend pytest and fixture generation.
* Frontend smoke and integration tests.
* CI test gating in GitHub Actions.
* Coverage and performance metrics.

**Out of Scope:**

* Performance load testing at scale.
* Manual QA or usability studies.

---

## 3) Dependencies

**Upstream:**

* Playbook 02 – Backend Auth & Security (auth tests foundation).
* Playbook 04 – DevOps CI/CD (test pipeline integration).

**Downstream:**

* Playbook 01 – MVP Launch (requires passing tests before go-live).

---

## 4) Milestones

| Milestone | Description                          | Owner             | Status        |
| --------- | ------------------------------------ | ----------------- | ------------- |
| M1        | Pytest + fixture regeneration stable | TestGuardianAgent | ⏳ In Progress |
| M2        | Frontend smoke tests implemented     | Release Captain   | 🔄 Pending    |
| M3        | CI coverage reporting enabled        | DevOps Pilot      | 🔄 Pending    |
| M4        | Post-deploy smoke automation live    | TestGuardianAgent | 🔄 Pending    |
| M5        | QA summary report delivered          | TestGuardianAgent | 🔄 Pending    |

---

## 5) Checklist (Executable)

* [x] Create deterministic fixture regeneration script (`scripts/regenerate_fixtures.py`).
* [x] Enable pytest config in `pytest.ini` with proper testpaths.
* [ ] Integrate smoke test runner in CI pipeline.
* [ ] Add frontend Cypress or Playwright tests for login/onboarding.
* [ ] Generate coverage report via `pytest --cov`.
* [ ] Store reports in `docs/test_reports/`.

---

## 6) Runbook / Commands

```bash
# Run all tests
make test

# Run only backend tests
pytest backend/tests -v

# Regenerate fixtures deterministically
python3 scripts/regenerate_fixtures.py

# Run smoke tests
pytest -k "smoke" -v
```

---

## 7) Risks & Mitigations

| Risk                                          | Mitigation                                             |
| --------------------------------------------- | ------------------------------------------------------ |
| Tests fail intermittently due to async timing | Use `httpx.AsyncClient` with fixed event loop fixtures |
| Inconsistent fixtures between environments    | Normalize using TestGuardianAgent fixture regeneration |
| Coverage drops undetected                     | Enforce coverage thresholds in CI                      |
| Frontend test flakiness on CI                 | Use headless mode + deterministic seeds                |

---

## 8) Links

* [`docs/PLAYBOOKS_OVERVIEW.md`](../PLAYBOOKS_OVERVIEW.md)
* [`pytest.ini`](../../pytest.ini)
* [`scripts/regenerate_fixtures.py`](../../scripts/regenerate_fixtures.py)
* [`backend/tests/`](../../backend/tests/)
* [`client/tests/`](../../client/tests/)

---

## ✅ Next Actions

1. Finalize deterministic fixture setup (M1).
2. Implement frontend smoke tests (M2).
3. Add coverage + smoke gates to GitHub Actions (M3–M4).
4. Deliver QA summary before MVP Launch (M5).
