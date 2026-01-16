#!/usr/bin/env python3
"""Script to run the Weather Intelligence Agent API server."""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.app_name}...")
    print(f"API docs available at: http://{settings.api_host}:{settings.api_port}/docs")

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
