
# Act as my Senior DevOps & Project Lead

## Objective

Audit our current platform posture, freeze unnecessary cloud work, prevent scope creep, align secrets, control costs, and update the delivery plan.

## What to Check & Do

1. **Platform in use (Heroku vs AWS)**

   * Verify whether **Heroku** (app: `autorisen`) is the active runtime.
   * Note last deploy, current dynos, add-ons, config vars, and health endpoints.

1. **AWS status — put on hold**

   * Assess the state of our AWS footprint (ECS/ALB/RDS/SSM/etc.).
   * Recommend steps to **pause/hold** AWS safely (retain IaC, stop spend, keep minimal artifacts).

1. **Scope guardrails**

   * Call out scope creep risk (ECS + ALB + RDS can balloon).
   * For a first pass, propose a **minimal ECS footprint: “cluster + single task only,” no ALB/RDS**.
   * Define explicit “not now” items.

1. **Secrets: single source of truth**

   * Identify **secret drift** between **Heroku config vars** and **AWS SSM Parameters**.
   * Propose and document **one SSOT** and a one-way sync policy (mapping + rotation).

1. **Cost controls**

   * Highlight risk of **idle ECS costs**.
   * Recommend **Fargate Spot** for dev and **scale-to-0** patterns when not testing.

[...existing code...]

## Senior DevOps — autorisen

Snapshot: 2025-09-26

Purpose
* Operational and emergency playbook for CI/infra tasks: validate OIDC, run secrets sync, run the live audit, and prepare the minimal ECS migration skeleton.

Quick status
* GitHub is the short-term SSOT for secrets.
* OIDC provider exists in AWS; `gh-oidc-autorisen-ecr` role exists (ARN: arn:aws:iam::381492223887:role/gh-oidc-autorisen-ecr).
* Safe-sync tooling: `infra/secrets-mapping.json` and `infra/scripts/sync_github_to_heroku.sh` (dry-run default).
* Manual test workflow for OIDC added on feature branch; PR #7 created to merge it into `main`.

Core contracts
* Inputs:
  * Repo secrets (GitHub): `HEROKU_API_KEY`, `HEROKU_APP_NAME`, `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `AWS_OIDC_ROLE`, `AWS_REGION` (as relevant).
* Outputs:
  * Audit artifact (`live-audit-output.zip`) produced by `live-audit.yml`.
  * Heroku config-vars updated (only after controlled `--apply` run).
* Error modes:
  * Missing secrets → dry-run only, no writes.
  * OIDC assume-role failure → role/trust policy misconfig.

Key files (what to look at)
* `.github/workflows/ci-health.yml` — builds `services/health`, runs smoke test.
* `.github/workflows/docker-publish.yml` — DockerHub publish pipeline.
* `.github/workflows/test-oidc-assume-role.yml` — manual OIDC assume-role test (PR #7).
* `.github/workflows/live-audit.yml` — manual live audit workflow (runs Heroku + AWS queries).
* `infra/secrets-mapping.json` — mapping GitHub secrets => Heroku config-vars.
* `infra/scripts/sync_github_to_heroku.sh` — safe sync script (dry-run default).
* `infra/aws-ecs-skel/trust-policy.json` — OIDC trust policy for role creation.

How to validate OIDC (short)

1. Merge PR #7 (adds the `test-oidc-assume-role.yml` workflow to `main`).
1. On `main`, go to Actions → run `Test OIDC Assume Role` (workflow_dispatch).
1. Inspect logs: the job should run `aws sts get-caller-identity` after `assume-role` and show an ARN for the role/session. Successful output indicates OIDC assume-role is working.

How to run the secrets sync (recommended safe flow)

1. Create a workflow `ci/sync-github-to-heroku.yml` that runs `infra/scripts/sync_github_to_heroku.sh` in dry-run mode (default).
1. Dispatch the dry-run workflow, review output/artifacts for mapping and missing keys.
1. If the dry-run is good, re-run the workflow with an approval step and an environment variable/flag to pass `--apply` to the script (explicit, auditable run).
1. Audit the Heroku app’s config-vars after the apply (`heroku config --app $HEROKU_APP_NAME`).

Local developer hints (don’t use for writes unless you know what you’re doing)
* Dry-run locally:
  * Ensure you DO NOT have mapped secrets in your shell — local runs default to dry-run and will show missing keys.
  * Run: infra/scripts/sync_github_to_heroku.sh
* Apply locally (not recommended; prefer Actions-run):
  * infra/scripts/sync_github_to_heroku.sh --apply

Essential commands (examples)
* Validate role:
  * aws iam get-role --role-name gh-oidc-autorisen-ecr --query 'Role.Arn' --output text

* Dry-run sync (Actions preferred):

* # From Actions run: infra/scripts/sync_github_to_heroku.sh

* Run Test OIDC (from Actions UI after PR merged):
  * dispatch `Test OIDC Assume Role` workflow on `main`.

Production readiness checklist (ops)
* OIDC test passes on `main`.
* Secrets sync dry-run completed and reviewed.
* Secrets sync `--apply` run passed with audit log.
* `live-audit.yml` run produces `live-audit-output` artifact.
* Deliverables A–E produced and published to stakeholders.

Contact / Maintainers
* Ops: <ops@example.com>
* Infra: <infra@example.com>
* Security: <security@example.com>
| -------------------- | -------------- | --------------------------- | ----------------------------------------------------------------------- | ----------------------------------------- |
| `DOCKERHUB_USERNAME` | GitHub Secrets | Heroku `DOCKERHUB_USERNAME` | One-way: GitHub → Heroku via `sync_github_to_heroku.sh` (dry run first) | [ops@example.com](mailto:ops@example.com) |
| `DOCKERHUB_TOKEN`    | GitHub Secrets | Heroku `DOCKERHUB_TOKEN`    | One-way: GitHub → Heroku                                                | [ops@example.com](mailto:ops@example.com) |
| `AWS_OIDC_ROLE`      | GitHub Secrets | AWS IAM role ARN (Actions)  | Manually created; store ARN in GitHub                                   | [ops@example.com](mailto:ops@example.com) |

> Next step: run sync with `--apply` from Actions (preferred) or locally after exporting secrets.

### D. Cost Mitigations

* **Immediate:** Stop/hold any running AWS test resources. Use Heroku for active testing until migration is ready.
* **Near-term:** Limit AWS work to skeletons (ECR + cluster). Use low-cost patterns (Fargate Spot) for dev.
* **Operational:** Add alerts for unplanned AWS spend and a daily cost report for resources tagged `project=autorisen`.

### E. 7-Day Action Plan (owner & date)

#### Day 0 (today)

* Merge PR **#7** to `main` (owner: repo admin) to enable OIDC test.

#### Day 1

* Dispatch **Test OIDC Assume Role** workflow and confirm `aws sts get-caller-identity` (owner: ops).
* Run `infra/scripts/sync_github_to_heroku.sh` in a workflow (dry run) and review planned writes (owner: ops).

#### Day 2

* If dry run is correct, run `--apply` in a controlled Action to push required Heroku config vars (owner: ops).

#### Day 3–7

* Run **Live Audit – Heroku & AWS (manual)** workflow; collect `live-audit-output` artifact; produce Deliverables **A–E** with live data (owners: ops + project lead).
* Finalize migration plan for ECS (minimal: cluster + single task) with cost estimates and a rollback plan (owner: infra lead).

## Notes, Assumptions & Checks

* **Assumption:** Repo secrets listed are current and accessible to Actions; update if not.
* **Assumption:** IAM role `gh-oidc-autorisen-ecr` has the trust policy in `trust-policy.json`.
* **Verify:** Heroku add-ons and last deploy info via Heroku API key; the audit workflow will collect this.

## Constraints & Style

* Optimize for **speed and clarity**; prioritize **Heroku** for staging until further notice.
* Keep AWS changes minimal and **reversible**.
* Be **decisive**: where data is missing, state assumptions, proceed, and list what to verify.

## Output Format

Use the headings above (**A–E**). Keep it concise, action-oriented, and ready to paste into our docs.
