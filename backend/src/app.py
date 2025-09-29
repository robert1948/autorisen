from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import textwrap
import os

app = FastAPI(title="Autorisen API", version="0.0.1")
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory="backend/src/static"), name="static")


@app.get("/api/health")
def health():
    return {"status": "ok", "env": os.getenv("APP_ENV", "development")}


@app.get("/alive")
def alive():
    """Lightweight health endpoint used by CI smoke tests."""
    return {"alive": True}


@app.get("/")
def root():
    """Simple root route so platform-level health checks (/) return 200."""
    html = textwrap.dedent(
        """\
        <!doctype html>
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width,initial-scale=1">
                <title>Autorisen</title>
                <link rel="icon" href="/favicon.ico" type="image/x-icon">
                <style>
                    body { font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; padding: 24px; background:#111; color:#eee }
                    pre { background:#000; color:#fff; padding:12px; border-radius:6px; }
                    .container { max-width:900px; margin:48px auto }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Autorisen</h1>
                    <p>Minimal landing page. API is available under <code>/api/</code>.</p>
                    <h2>Health</h2>
                    <pre>{"ok":true}</pre>
                </div>
            </body>
        </html>
        """
    )
    return HTMLResponse(content=html, status_code=200)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Serve the site favicon for browsers and uptime monitors."""
    return FileResponse("backend/src/static/favicon.ico")
