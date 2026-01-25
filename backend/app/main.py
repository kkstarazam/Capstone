"""FastAPI application entry point for Weather Intelligence Agent."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .config import settings


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    AI-powered Weather Intelligence Agent API.

    This API provides:
    - Natural language weather queries via an intelligent agent
    - Current weather conditions and forecasts
    - Location geocoding and reverse geocoding
    - Calendar integration for weather-aware scheduling
    - Personalized recommendations based on user preferences

    The agent uses Letta for stateful conversations with long-term memory,
    remembering user preferences, favorite locations, and activity patterns.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Configure CORS for mobile app access
# In production, set CORS_ORIGINS env var to specific allowed origins
cors_origins = settings.cors_origins_list if settings.cors_origins_list else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=len(cors_origins) > 0 and cors_origins[0] != "*",  # Only with specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)


# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "AI-powered Weather Intelligence Agent",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
