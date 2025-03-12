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

    for n_row, row in enumerate(gs_data):
        try:
            orig_url = row[2]
            for i in range(3):
                """3 раза пробуем скачать, потом сдаёмсо"""

                if "ozon" in orig_url:
                    response = parser.get_ozon_price(orig_url)
                elif "wildberries" in orig_url:
                    response = parser.get_wb_price(orig_url)
                else:
                    break

                if response:
                    print(response)
                    google_sheet.update_master(
                        n_row + 1,
                        response["Name"],
                        response["Price"],
                        get_sku(orig_url),
                    )
                    break
                else:
                    time.sleep(2)
                    try:
                        print(get_sku(orig_url))
                    except:
                        break

        except Exception as e:
            logger.error(f"Error {e}")
    # for _ in goods:
    #     print(_)
