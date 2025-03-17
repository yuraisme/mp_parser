## Прайс-Парсер с Отчетом в Telegram

[![Formatter](https://img.shields.io/badge/formatter-black-black)](https://github.com/psf/black)
[![Linter](https://img.shields.io/badge/linter-mypy-1f5082)](https://mypy-lang.org/)
[![Linter](https://img.shields.io/badge/scrapper-DrissionPage-29ae43)](https://github.com/g1879/DrissionPage)

Парсер для сравнения цен конкурентов с автоматическим обновлением и отчетом через Telegram. Работает напрямую с Google Sheets без использования базы данных.

## Установка и Настройка

### Переменные Окружения Telegram

1. Создайте файл `.env` в корневой директории проекта
2. Заполните следующими переменными:
   - `SPREADSHEET_ID`: ID вашей Google Таблицы (берется из URL)
   - `TELEGRAM_TOKEN`: Токен вашего Telegram-бота (получите через @BotFather)
   - `TELEGRAM_GROUP_ID`: ID чата группы (обычно отрицательное число). Получить можно через запрос:
     ```bash
     curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates"
     ```
     После получения ID, удалите этот файл для безопасности.

### Настройка Google Sheets

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект и включите API Google Sheets
3. Создайте учетные данные (OAuth-креденциалы)
4. Скачайте полученный `credentials.json` и поместите в папку `services/`
более подробная инструкция:
https://developers.google.com/workspace/guides/create-credentials?hl=ru

### Запуск Приложения

#### Через Docker (Рекомендуется)
```bash
# Cкачайте проект
git clone -b release https://github.com/yuraisme/mp_parser.git
```

```bash
# Соберите и запустите контейнер
docker compose up --build -d

# Проверьте запущенные контейнеры
docker ps

# Если что-то не работает, посмотрите логи
docker logs parsing_app
```

#### Локальный Запуск (без Docker)

1. Установите зависимости:
   ```bash
   pip install uv
   ```

2. Убедитесь, что установлен Chromium:
   ```bash
   sudo apt update && sudo apt-get install chromium
   ```

3. Запустите приложение:
   ```bash
   uv run main.py
   ```
   Для запуска в фоновом режиме:
   ```bash
   nohup uv run main.py &
   ```

## Основные Функции

- Автоматическое обновление цен из Google Sheets
- Сравнение цен конкурентов
- Отправка отчетов через Telegram
- Интеграция с Google Sheets без использования БД

## Требования

- Python 3.12+
- Docker (для запуска через Docker)
- Google Account с настроенными API
- Telegram-бот

## Лицензия

MIT
```