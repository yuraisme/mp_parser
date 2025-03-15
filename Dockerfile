# Базовый образ с Python 3.13
FROM python:3.13-slim

# Устанавливаем зависимости для Chromium
RUN apt-get update && apt-get install -y \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем UV — менеджер пакетов
RUN pip install uv

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Создаём виртуальное окружение и устанавливаем зависимости через UV
RUN uv venv && uv pip install -e .

# Указываем переменные окружения
#ENV PYTHONUNBUFFERED=1
#ENV PATH="/app/.venv/bin:$PATH"

# Запуск приложения
#CMD ["python", "main.py"]
