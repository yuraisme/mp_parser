import os
import sys

import telebot
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class Telebot:
    def __init__(self) -> None:
        self.token = os.getenv("TELEGRAM_TOKEN") or ""
        self.group_id = os.getenv("TELEGRAM_GROUP_ID") or ""
        if self.token == "" or self.group_id == "":
            logger.error(
                "Error: TELEGRAM_TOKEN и TELEGRAM_GROUP_ID must be setting up"
            )
            sys.exit(1)
        self.bot = telebot.TeleBot(self.token)

    def send_message(self, message: str) -> bool | None:
        try:
            self.bot.send_message(chat_id=self.group_id, text=message)
            logger.success("Bot successfully sent a message to the group")
            return True
        except Exception as e:
            logger.error(f"Error during bot sending message: {e}")


if __name__ == "__main__":
    # Собираем текст сообщения из аргументов командной строки
    message_text = "test message"
    bot = Telebot()
    bot.send_message(message_text)
    bot.send_message(message_text)
