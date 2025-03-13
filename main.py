import datetime
import os
import time
from typing import List
from urllib import response

from dotenv import load_dotenv
from loguru import logger

from models import Item, Opponents
from services.parser import Parser
from services.spreadsheet import GoogleSheetsClient, get_sku

load_dotenv()
SHEET_ID = os.getenv("SPREADSHEET_ID") or ""


def main():
    print("Hello from parsing!")


if __name__ == "__main__":
    # main()
    # refresh_items(SHEET_ID)
    # print(data)
    google_sheet = GoogleSheetsClient(
        os.path.join(os.getcwd(), "services", "credentials.json"),
        SHEET_ID,
    )
    gs_data = google_sheet.get_sheet_data()
    parser = Parser(headless=True)

    for n_row, row in enumerate(gs_data[2:]):
        try:
            # проверяем какой урл будем проверять - свой или конкурента
            url = row[2] if len(row[2]) > 10 else row[7]
            if url == "":
                continue
            for i in range(3):
                """3 раза пробуем скачать, потом сдаёмсо"""
                if len(row[2]) > 10:  # наша ссылка
                    if response := parser.get_data(url):
                        print(response)
                        google_sheet.update_master(
                            n_row + 3,
                            response["Name"],
                            response["Price"],
                            get_sku(url),
                        )
                        break
                    else:
                        time.sleep(2)
                        try:
                            print(get_sku(url))
                            if i == 2:
                                google_sheet.set_no_valid(n_row + 3, 2)
                        except:
                            break

                if len(row[7]) > 10:  # ссылка конкурентов
                    if response := parser.get_data(url):
                        print(response)
                        google_sheet.update_slave(
                            row=n_row + 3,
                            price=response["Price"],
                            prev_price=row[4],
                        )
                        break
                    else:
                        time.sleep(2)
                        try:
                            print(get_sku(url))
                            if i == 2:
                                google_sheet.set_no_valid(n_row + 3, 5)
                        except:
                            break

        except Exception as e:
            logger.error(f"Error {e}")
    # for _ in goods:
    #     print(_)
