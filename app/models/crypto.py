"""
Модели данных для криптовалют.

Pydantic модели используются для:
1. Валидации данных (проверка типов, ограничений)
2. Сериализации (преобразование в JSON и обратно)
3. Автоматической документации API (Swagger)
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CryptoPrice(BaseModel):
    """
    Модель цены одной криптовалюты.
    
    Attributes:
        id: Идентификатор криптовалюты (например, "bitcoin")
        symbol: Короткий символ (например, "btc")
        name: Полное название (например, "Bitcoin")
        current_price: Текущая цена в выбранной валюте
        currency: Валюта цены (usd, eur, rub и т.д.)
        price_change_24h: Изменение цены за 24 часа
        price_change_percentage_24h: Процент изменения за 24 часа
        market_cap: Рыночная капитализация
        last_updated: Время последнего обновления
    """
    
    id: str = Field(..., description="Идентификатор криптовалюты", example="bitcoin")
    symbol: str = Field(..., description="Символ криптовалюты", example="btc")
    name: str = Field(..., description="Название криптовалюты", example="Bitcoin")
    
    current_price: float = Field(..., description="Текущая цена", example=45000.50)
    currency: str = Field(default="usd", description="Валюта цены", example="usd")
    
    price_change_24h: Optional[float] = Field(
        default=None, 
        description="Изменение цены за 24ч",
        example=1250.30
    )
    price_change_percentage_24h: Optional[float] = Field(
        default=None,
        description="Процент изменения за 24ч",
        example=2.85
    )
    
    market_cap: Optional[float] = Field(
        default=None,
        description="Рыночная капитализация",
        example=850000000000
    )
    
    last_updated: Optional[datetime] = Field(
        default=None,
        description="Время последнего обновления"
    )

    class Config:
        """Конфигурация модели."""
        json_schema_extra = {
            "example": {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.50,
                "currency": "usd",
                "price_change_24h": 1250.30,
                "price_change_percentage_24h": 2.85,
                "market_cap": 850000000000,
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }


class CryptoList(BaseModel):
    """
    Список криптовалют с метаданными.
    
    Используется для ответа API со списком всех отслеживаемых криптовалют.
    """
    
    count: int = Field(..., description="Количество криптовалют в списке")
    currency: str = Field(..., description="Валюта цен")
    data: list[CryptoPrice] = Field(..., description="Список криптовалют")
    cached: bool = Field(default=False, description="Данные из кэша?")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversionRequest(BaseModel):
    """
    Запрос на конвертацию криптовалюты.
    
    Пример: сколько будет 0.5 BTC в USD?
    """
    
    from_crypto: str = Field(
        ..., 
        description="Из какой криптовалюты",
        example="bitcoin"
    )
    to_currency: str = Field(
        ..., 
        description="В какую валюту",
        example="usd"
    )
    amount: float = Field(
        ..., 
        gt=0,  # greater than 0 (больше нуля)
        description="Количество криптовалюты",
        example=0.5
    )


class ConversionResult(BaseModel):
    """
    Результат конвертации.
    """
    
    from_crypto: str = Field(..., description="Из криптовалюты")
    from_amount: float = Field(..., description="Исходное количество")
    
    to_currency: str = Field(..., description="В валюту")
    to_amount: float = Field(..., description="Результат конвертации")
    
    rate: float = Field(..., description="Курс конвертации")
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Время конвертации"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "from_crypto": "bitcoin",
                "from_amount": 0.5,
                "to_currency": "usd",
                "to_amount": 22500.25,
                "rate": 45000.50,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class CryptoCalculatorRequest(BaseModel):
    """
    Запрос калькулятора: сколько крипты можно купить за сумму?
    
    Пример: сколько BTC можно купить за 1000 USD?
    """
    
    crypto_id: str = Field(..., description="Какую криптовалюту", example="bitcoin")
    fiat_currency: str = Field(..., description="За какую валюту", example="usd")
    fiat_amount: float = Field(
        ..., 
        gt=0,
        description="Сумма в фиатной валюте",
        example=1000.0
    )


class CryptoCalculatorResult(BaseModel):
    """
    Результат калькулятора.
    """
    
    crypto_id: str
    crypto_name: str
    crypto_symbol: str
    
    fiat_currency: str
    fiat_amount: float
    
    crypto_amount: float = Field(..., description="Сколько крипты можно купить")
    rate: float = Field(..., description="Текущий курс")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
