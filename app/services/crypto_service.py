"""
Сервис для работы с криптовалютами.

Этот модуль отвечает за:
1. Получение курсов криптовалют с внешнего API (CoinGecko)
2. Кэширование данных для снижения нагрузки
3. Конвертацию между криптовалютами и фиатными валютами
"""

import httpx
from datetime import datetime
from typing import Optional
from cachetools import TTLCache
from loguru import logger

from app.core.config import get_settings
from app.models.crypto import (
    CryptoPrice,
    CryptoList,
    ConversionResult,
    CryptoCalculatorResult,
)

# Получаем настройки
settings = get_settings()

# Создаём кэш с временем жизни (TTL = Time To Live)
# maxsize=100 - максимум 100 записей в кэше
# ttl=60 - каждая запись живёт 60 секунд
price_cache: TTLCache = TTLCache(maxsize=100, ttl=settings.cache_ttl)


class CryptoService:
    """
    Сервис для работы с криптовалютами.
    
    Использует CoinGecko API (бесплатный, без ключа).
    Документация: https://www.coingecko.com/en/api/documentation
    """
    
    def __init__(self):
        """Инициализация сервиса."""
        self.base_url = settings.coingecko_api_url
        self.tracked_cryptos = settings.tracked_cryptos
        self.supported_currencies = settings.supported_currencies
        
        logger.info(f"CryptoService initialized. Tracking: {self.tracked_cryptos}")
    
    async def get_prices(self, currency: str = "usd") -> CryptoList:
        """
        Получить цены всех отслеживаемых криптовалют.
        
        Args:
            currency: Валюта для цен (usd, eur, rub и т.д.)
            
        Returns:
            CryptoList: Список криптовалют с ценами
        """
        # Проверяем валюту
        currency = currency.lower()
        if currency not in self.supported_currencies:
            logger.warning(f"Unsupported currency: {currency}, using usd")
            currency = "usd"
        
        # Ключ для кэша
        cache_key = f"prices_{currency}"
        
        # Проверяем кэш
        if cache_key in price_cache:
            logger.debug(f"Cache hit for {cache_key}")
            cached_data = price_cache[cache_key]
            cached_data.cached = True
            return cached_data
        
        logger.info(f"Fetching prices from CoinGecko API for {currency}")
        
        # Формируем запрос к API
        # Документация: https://www.coingecko.com/api/documentation
        url = f"{self.base_url}/coins/markets"
        params = {
            "vs_currency": currency,
            "ids": ",".join(self.tracked_cryptos),
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h"
        }
        
        try:
            # Асинхронный HTTP-запрос
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()  # Выбросит исключение если статус != 200
                
                data = response.json()
                logger.debug(f"Received {len(data)} cryptocurrencies")
        
        except httpx.TimeoutException:
            logger.error("CoinGecko API timeout")
            raise Exception("External API timeout. Please try again.")
        
        except httpx.HTTPStatusError as e:
            logger.error(f"CoinGecko API error: {e.response.status_code}")
            raise Exception(f"External API error: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise Exception("Failed to fetch cryptocurrency data")
        
        # Преобразуем ответ API в наши модели
        crypto_prices = []
        for coin in data:
            crypto_price = CryptoPrice(
                id=coin["id"],
                symbol=coin["symbol"],
                name=coin["name"],
                current_price=coin["current_price"],
                currency=currency,
                price_change_24h=coin.get("price_change_24h"),
                price_change_percentage_24h=coin.get("price_change_percentage_24h"),
                market_cap=coin.get("market_cap"),
                last_updated=datetime.fromisoformat(
                    coin["last_updated"].replace("Z", "+00:00")
                ) if coin.get("last_updated") else None
            )
            crypto_prices.append(crypto_price)
        
        # Создаём результат
        result = CryptoList(
            count=len(crypto_prices),
            currency=currency,
            data=crypto_prices,
            cached=False,
            updated_at=datetime.utcnow()
        )
        
        # Сохраняем в кэш
        price_cache[cache_key] = result
        logger.info(f"Cached {len(crypto_prices)} prices for {currency}")
        
        return result
    
    async def get_single_price(self, crypto_id: str, currency: str = "usd") -> Optional[CryptoPrice]:
        """
        Получить цену одной криптовалюты.
        
        Args:
            crypto_id: ID криптовалюты (bitcoin, ethereum и т.д.)
            currency: Валюта для цены
            
        Returns:
            CryptoPrice или None если не найдено
        """
        # Получаем все цены (они кэшируются)
        all_prices = await self.get_prices(currency)
        
        # Ищем нужную криптовалюту
        for crypto in all_prices.data:
            if crypto.id == crypto_id.lower():
                return crypto
        
        logger.warning(f"Cryptocurrency not found: {crypto_id}")
        return None
    
    async def convert(
        self, 
        from_crypto: str, 
        to_currency: str, 
        amount: float
    ) -> ConversionResult:
        """
        Конвертировать криптовалюту в фиатную валюту.
        
        Пример: 0.5 BTC → USD
        
        Args:
            from_crypto: ID криптовалюты (bitcoin, ethereum)
            to_currency: Целевая валюта (usd, eur, rub)
            amount: Количество криптовалюты
            
        Returns:
            ConversionResult: Результат конвертации
        """
        logger.info(f"Converting {amount} {from_crypto} to {to_currency}")
        
        # Получаем текущую цену
        crypto = await self.get_single_price(from_crypto, to_currency)
        
        if not crypto:
            raise ValueError(f"Cryptocurrency '{from_crypto}' not found or not supported")
        
        # Вычисляем результат
        result_amount = amount * crypto.current_price
        
        return ConversionResult(
            from_crypto=from_crypto,
            from_amount=amount,
            to_currency=to_currency,
            to_amount=round(result_amount, 2),
            rate=crypto.current_price,
            timestamp=datetime.utcnow()
        )
    
    async def calculate(
        self,
        crypto_id: str,
        fiat_currency: str,
        fiat_amount: float
    ) -> CryptoCalculatorResult:
        """
        Рассчитать сколько криптовалюты можно купить за сумму.
        
        Пример: сколько BTC за 1000 USD?
        
        Args:
            crypto_id: ID криптовалюты
            fiat_currency: Фиатная валюта
            fiat_amount: Сумма в фиате
            
        Returns:
            CryptoCalculatorResult: Результат расчёта
        """
        logger.info(f"Calculating how much {crypto_id} for {fiat_amount} {fiat_currency}")
        
        # Получаем текущую цену
        crypto = await self.get_single_price(crypto_id, fiat_currency)
        
        if not crypto:
            raise ValueError(f"Cryptocurrency '{crypto_id}' not found or not supported")
        
        # Вычисляем сколько крипты можно купить
        crypto_amount = fiat_amount / crypto.current_price
        
        return CryptoCalculatorResult(
            crypto_id=crypto.id,
            crypto_name=crypto.name,
            crypto_symbol=crypto.symbol,
            fiat_currency=fiat_currency,
            fiat_amount=fiat_amount,
            crypto_amount=round(crypto_amount, 8),  # 8 знаков после запятой
            rate=crypto.current_price,
            timestamp=datetime.utcnow()
        )
    
    def get_supported_cryptos(self) -> list[str]:
        """Получить список поддерживаемых криптовалют."""
        return self.tracked_cryptos
    
    def get_supported_currencies(self) -> list[str]:
        """Получить список поддерживаемых фиатных валют."""
        return self.supported_currencies


# Создаём глобальный экземпляр сервиса (Singleton)
crypto_service = CryptoService()


def get_crypto_service() -> CryptoService:
    """
    Получить экземпляр сервиса.
    
    Используется для dependency injection в FastAPI.
    """
    return crypto_service
