"""
API эндпоинты для работы с криптовалютами.

Этот модуль содержит все HTTP-эндпоинты для:
- Получения курсов криптовалют
- Конвертации валют
- Калькулятора
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from loguru import logger

from app.services.crypto_service import CryptoService, get_crypto_service
from app.models.crypto import (
    CryptoList,
    CryptoPrice,
    ConversionRequest,
    ConversionResult,
    CryptoCalculatorRequest,
    CryptoCalculatorResult,
)

# Создаём роутер с префиксом /crypto
# Все эндпоинты будут начинаться с /crypto
router = APIRouter(
    prefix="/crypto",
    tags=["Криптовалюты"],  # Группировка в Swagger UI
    responses={
        404: {"description": "Не найдено"},
        500: {"description": "Внутренняя ошибка сервера"}
    }
)


@router.get(
    "/prices",
    response_model=CryptoList,
    summary="Получить курсы всех криптовалют",
    description="Возвращает текущие курсы топ-10 криптовалют в выбранной валюте"
)
async def get_prices(
    currency: str = Query(
        default="usd",
        description="Валюта для отображения цен (usd, eur, rub, gbp, jpy, cny)",
        example="usd"
    ),
    service: CryptoService = Depends(get_crypto_service)
) -> CryptoList:
    """
    Получить текущие курсы всех отслеживаемых криптовалют.
    
    - **currency**: Валюта для цен (по умолчанию USD)
    
    Возвращает список из 10 криптовалют с текущими ценами,
    изменением за 24 часа и рыночной капитализацией.
    """
    try:
        logger.info(f"API: Getting prices in {currency}")
        return await service.get_prices(currency)
    
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch prices: {str(e)}"
        )


@router.get(
    "/prices/{crypto_id}",
    response_model=CryptoPrice,
    summary="Получить курс одной криптовалюты",
    description="Возвращает текущий курс конкретной криптовалюты"
)
async def get_single_price(
    crypto_id: str,
    currency: str = Query(default="usd", description="Валюта для цены"),
    service: CryptoService = Depends(get_crypto_service)
) -> CryptoPrice:
    """
    Получить текущий курс одной криптовалюты.
    
    - **crypto_id**: ID криптовалюты (bitcoin, ethereum, solana и т.д.)
    - **currency**: Валюта для цены
    """
    try:
        logger.info(f"API: Getting price for {crypto_id} in {currency}")
        result = await service.get_single_price(crypto_id, currency)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Cryptocurrency '{crypto_id}' not found. "
                       f"Supported: {service.get_supported_cryptos()}"
            )
        
        return result
    
    except HTTPException:
        raise  # Пробрасываем HTTP исключения дальше
    
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/convert",
    response_model=ConversionResult,
    summary="Конвертировать криптовалюту",
    description="Конвертирует указанное количество криптовалюты в фиатную валюту"
)
async def convert_crypto(
    request: ConversionRequest,
    service: CryptoService = Depends(get_crypto_service)
) -> ConversionResult:
    """
    Конвертировать криптовалюту в фиатную валюту.
    
    Пример: сколько USD за 0.5 Bitcoin?
    
    - **from_crypto**: Из какой криптовалюты (bitcoin, ethereum...)
    - **to_currency**: В какую валюту (usd, eur, rub...)
    - **amount**: Количество криптовалюты
    """
    try:
        logger.info(
            f"API: Converting {request.amount} {request.from_crypto} "
            f"to {request.to_currency}"
        )
        return await service.convert(
            from_crypto=request.from_crypto,
            to_currency=request.to_currency,
            amount=request.amount
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/calculate",
    response_model=CryptoCalculatorResult,
    summary="Калькулятор: сколько крипты за сумму",
    description="Рассчитывает сколько криптовалюты можно купить за указанную сумму"
)
async def calculate_crypto(
    request: CryptoCalculatorRequest,
    service: CryptoService = Depends(get_crypto_service)
) -> CryptoCalculatorResult:
    """
    Рассчитать сколько криптовалюты можно купить.
    
    Пример: сколько Bitcoin можно купить за 1000 USD?
    
    - **crypto_id**: Какую криптовалюту купить
    - **fiat_currency**: За какую валюту
    - **fiat_amount**: Сумма денег
    """
    try:
        logger.info(
            f"API: Calculating {request.crypto_id} "
            f"for {request.fiat_amount} {request.fiat_currency}"
        )
        return await service.calculate(
            crypto_id=request.crypto_id,
            fiat_currency=request.fiat_currency,
            fiat_amount=request.fiat_amount
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/supported",
    summary="Список поддерживаемых валют",
    description="Возвращает списки поддерживаемых криптовалют и фиатных валют"
)
async def get_supported(
    service: CryptoService = Depends(get_crypto_service)
) -> dict:
    """
    Получить списки поддерживаемых валют.
    
    Возвращает:
    - Список криптовалют для отслеживания
    - Список фиатных валют для конвертации
    """
    return {
        "cryptocurrencies": service.get_supported_cryptos(),
        "fiat_currencies": service.get_supported_currencies()
    }
