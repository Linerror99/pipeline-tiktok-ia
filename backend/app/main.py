from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import videos, auth, websocket

# Créer l'application FastAPI
app = FastAPI(
    title="Pipeline Vidéo IA API V2",
    description="API pour la génération automatique de vidéos TikTok/Shorts avec IA (Veo 3.1)",
    version="2.1.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """Endpoint racine pour vérifier que l'API est en ligne"""
    return {
        "message": "Pipeline Vidéo IA API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "service": "pipeline-video-ia-api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
