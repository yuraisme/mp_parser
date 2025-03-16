import os
import random
import sys
import time

from dotenv import load_dotenv
from loguru import logger

from services.parser import Parser
from services.spreadsheet import GoogleSheetsClient, get_sku
from services.telegram_bot import Telebot

load_dotenv()
SHEET_ID = os.getenv("SPREADSHEET_ID") or ""


def main(headless: bool = True):
    google_sheet = GoogleSheetsClient(
        os.path.join(os.getcwd(), "services", "credentials.json"),
        SHEET_ID,
    )
    parser = Parser(headless)

    bot = Telebot()
    while True:
        logger.info("*************Start from Begin Google Sheet*************")
        gs_data = google_sheet.get_sheet_data()
        for n_row, row in enumerate(gs_data[2:]):
            try:
                # проверяем какой урл будем проверять - свой или конкурента
                url = row[2] if len(row[2]) > 10 else row[7]
                if url == "":
                    continue
                for i in range(3):
                    """3 раза пробуем скачать, потом сдаёмсо"""

                    """но если невалидная - сдаёмся после певого раза """
                    if len(row) > 9:  # пока лист чистый- 10го столбца нет
                        if i > 0 and row[9] == "! НЕВАЛИДНАЯ ССЫЛКА !":
                            logger.warning(
                                "Url already invalid - exit from trying"
                            )
                            break
                    """наша ссылка"""

                    if len(row[2]) > 10:  # проверка на то что ячейке есть URL
                        if response := parser.get_data(url):
                            # print(response)
                            logger.info(f"Send {response} to google sheet")
                            google_sheet.update_master(
                                n_row + 3,
                                response["Name"],
                                response["Price"],
                                get_sku(url),
                            )
                            break
                        else:
                            time.sleep(random.randrange(3, 5))
                            try:
                                print(get_sku(url))
                                if i == 2:
                                    google_sheet.set_no_valid(n_row + 3)
                                    logger.warning(
                                        f"Looks like {get_sku(url)} not valid"
                                    )
                            except:
                                break
                    """ссылка конкурентов"""
                    if len(row[7]) > 10:  # проверка на то что ячейке есть URL
                        if response := parser.get_data(url):
                            # print(response)
                            logger.info(f"Send {response} to google sheet")
                            google_sheet.update_slave(
                                row=n_row + 3,
                                price=response["Price"],
                                prev_price=row[4],
                            )
                            bot.send_message(url, row[4], response["Price"])
                            break
                        else:
                            time.sleep(random.randrange(3, 5))
                            try:
                                print(get_sku(url))
                                if i == 2:
                                    google_sheet.set_no_valid(n_row + 3)
                                    logger.warning(
                                        f"Looks like {get_sku(url)} not valid"
                                    )
                            except:
                                break
            except KeyboardInterrupt:
                logger.warning("Exit at the user's request")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Error {e}")
        logger.info("===========End of Google Sheet. Start Again===========")
        time.sleep(5)


if __name__ == "__main__":
    main(headless=True)
    # refresh_items(SHEET_ID)
    # print(data)
