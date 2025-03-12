import datetime
import os
import time
from http import client
from time import strftime
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


def refresh_items(gs_id: str) -> List[Item]:
    gs_client = GoogleSheetsClient(
        os.path.join("services", "credentials.json"),
        gs_id,
    )
    if gs_client.authorised:
        cells = gs_client.sheet.sheet1.get_all_values()
        result: List[Item] = []
        if cells:
            for n_row, row in enumerate(cells):
                if n_row >= 2:
                    if "ozon.ru" in row[2]:
                        print(get_ozon_art(row[2]))
                        gs_client.sheet.sheet1.update_cell(
                            n_row + 1, 1, get_ozon_art(row[2]) or ""
                        )
                    elif "wildberries.ru" in row[2]:
                        print(get_wb_art(row[2]))

                        gs_client.sheet.sheet1.update_cell(
                            n_row + 1, 1, get_wb_art(row[2]) or ""
                        )
    else:
        logger.error("Something wrong with connect to google sheets")
        raise ValueError("Something wrong with connect to google sheets")

    return result


if __name__ == "__main__":
    # main()
    # refresh_items(SHEET_ID)
    # print(data)
    google_sheet = GoogleSheetsClient(
        os.path.join(os.getcwd(), "services", "credentials.json"),
        SHEET_ID,
    )
    gs_data = google_sheet.get_sheet_data()
    n_row = 2
    goods: List[Item] = []
    parser = Parser(headless=True)

    for n_row, row in enumerate(gs_data):
        try:
            orig_url = row[2]
            for i in range(3):
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
                        2,
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
