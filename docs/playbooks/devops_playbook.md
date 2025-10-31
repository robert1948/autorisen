# DevOps Playbook

- **Goal:** Ensure reliable delivery pipelines, secure infrastructure, and responsive incident handling.
- **Scope:** CI/CD workflows, environment management, infrastructure-as-code, monitoring, and on-call.

## Cadence

- Daily review of pipeline health dashboards.
- Weekly patching window for dependencies and base images.
- Monthly disaster recovery drill with documented learnings.

## Checklist

- Keep `Dockerfile` and `docker-compose.yml` aligned with production configuration.
- Validate migrations locally and in staging before deployment.
- Monitor Heroku release logs (`make heroku-smoke-staging`) after each deploy.
- Maintain environment secrets in the designated secrets manager.
- Update runbooks with any new incident or infrastructure change.

## Tooling

- GitHub Actions for CI (tests, lint, builds).
- Heroku pipelines for staging and production deploys.
- Sentry/Loki (planned) for logging and alerting.
- PagerDuty / Opsgenie for incident escalation.

## Owners

- **Primary:** DevOps engineer.
- **Support:** Backend lead, Security officer, On-call rotation.
