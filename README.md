[![](https://img.shields.io/badge/formatter-black-black)](https://github.com/psf/black)
[![Linter](https://img.shields.io/badge/linter-mypy-1f5082)](https://mypy-lang.org/)

Парсер для  сравнивания цен конкурентов, с автоматическим обновлением и отчётом через телеграмм.
Вариант без базы данных, только GOOGLE SPREADSHEETS
### Установка


#### <u>Telegram</u>
перво-наперво создаем в корне файл-переменную окружения `.env`

внутри разместить 3 переменных:

**SPREADSHEET_ID** =  <id google spead sheet - берётся из url><br>
**TELEGRAM_TOKEN** = <токен телеграмм бота (создаётся через FatherBot)><br>
**TELEGRAM_GROUP_ID** = <id чата группы - обычно отрицательный -можно получить: 
```bash 
curl -s "https://api.telegram.org/bot<TELEGEAM TOKEN>/getUpdates"
```
или вставить прямо в строку браузера. в итоговом JSON - искать chat. Предварительно в группу, куда добавлен бот - послать `/start`
>


#### <u> SpreadSheets </u>
для доступа к листам google необходимо подключить ключи доступа по API.

Инструкция: https://developers.google.com/workspace/guides/create-credentials?hl=ru

необходимо получить в итоге  файл `credentials.json` который кладём в папку **services**.



#### <u> Запуск </u>

Для установки в Docker - переходим в корень и запускаем:
```bash
$ docker compose up --build -d
```
после сборки контейнера проверяем
проверяем: 
```bash
$  docker ps 
```

должен отобразиться процесс с именем *parsing_app*

если что-то не сработает - можно посомтреть логи:
```bash
$  docker logs parsing_app
```

если докер не устраивает  - можно запусить прямо в коммандной строке, предварительно установив *uv* :
```bash
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```
или через pip:
```bash
$ pip install uv
```

после чего в корне запускаем:
```bash
$ uv run main.py
```
или, в фоновом режиме:

```bash
$ nohup uv run main.py &
```
В этом случае на запускаемой машине должен быть явно устанвлен Chromium browser!
например:

```bash
$ sudo apt update
$ sudo apt-get install chromium
```