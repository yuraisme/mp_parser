import os
import sys

import telebot
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class Telebot:
    def __init__(self) -> None:
        try:
            logger.info("Creating telegram bot object...")
            self.token = os.getenv("TELEGRAM_TOKEN") or ""
            self.group_id = os.getenv("TELEGRAM_GROUP_ID") or ""
            if self.token == "" or self.group_id == "":
                logger.error(
                    "Error: TELEGRAM_TOKEN и TELEGRAM_GROUP_ID must be setting up"
                )
                sys.exit(1)
            self.bot = telebot.TeleBot(self.token)
            logger.success("Telegramm object succefully create!")
        except Exception as e:
            logger.critical(f"Bot wasn't create: {e}")

    def send_message(self, url: str, price_prev: str, price_current: str):
        if (
            price_prev == price_current
            or price_prev == ""
            or price_current == ""
        ):
            return None

        logger.info("Price was change ↓↓↓")
        if int(price_prev) < int(price_current):
            logger.info("Sending message about prise rising...")
            self.send_rise_message(url, price_prev, price_current)
            return True

        if int(price_prev) > int(price_current):
            logger.info("Sending message about prise falling...")
            self.send_fall_message(url, price_prev, price_current)
            return True

    def send_rise_message(
        self, url: str, price_prev: str, price_current: str
    ) -> bool | None:
        try:
            diff = int(price_current) - int(price_prev)
            diff_percent = float(int(price_current) / int(price_prev)) - 1
            message = (
                f"Цена на [товар]({url}) конкурента\n"
                f"⬆️ Выросла с *{price_prev} ₽* до *{price_current} ₽*\n"
                f"📊 Разница  `{diff} ₽ ({diff_percent:.1%})`"
            )
            self.bot.send_message(
                chat_id=self.group_id, parse_mode="Markdown", text=message
            )
            logger.success("Bot successfully sent a message to the group")
            return True
        except Exception as e:
            logger.error(f"Error during bot sending message: {e}")

    def send_fall_message(
        self, url: str, price_prev: str, price_current: str
    ) -> bool | None:
        try:
            diff = int(price_current) - int(price_prev)
            diff_percent = 1 - float(int(price_prev) / int(price_current))
            message = (
                f"Цена на [товар]({url}) конкурента\n"
                f"⬇️ Упала с *{price_prev} ₽* до *{price_current} ₽*\n"
                f"📊 Разница  `{diff} ₽ ({diff_percent:.1%})`"
            )
            self.bot.send_message(
                chat_id=self.group_id, parse_mode="Markdown", text=message
            )
            logger.success("Bot successfully sent a message to the group")
            return True
        except Exception as e:
            logger.error(f"Error during bot sending message: {e}")


if __name__ == "__main__":
    # Собираем текст сообщения из аргументов командной строки
    message_text = "test message"
    bot = Telebot()
    bot.send_message(
        "https://www.ozon.ru/product/chesalka-dlya-tela-teleskopicheskaya-massazher-dlya-spiny-1400285112/?at=pZtpw3j31FxXrWkqU3vwr9pimJvYN1fXm8JvocyoDJKE&avtc=1&avte=4&avts=1738053903&keywords=%D1%87%D0%B5%D1%81%D0%B0%D0%BB%D0%BA%D0%B0+%D0%B4%D0%BB%D1%8F+%D1%81%D0%BF%D0%B8%D0%BD%D1%8B",
        "140",
        "148",
    )
