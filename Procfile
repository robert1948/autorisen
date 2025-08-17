web: uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --access-log --log-level info
release: python migrate_production_simple.pyeb: uvicorn app.main:app --host=0.0.0.0 --port=$PORT
