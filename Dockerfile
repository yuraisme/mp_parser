# Базовый образ с Python 3.13
FROM python:3.13

# Устанавливаем зависимости для Chromium
RUN apt-get -y update
    # Install Chrome.
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add \
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
apt-get -y update \
apt-get -y install chromium-browser

# Install ChromeDriver.
RUN wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/ \
unzip ~/chromedriver_linux64.zip -d ~/ \
rm ~/chromedriver_linux64.zip \
mv -f ~/chromedriver /usr/local/bin/chromedriver \
chown root:root /usr/local/bin/chromedriver \
chmod 0755 /usr/local/bin/chromedriver

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
