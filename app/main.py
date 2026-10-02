"""
main.py
FastAPI application entry point for ComicCraft.
Configures middleware, static files, template engine, and mounts all routes.
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.routes import router
from app.config import STATIC_DIR, PANELS_DIR, EXPORTS_DIR, TEMPLATES_DIR

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ensure required directories exist
# ---------------------------------------------------------------------------

for directory in [STATIC_DIR, PANELS_DIR, EXPORTS_DIR, TEMPLATES_DIR]:
    Path(directory).mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ComicCraft — AI Comic Story Creator",
    description=(
        "Generate personalized comic book stories and illustrations using "
        "Google Gemini AI models and Stable Diffusion. "
        "Input your story prompt, character, setting, tone, and art style — "
        "ComicCraft does the rest!"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "ComicCraft AI",
        "url": "http://127.0.0.1:8000",
    },
    license_info={
        "name": "MIT",
    },
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

# CORS — allow all origins for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

app.include_router(router)

# ---------------------------------------------------------------------------
# Application events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup():
    logger.info("=" * 60)
    logger.info("ComicCraft AI — Starting up")
    logger.info("  Homepage:   http://127.0.0.1:8000")
    logger.info("  API Docs:   http://127.0.0.1:8000/docs")
    logger.info("  ReDoc:      http://127.0.0.1:8000/redoc")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("ComicCraft AI — Shutting down.")
