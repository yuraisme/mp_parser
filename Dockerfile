# Базовый образ с Python 3.13
FROM python:3.13-bookworm

# Устанавливаем зависимости для Chromium
RUN apt-get -y update
    # Install Chrome.
RUN  apt install chromium wget -y
# Install ChromeDriver.
RUN wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/
RUN unzip ~/chromedriver_linux64.zip -d ~/ 
RUN rm ~/chromedriver_linux64.zip 
RUN mv -f ~/chromedriver /usr/local/bin/chromedriver 
RUN chown root:root /usr/local/bin/chromedriver 
RUN chmod 0755 /usr/local/bin/chromedriver

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
