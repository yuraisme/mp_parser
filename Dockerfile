# Базовый образ с Python 3.13
FROM python:3.13-bookworm

# Устанавливаем зависимости для Chromium
RUN apt-get -y update
    # Install Chrome.
RUN  apt install chromium -y
RUN  apt update
RUN  apt install chromium-chromedriver -y
# Install ChromeDriver.


RUN pip install uv

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

ENV PATH="/usr/lib/chromium/:${PATH}"
# Создаём виртуальное окружение и устанавливаем зависимости через UV
RUN uv sync
# Указываем переменные окружения
#ENV PYTHONUNBUFFERED=1
#ENV PATH="/app/.venv/bin:$PATH"

# Запуск приложения
#CMD ["python", "main.py"]
