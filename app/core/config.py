"""
Конфигурация приложения.

Этот модуль содержит все настройки приложения.
Настройки загружаются из переменных окружения или используют значения по умолчанию.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Класс настроек приложения.
    
    Attributes:
        app_name: Название приложения
        app_version: Версия приложения
        debug: Режим отладки (True/False)
        api_host: Хост для запуска сервера
        api_port: Порт для запуска сервера
        
        coingecko_api_url: URL API CoinGecko (бесплатный API криптовалют)
        cache_ttl: Время жизни кэша в секундах
        
        supported_currencies: Поддерживаемые фиатные валюты
    """
    
    # Основные настройки приложения
    app_name: str = "Crypto Tracker"
    app_version: str = "1.0.0"
    debug: bool = False
    
     # Настройки сервера
    api_host: str = "0.0.0.0"  # nosec B104 - Required for Docker
    api_port: int = 8000
    
    # Настройки API криптовалют (используем бесплатный CoinGecko)
    coingecko_api_url: str = "https://api.coingecko.com/api/v3"
    
    # Настройки кэширования (чтобы не спамить внешний API)
    cache_ttl: int = 60  # секунд
    
    # Поддерживаемые валюты для конвертации
    supported_currencies: list = ["usd", "eur", "rub", "gbp", "jpy", "cny"]
    
    # Топ-10 криптовалют для отслеживания
    tracked_cryptos: list = [
        "bitcoin",
        "ethereum", 
        "tether",
        "binancecoin",
        "solana",
        "ripple",
        "cardano",
        "dogecoin",
        "polkadot",
        "polygon"
    ]
    
    class Config:
        """Конфигурация Pydantic."""
        env_file = ".env"  # Загружать переменные из файла .env


@lru_cache()
def get_settings() -> Settings:
    """
    Получить настройки приложения.
    
    Используем @lru_cache чтобы не создавать объект настроек
    каждый раз заново (singleton pattern).
    
    Returns:
        Settings: Объект с настройками
    """
    return Settings()
