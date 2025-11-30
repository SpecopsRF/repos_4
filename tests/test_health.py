"""
Тесты для health check эндпоинтов.

Эти тесты проверяют что базовые эндпоинты работают.
Они должны проходить всегда — если падают, значит приложение сломано.
"""

import pytest


class TestHealthEndpoints:
    """Тесты системных эндпоинтов."""
    
    def test_root_endpoint(self, client):
        """
        Тест: главная страница возвращает информацию о приложении.
        
        Проверяем:
        - Статус код 200
        - Есть название приложения
        - Есть версия
        """
        response = client.get("/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "app" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """
        Тест: /health возвращает статус healthy.
        
        Этот эндпоинт использует Kubernetes для проверки
        что приложение живо (liveness probe).
        """
        response = client.get("/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "app_name" in data
    
    def test_ready_endpoint(self, client):
        """
        Тест: /ready возвращает статус ready.
        
        Этот эндпоинт использует Kubernetes для проверки
        что приложение готово принимать трафик (readiness probe).
        """
        response = client.get("/ready")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data


class TestAPIDocumentation:
    """Тесты документации API."""
    
    def test_swagger_ui_available(self, client):
        """Тест: Swagger UI доступен."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema_available(self, client):
        """Тест: OpenAPI схема доступна."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
