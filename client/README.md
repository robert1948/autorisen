## Frontend dependency locking

The frontend (`client/`) intentionally tracks `package-lock.json`
to guarantee reproducible installs in CI and Docker builds.

Do not delete or regenerate the lockfile unless explicitly instructed.
