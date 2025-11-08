# CapeControl Production Process Configuration
# Optimized for production deployment with proper worker configuration

web: bash -lc "gunicorn backend.src.app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-2} --worker-tmp-dir /dev/shm"
release: python -m alembic -c backend/alembic.ini upgrade head
