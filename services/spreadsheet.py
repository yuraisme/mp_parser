import datetime
import os
import re
from typing import List
from zoneinfo import ZoneInfo

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from gspread import Cell
from loguru import logger

load_dotenv()
SHEET_ID = os.getenv("SPREADSHEET_ID")
TIME_ZONE = datetime.timezone(datetime.timedelta(hours=5))  #  (UTC+5)


class GoogleSheetsClient:
    authorised: bool = False

    def __init__(self, credentials_path: str, sheet_id: str | None):
        """
        :param credentials_path: Путь к файлу с учетными данными JSON.
        :param sheet_id: ID Google таблицы.
        """
        logger.info("Try to connect to Google sheet")

        if sheet_id is not None:
            try:
                self.credentials_path = credentials_path
                self.sheet_id = sheet_id
                self.client = self._authenticate()
                self.sheet = self.client.open_by_key(sheet_id)
                self.authorised = True
                logger.info("Success connect to google spreadsheet")
            except Exception as e:
                logger.error(f"Problem to acces to speadsheets: {e}")
                # raise ExceptGsheetApi
        else:
            logger.error("Where no sheet id name")
            # raise ExceptGsheetApi

    def _authenticate(self):
        """Аутентификация через сервисный аккаунт."""
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(
            self.credentials_path, scopes=scope
        )
        return gspread.authorize(creds)

    def get_sheet_data(self) -> List[List[str]]:
        worksheet = self.sheet.sheet1
        return worksheet.get_all_values()

    def update_master(self, row: int, name: str, price: int, sku: str):
        timestamp = datetime.datetime.now(TIME_ZONE).strftime(
            "%d.%m.%Y %H:%M:%S"
        )

        cells = [
            Cell(row, 1, sku),  # A
            Cell(row, 2, name),  # B
            Cell(row, 4, str(price)),  # D
            Cell(row, 9, timestamp),  # I
        ]
        self.sheet.sheet1.update_cells(cells)

    def update_slave(self, row: int, price: str, prev_price: str):
        timestamp = datetime.datetime.now(TIME_ZONE).strftime(
            "%d.%m.%Y %H:%M:%S"
        )
        diff_price = (
            str(int(prev_price) - int(price)) if prev_price != "" else "0"
        )

        cells = [
            Cell(row, 5, price),  # E
            Cell(row, 6, prev_price),  # F
            Cell(row, 7, diff_price),  # G
            Cell(row, 9, timestamp),  # I
        ]
        self.sheet.sheet1.update_cells(cells)

    def set_no_valid(self, row: int, column: int):
        self.sheet.sheet1.update_cell(row, column, "не валидная ссылка")


def get_sku(url: str | None = None) -> str | None:
    """return article as string"""
    if not url:
        logger.error("No url for ozon/WB SKU")
        raise ValueError("No url for ozon/WB SKU")

    pattern_ozon = r"https:\/\/www\.ozon\.ru\/product\/[^\/]+-(\d+)\/"
    pattern_wb = r"https:\/\/www\.wildberries\.ru\/catalog\/(\d+)\/detail"

    if match := re.search(pattern_ozon, url):
        return match.group(1)

    if match := re.search(pattern_wb, url):
        return match.group(1)

    # не случилось ни одного совпадения
    logger.error("No CORRECT url for ozon/WB SKU")
    raise ValueError("No CORRECT url for ozon/WB SKU")


if __name__ == "__main__":
    client = GoogleSheetsClient(
        os.path.join(os.getcwd(), "services", "credentials.json"),
        SHEET_ID,
    )

    if client.authorised:
        # data = client.get_sheet_data("Лист1")
        data = client.sheet.sheet1.get_all_values()
        print(data[0])
        # data1 = client.sheet.sheet1.get_all_values(f"C3:")
        exit()
        for _ in data:
            try:
                if _ != [""]:
                    # print(get_ozon_art(_[0]))
                    print(get_wb_art(_[0]))
            except:
                pass
        # print(data)
