from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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
    """Root endpoint."""
    return {"message": "Flashcards API", "docs": "/docs"}
