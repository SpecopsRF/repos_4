"""API endpoints."""

from app.api.crypto_routes import router as crypto_router
from app.api.health_routes import router as health_router

__all__ = ["crypto_router", "health_router"]
