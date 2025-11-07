# CapeControl Production Process Configuration
web: PYTHONPATH=backend gunicorn app.main:app -k uvicorn.workers.UvicornWorker
release: alembic -c backend/alembic.ini upgrade head

