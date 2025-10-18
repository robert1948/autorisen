web: PYTHONPATH=backend gunicorn app.main:app -k uvicorn.workers.UvicornWorker
# Procfile
release: alembic -c backend/alembic.ini upgrade head

