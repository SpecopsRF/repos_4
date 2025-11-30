"""
Health check эндпоинты.

Используются для:
- Kubernetes liveness/readiness probes
- Мониторинга состояния приложения
- Балансировщиков нагрузки
"""

from fastapi import APIRouter
from datetime import datetime
from app.core.config import get_settings

router = APIRouter(tags=["Системные"])

settings = get_settings()


@router.get(
    "/health",
    summary="Проверка здоровья",
    description="Возвращает статус работоспособности приложения"
)
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Используется Kubernetes для проверки что приложение живо.
    Если возвращает 200 OK — приложение работает.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "app_name": settings.app_name,
        "version": settings.app_version
    }


@router.get(
    "/ready",
    summary="Готовность к работе",
    description="Проверяет готовность приложения принимать трафик"
)
async def readiness_check() -> dict:
    """
    Readiness check endpoint.
    
    Используется Kubernetes для проверки что приложение
    готово принимать запросы.
    """
    # Здесь можно добавить проверки:
    # - Подключение к базе данных
    # - Доступность внешних сервисов
    # - Достаточно ли памяти
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "api": "ok",
            "config": "ok"
        }
    }


@router.get(
    "/",
    summary="Главная страница",
    description="Информация о приложении"
)
async def root() -> dict:
    """Главная страница API."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "description": "API для отслеживания курсов криптовалют",
        "docs": "/docs",
        "endpoints": {
            "prices": "/crypto/prices",
            "convert": "/crypto/convert",
            "calculate": "/crypto/calculate",
            "health": "/health"
        }
    }
