from datetime import datetime

from fastapi import FastAPI

app = FastAPI()


@app.get("/alive")
def alive():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}


@app.get("/ping")
def ping():
    return {"status": "pong", "ts": datetime.utcnow().isoformat()}
