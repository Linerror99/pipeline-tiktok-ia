"""Reetik V3 — FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import settings
from .routers import auth, projects, characters, scenarios, videos, tiktok, websocket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Reetik API V3",
    description="Pipeline IA de production vidéo TikTok/Shorts — V3",
    version="3.0.0",
    docs_url="/api/v3/docs",
    redoc_url="/api/v3/redoc",
    openapi_url="/api/v3/openapi.json",
    redirect_slashes=False,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(characters.router)
app.include_router(scenarios.router)
app.include_router(videos.router)
app.include_router(tiktok.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    return {
        "app": "Reetik V3",
        "version": "3.0.0",
        "status": "running",
        "docs": "/api/v3/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}
