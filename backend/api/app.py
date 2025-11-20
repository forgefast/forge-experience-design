"""
FastAPI Application - ForgeExperienceDesign
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .routes import fixes

def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="ForgeExperienceDesign API",
        description="Ferramenta de correção automática de UI/UX",
        version="0.2.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(fixes.router)
    
    # Servir fix-injector.js como arquivo estático
    # Em produção, servir via CDN ou servidor web
    if os.path.exists("frontend/public/fix-injector.js"):
        app.mount("/static", StaticFiles(directory="frontend/public"), name="static")
    
    return app

