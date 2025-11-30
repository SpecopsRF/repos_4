"""
Crypto Tracker - Главный файл приложения.

Это точка входа в приложение. Здесь:
1. Создаётся FastAPI приложение
2. Подключаются роутеры (эндпоинты)
3. Настраивается логирование
4. Добавляется middleware
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.core.config import get_settings
from app.api.crypto_routes import router as crypto_router
from app.api.health_routes import router as health_router

# Получаем настройки
settings = get_settings()

# Настраиваем логирование
logger.remove()  # Удаляем стандартный handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
           "<level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO",
    colorize=True
)

# Создаём приложение FastAPI
app = FastAPI(
    title=settings.app_name,
    description="""
    ## Crypto Tracker API 🚀
    
    API для отслеживания курсов криптовалют в реальном времени.
    
    ### Возможности:
    
    * 📊 **Курсы** — текущие цены топ-10 криптовалют
    * 💱 **Конвертер** — конвертация криптовалют в фиатные деньги
    * 🧮 **Калькулятор** — расчёт сколько крипты можно купить
    
    ### Поддерживаемые криптовалюты:
    
    Bitcoin, Ethereum, Tether, BNB, Solana, XRP, Cardano, Dogecoin, Polkadot, Polygon
    
    ### Поддерживаемые валюты:
    
    USD, EUR, RUB, GBP, JPY, CNY
    """,
    version=settings.app_version,
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc (альтернативная документация)
    openapi_url="/openapi.json"
)

# Добавляем CORS middleware
# Это позволяет обращаться к API из браузера с других доменов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(health_router)   # /, /health, /ready
app.include_router(crypto_router)   # /crypto/*

# Событие при запуске приложения
@app.on_event("startup")
async def startup_event():
    """Выполняется при старте приложения."""
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"📊 Tracking {len(settings.tracked_cryptos)} cryptocurrencies")
    logger.info(f"💱 Supporting {len(settings.supported_currencies)} fiat currencies")
    logger.info(f"📝 API docs available at /docs")


# Событие при остановке приложения
@app.on_event("shutdown")
async def shutdown_event():
    """Выполняется при остановке приложения."""
    logger.info(f"👋 Shutting down {settings.app_name}")


# Для локального запуска через: python app/main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
