"""
Тесты для Pydantic моделей.

Проверяем что модели правильно валидируют данные.
"""

import pytest
from pydantic import ValidationError

from app.models.crypto import (
    CryptoPrice,
    ConversionRequest,
    CryptoCalculatorRequest,
)


class TestCryptoPriceModel:
    """Тесты модели CryptoPrice."""
    
    def test_valid_crypto_price(self):
        """Тест: создание валидной модели."""
        price = CryptoPrice(
            id="bitcoin",
            symbol="btc",
            name="Bitcoin",
            current_price=45000.50,
            currency="usd"
        )
        
        assert price.id == "bitcoin"
        assert price.symbol == "btc"
        assert price.current_price == 45000.50
    
    def test_crypto_price_with_optional_fields(self):
        """Тест: модель с опциональными полями."""
        price = CryptoPrice(
            id="ethereum",
            symbol="eth",
            name="Ethereum",
            current_price=2500.00,
            currency="usd",
            price_change_24h=50.25,
            price_change_percentage_24h=2.05,
            market_cap=300000000000
        )
        
        assert price.price_change_24h == 50.25
        assert price.market_cap == 300000000000


class TestConversionRequestModel:
    """Тесты модели ConversionRequest."""
    
    def test_valid_conversion_request(self):
        """Тест: валидный запрос конвертации."""
        request = ConversionRequest(
            from_crypto="bitcoin",
            to_currency="usd",
            amount=1.5
        )
        
        assert request.from_crypto == "bitcoin"
        assert request.amount == 1.5
    
    def test_invalid_amount_zero(self):
        """Тест: amount = 0 должен быть отклонён."""
        with pytest.raises(ValidationError):
            ConversionRequest(
                from_crypto="bitcoin",
                to_currency="usd",
                amount=0  # Должно быть > 0
            )
    
    def test_invalid_amount_negative(self):
        """Тест: отрицательный amount должен быть отклонён."""
        with pytest.raises(ValidationError):
            ConversionRequest(
                from_crypto="bitcoin",
                to_currency="usd",
                amount=-10.0
            )


class TestCalculatorRequestModel:
    """Тесты модели CryptoCalculatorRequest."""
    
    def test_valid_calculator_request(self):
        """Тест: валидный запрос калькулятора."""
        request = CryptoCalculatorRequest(
            crypto_id="ethereum",
            fiat_currency="eur",
            fiat_amount=1000.0
        )
        
        assert request.crypto_id == "ethereum"
        assert request.fiat_amount == 1000.0
    
    def test_invalid_fiat_amount(self):
        """Тест: fiat_amount должен быть > 0."""
        with pytest.raises(ValidationError):
            CryptoCalculatorRequest(
                crypto_id="bitcoin",
                fiat_currency="usd",
                fiat_amount=-500.0
            )
