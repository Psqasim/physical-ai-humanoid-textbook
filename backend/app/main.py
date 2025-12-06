"""
FastAPI application entry point for RAG Study Assistant.

This module creates and configures the FastAPI application instance,
sets up CORS middleware, and includes API routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import health


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Physical AI Study Assistant API",
        description="RAG-powered backend for Physical AI & Humanoid Robotics textbook",
        version="0.1.0",
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api", tags=["health"])

    return app


# Create application instance
app = create_app()


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint to verify the API is running.

    Returns:
        Basic API information and status
    """
    return {
        "message": "Physical AI Study Assistant API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }
