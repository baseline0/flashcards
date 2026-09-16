from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from ..core.config import settings
from ..core.database import init_db
from .routes import api

app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()


# Include API routes
app.include_router(api.router, prefix="/api", tags=["api"])


@app.get("/")
def root():
    """Serve landing page."""
    docs_path = Path(__file__).parent.parent.parent.parent / "docs" / "index.html"
    return FileResponse(docs_path)


@app.get("/study")
def study():
    """Serve interactive study interface."""
    docs_path = Path(__file__).parent.parent.parent.parent / "docs" / "study.html"
    return FileResponse(docs_path)


# Serve static files (docs)
docs_dir = Path(__file__).parent.parent.parent.parent / "docs"
app.mount("/static", StaticFiles(directory=docs_dir), name="static")
