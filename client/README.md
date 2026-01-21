## Frontend dependency locking

The frontend (`client/`) intentionally tracks `package-lock.json`
to guarantee reproducible installs in CI and Docker builds.

Do not delete or regenerate the lockfile unless explicitly instructed.

## Frontend versioning (deploy traceability)

The UI version shown in the footer comes from `client/package.json` → `version`.

Before any Heroku deploy, bump `client/package.json` `version` so the release is traceable.
