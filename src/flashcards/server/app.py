from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from flashcards.constants import REPO_ROOT
from flashcards.core.config import settings
from flashcards.core.database import init_db

from .routes import api

app = FastAPI(title=settings.app_name, debug=settings.debug)

# The published site. GitHub Pages uploads this folder and nothing else (.github/workflows/deploy-pages.yml).
SITE_DIR = REPO_ROOT / "site"
# The study interface is served by this server only. It calls /api, which Pages does not provide.
STUDY_PAGE = REPO_ROOT / "src" / "flashcards" / "server" / "static" / "study.html"


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()


# Include API routes
app.include_router(api.router, prefix="/api", tags=["api"])


@app.get("/")
def root():
    """Serve landing page."""
    return FileResponse(SITE_DIR / "index.html")


@app.get("/study")
def study():
    """Serve interactive study interface."""
    return FileResponse(STUDY_PAGE)


# Serve static files (site)
app.mount("/static", StaticFiles(directory=SITE_DIR), name="static")
