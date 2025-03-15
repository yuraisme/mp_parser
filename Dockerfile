# Базовый образ с Python 3.13
FROM python:3.13-bookworm

# Устанавливаем зависимости для Chromium
RUN apt-get -y update
    # Install Chrome.
RUN  apt install chromium -y
RUN  apt upgrade -y
 # RUN  apt install chromium-chromedriver -y
# Install ChromeDriver.
RUN apt-get install unzip 
RUN wget -N https://chromedriver.storage.googleapis.com/133.0.6943.142/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN chmod +x chromedriver

RUN mv -f chromedriver /usr/local/share/chromedriver
RUN ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
RUN ln -s /usr/local/share/chromedriver /usr/bin/chromedriver

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
