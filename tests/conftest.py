"""
Конфигурация pytest.

conftest.py — специальный файл pytest, который:
1. Содержит fixtures (переиспользуемые объекты для тестов)
2. Автоматически загружается pytest
3. Fixtures доступны во всех тестах
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def client():
    """
    Синхронный тестовый клиент.
    
    Используется для простых тестов без async/await.
    
    Пример использования:
        def test_example(client):
            response = client.get("/")
            assert response.status_code == 200
    """
    return TestClient(app)


@pytest.fixture
async def async_client():
    """
    Асинхронный тестовый клиент.
    
    Используется для тестов асинхронных эндпоинтов.
    
    Пример использования:
        async def test_example(async_client):
            response = await async_client.get("/")
            assert response.status_code == 200
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_conversion_request():
    """Пример запроса на конвертацию."""
    return {
        "from_crypto": "bitcoin",
        "to_currency": "usd",
        "amount": 0.5
    }


@pytest.fixture
def sample_calculator_request():
    """Пример запроса калькулятора."""
    return {
        "crypto_id": "bitcoin",
        "fiat_currency": "usd",
        "fiat_amount": 1000.0
    }
