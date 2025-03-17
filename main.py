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
HEADER_ROWS_OFFSET = 3
MAX_RETRIES = 3
NO_VALID_DATA_IDX = 9
NO_VALID_DATA_GS_COL = 10
ROW_LEN_WITH_INVALID_COL = 10
OUR_URL_IDX = 2
OPPONENT_URL_IDX = 7
PREV_PRICE_IDX = 4
DELAY_RANGE = (3, 5)


def main(headless: bool = True):
    google_sheet = GoogleSheetsClient(
        os.path.join(os.getcwd(), "services", "credentials.json"), SHEET_ID
    )
    parser = Parser(headless)

    bot = Telebot()
    while True:
        logger.info("*************Start from Begin Google Sheet*************")
        gs_data = google_sheet.get_sheet_data()

        """начинаем не с самого вверха = отступаем шапку"""
        for n_row, row in enumerate(gs_data[HEADER_ROWS_OFFSET - 1 :]):
            try:
                # проверяем какой урл будем проверять - свой или конкурента
                url = row[OUR_URL_IDX]
                if "http" in row[OPPONENT_URL_IDX]:
                    url = row[OPPONENT_URL_IDX]
                if url == "":
                    continue
                sku = get_sku(url) or ""

                """сколько то раз пробуем, если с первого не получится
                    в идеале - ещё и прокси переключать, но пока этого не требуется
                """
                for atempt_idx in range(MAX_RETRIES):
                    """3 раза пробуем скачать, потом сдаёмсо"""
                    """но если невалидная - сдаёмся после певого раза """
                    if len(row) > 9:  # пока лист чистый- 10го столбца нет
                        if (
                            atempt_idx > 0
                            and row[NO_VALID_DATA_IDX]
                            == "! НЕВАЛИДНАЯ ССЫЛКА !"
                        ):
                            logger.warning(
                                "Url already invalid - exit from trying"
                            )
                            break  # выходим из цикла попыток

                    """наша ссылка"""
                    # проверка на то что ячейке есть URL
                    if "http" in row[OUR_URL_IDX]:
                        if response := parser.get_data(url):
                            # print(response)
                            logger.info(f"Send {response} to google sheet")
                            google_sheet.update_master(
                                n_row + HEADER_ROWS_OFFSET,
                                response["Name"],
                                response["Price"],
                                sku,
                            )
                            break
                        else:
                            time.sleep(random.randrange(*DELAY_RANGE))
                            try:
                                print(sku)
                                if atempt_idx >= MAX_RETRIES - 1:
                                    google_sheet.set_no_valid(
                                        n_row + HEADER_ROWS_OFFSET
                                    )
                                    logger.warning(
                                        f"Looks like {sku} isn't valid"
                                    )
                            except Exception as e:
                                logger.error(
                                    f"Error during GS was added no valid sku: {e}"
                                )
                                break

                    """ссылка конкурентов"""
                    # проверка на то что ячейке есть URL
                    if "http" in row[OPPONENT_URL_IDX]:
                        if response := parser.get_data(url):
                            # print(response)
                            logger.info(f"Send {response} to google sheet")
                            google_sheet.update_slave(
                                row=n_row + HEADER_ROWS_OFFSET,
                                price=response["Price"],
                                prev_price=row[PREV_PRICE_IDX],
                            )
                            bot.send_message(
                                url, row[PREV_PRICE_IDX], response["Price"]
                            )
                            break
                        else:
                            time.sleep(random.randrange(*DELAY_RANGE))
                            try:
                                print(sku)
                                if atempt_idx >= MAX_RETRIES - 1:
                                    google_sheet.set_no_valid(
                                        n_row + HEADER_ROWS_OFFSET
                                    )
                                    logger.warning(
                                        f"Looks like {sku} not valid"
                                    )
                            except Exception as e:
                                logger.error(
                                    f"Error during GS was added no valid sku: {e}"
                                )
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
