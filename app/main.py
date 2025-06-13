from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import API routers
from .api import articles
from .api import scan as scan_api

app = FastAPI(title="NewsQuant MVP")

# Allow CORS for local development / testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for static assets
static_dir = Path(__file__).parent / "static"

# Register API routes
app.include_router(articles.router, prefix="/articles")
app.include_router(scan_api.router)

# Mount static files on root (allows /main.js, /index.html etc.)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static_root")
