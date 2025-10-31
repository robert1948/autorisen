# Onboarding Playbook

- **Goal:** Deliver a frictionless onboarding journey from invite to first successful automation run.
- **Scope:** Landing page messaging, account creation, CSRF/auth flows, welcome checklist, and onboarding nudges.

## Cadence

- Weekly funnel review using analytics dashboards.
- Bi-weekly usability testing with new customers.
- Monthly review of onboarding flows with Support and Sales.

## Checklist

- Verify signup, login, and CSRF protections in staging before release.
- Ensure onboarding checklist API returns required milestones.
- Update automated emails and in-app tips after major feature launches.
- Confirm telemetry events are sent for each onboarding step.
- Run regression tests (`make auth-tests`) during onboarding code changes.

## Tooling

- Mixpanel (or equivalent) for activation metrics.
- FastAPI backend for auth and onboarding APIs.
- React client for onboarding UI.
- Postmark (or SMTP) for transactional emails.

## Owners

- **Primary:** Growth PM.
- **Support:** Backend auth team, Frontend onboarding squad, Support lead.
