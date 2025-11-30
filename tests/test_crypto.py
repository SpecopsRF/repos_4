"""
Тесты для криптовалютных эндпоинтов.

Эти тесты проверяют основную функциональность приложения:
- Получение курсов
- Конвертацию
- Калькулятор
"""

import pytest


class TestCryptoPrices:
    """Тесты получения курсов криптовалют."""
    
    @pytest.mark.integration
    def test_get_all_prices(self, client):
        """
        Тест: получение курсов всех криптовалют.
        
        Проверяем:
        - Статус 200
        - Есть список криптовалют
        - Количество >= 1
        """
        response = client.get("/crypto/prices")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "count" in data
        assert data["count"] >= 1
        assert data["count"] <= 10
        assert data["currency"] == "usd"
    
    @pytest.mark.integration
    def test_get_prices_in_eur(self, client):
        """Тест: получение курсов в евро."""
        response = client.get("/crypto/prices?currency=eur")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["currency"] == "eur"
    
    @pytest.mark.integration
    def test_get_prices_in_rub(self, client):
        """Тест: получение курсов в рублях."""
        response = client.get("/crypto/prices?currency=rub")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["currency"] == "rub"
    
    @pytest.mark.integration
    def test_get_single_price_bitcoin(self, client):
        """Тест: получение курса Bitcoin."""
        response = client.get("/crypto/prices/bitcoin")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "bitcoin"
        assert data["symbol"] == "btc"
        assert "current_price" in data
        assert data["current_price"] > 0
    
    @pytest.mark.integration
    def test_get_single_price_ethereum(self, client):
        """Тест: получение курса Ethereum."""
        response = client.get("/crypto/prices/ethereum")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "ethereum"
        assert data["symbol"] == "eth"
    
    def test_get_price_not_found(self, client):
        """Тест: несуществующая криптовалюта возвращает 404."""
        response = client.get("/crypto/prices/notexistingcoin")
        
        assert response.status_code == 404


class TestCryptoConversion:
    """Тесты конвертации криптовалют."""
    
    @pytest.mark.integration
    def test_convert_bitcoin_to_usd(self, client, sample_conversion_request):
        """
        Тест: конвертация Bitcoin в USD.
        
        Проверяем:
        - Статус 200
        - Результат > 0
        - Правильные поля в ответе
        """
        response = client.post("/crypto/convert", json=sample_conversion_request)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["from_crypto"] == "bitcoin"
        assert data["from_amount"] == 0.5
        assert data["to_currency"] == "usd"
        assert data["to_amount"] > 0
        assert data["rate"] > 0
    
    @pytest.mark.integration
    def test_convert_ethereum_to_eur(self, client):
        """Тест: конвертация Ethereum в EUR."""
        request = {
            "from_crypto": "ethereum",
            "to_currency": "eur",
            "amount": 2.0
        }
        
        response = client.post("/crypto/convert", json=request)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["from_crypto"] == "ethereum"
        assert data["to_currency"] == "eur"
    
    def test_convert_invalid_crypto(self, client):
        """Тест: конвертация несуществующей крипты возвращает 404."""
        request = {
            "from_crypto": "fakecoin",
            "to_currency": "usd",
            "amount": 1.0
        }
        
        response = client.post("/crypto/convert", json=request)
        
        assert response.status_code == 404
    
    def test_convert_invalid_amount(self, client):
        """Тест: отрицательная сумма возвращает ошибку."""
        request = {
            "from_crypto": "bitcoin",
            "to_currency": "usd",
            "amount": -1.0
        }
        
        response = client.post("/crypto/convert", json=request)
        
        assert response.status_code == 422


class TestCryptoCalculator:
    """Тесты калькулятора криптовалют."""
    
    @pytest.mark.integration
    def test_calculate_bitcoin_for_usd(self, client, sample_calculator_request):
        """
        Тест: сколько Bitcoin можно купить за 1000 USD.
        
        Проверяем:
        - Статус 200
        - crypto_amount > 0
        - Правильные поля
        """
        response = client.post("/crypto/calculate", json=sample_calculator_request)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["crypto_id"] == "bitcoin"
        assert data["fiat_currency"] == "usd"
        assert data["fiat_amount"] == 1000.0
        assert data["crypto_amount"] > 0
        assert data["rate"] > 0
    
    @pytest.mark.integration
    def test_calculate_ethereum_for_eur(self, client):
        """Тест: сколько Ethereum за 500 EUR."""
        request = {
            "crypto_id": "ethereum",
            "fiat_currency": "eur",
            "fiat_amount": 500.0
        }
        
        response = client.post("/crypto/calculate", json=request)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["crypto_id"] == "ethereum"
        assert data["crypto_amount"] > 0


class TestSupportedCurrencies:
    """Тесты списка поддерживаемых валют."""
    
    def test_get_supported_currencies(self, client):
        """Тест: получение списка поддерживаемых валют."""
        response = client.get("/crypto/supported")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "cryptocurrencies" in data
        assert "fiat_currencies" in data
        
        cryptos = data["cryptocurrencies"]
        assert "bitcoin" in cryptos
        assert "ethereum" in cryptos
        
        fiats = data["fiat_currencies"]
        assert "usd" in fiats
        assert "eur" in fiats
        assert "rub" in fiats
