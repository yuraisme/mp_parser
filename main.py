import datetime
import os
from http import client
from time import strftime
from typing import List

from dotenv import load_dotenv
from loguru import logger

from models import Item, Opponents
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
    while n_row <= len(gs_data) - 2:
        if (
            "ozon.ru" in gs_data[n_row][2]
            or "wildberries.ru" in gs_data[n_row][2]
        ):
            goods.append(
                Item(
                    sku=get_sku(gs_data[n_row][2]) or "",
                    name=gs_data[n_row][1],
                    timestamp=datetime.datetime.now(),
                )
            )
            n_row += 1
            while gs_data[n_row][2] == "" and gs_data[n_row][7] != "":
                if get_sku(gs_data[n_row][7]):
                    goods[len(goods) - 1].opponents_id.append(
                        get_sku(gs_data[n_row][7])
                    )
                n_row += 1
                if n_row >= len(gs_data):
                    break
        n_row += 1
    print(goods)
