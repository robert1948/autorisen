# CapeControl Production Process Configuration
# Optimized for production deployment with proper worker configuration

web: bash -lc "gunicorn backend.src.app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-2} --worker-tmp-dir /dev/shm"
worker: bash -lc "python -m backend.src.worker.email_worker"
release: bash -lc "echo '🛑 Release phase migrations are DISABLED by policy. Run explicit migrations via: make heroku-run-migrate HEROKU_APP_NAME=<app>'"
