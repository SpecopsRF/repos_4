# ============================================
# Crypto Tracker - Dockerfile
# ============================================
# Многоэтапная сборка (multi-stage build)
# Этап 1: builder - устанавливаем зависимости
# Этап 2: production - минимальный образ для запуска
# ============================================

# ----- Этап 1: Builder -----
# Используем полный образ Python для установки зависимостей
FROM python:3.12-slim AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Создаём виртуальное окружение и устанавливаем зависимости
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ----- Этап 2: Production -----
# Используем минимальный образ для запуска
FROM python:3.12-slim AS production

# Метаданные образа
LABEL maintainer="SpecopsRF"
LABEL description="Crypto Tracker API"
LABEL version="1.0.0"

# Создаём непривилегированного пользователя (безопасность!)
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем виртуальное окружение из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем код приложения
COPY --chown=appuser:appgroup ./app ./app

# Переключаемся на непривилегированного пользователя
USER appuser

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000

# Открываем порт
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
