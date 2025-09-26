# Infra: Secrets sync helpers

This folder contains a mapping and helper scripts to safely sync repository GitHub Secrets to Heroku config vars.

Files added:

- `secrets-mapping.json` - mapping of secret names and target locations
- `scripts/sync_github_to_heroku.sh` - dry-run and apply script to push secrets to Heroku

Usage (dry-run):

```bash
cd infra
infra/scripts/sync_github_to_heroku.sh
```

Apply (writes to Heroku app):

```bash
export HEROKU_API_KEY=...    # set in environment securely
export HEROKU_APP_NAME=autorisen
cd infra
infra/scripts/sync_github_to_heroku.sh --apply
```

Notes:

- Scripts default to dry-run and will not write unless `--apply` is provided.
- The scripts expect secrets to be available as environment variables locally for safety. You can export them temporarily to test.
