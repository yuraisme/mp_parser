import datetime
import os
import re
import time
from typing import List

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from gspread import Cell
from gspread.exceptions import APIError
from loguru import logger

load_dotenv()
SHEET_ID = os.getenv("SPREADSHEET_ID")
TIME_ZONE = datetime.timezone(datetime.timedelta(hours=5))  #  (UTC+5)
DELAY_FOR_GS_LIMITS = 10  # seconds
SKU_COL = 1
NAME_COL = 2
PRICE_COL = 4
TIMESTAMP_COL = 9
SLAVE_PRICE_COL = 5
SLAVE_PREV_PRICE_COL = 6
SLAVE_DIFF_PRICE_COL = 7
NO_VALID_COL = 10


class GoogleSheetsClient:
    authorised: bool = False

    def __init__(self, credentials_path: str, sheet_id: str | None):
        """
        :param credentials_path: Путь к файлу с учетными данными JSON.
        :param sheet_id: ID Google таблицы.
        """
        logger.info("Try to connect to Google sheet")
        self.authorised = False
        if sheet_id:
            self.credentials_path = credentials_path
            self.sheet_id = sheet_id
            try:
                self.client = self._authenticate()
                self.sheet = self.client.open_by_key(sheet_id)
                self.authorised = True
                logger.success("Success connect to google spreadsheet")
            except Exception as e:
                logger.error(f"Problem with speadsheets: {e}")
        else:
            logger.error("GS sheet ID hadn't loaded")
            raise ValueError("SPREADSHEET_ID is not set in env variables")

    @staticmethod
    def _get_timestamp() -> str:
        return datetime.datetime.now(TIME_ZONE).strftime("%d.%m.%Y %H:%M:%S")

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
        """получение данных со всего листа"""
        worksheet = self.sheet.sheet1
        return worksheet.get_all_values()

    def update_master(self, row: int, name: str, price: str, sku: str):
        cells = [
            Cell(row, SKU_COL, sku),  # A
            Cell(row, NAME_COL, name),  # B
            Cell(row, PRICE_COL, price),  # D
            Cell(row, TIMESTAMP_COL, self._get_timestamp()),  # I
        ]
        try:
            self.sheet.sheet1.update_cells(cells)
        except APIError as e:
            if e.code == 429:
                logger.error("Overdraft limit connections to SG")
                time.sleep(DELAY_FOR_GS_LIMITS)
                return None
            logger.error(f"Error while write to GS {sku=}: {e}")

    def update_slave(self, row: int, price: str, prev_price: str):
        """используем буффер на листе"""
        diff_price = "0"
        try:
            if price != "" and prev_price != "":
                diff_price = (
                    str(int(price) - int(prev_price))
                    if prev_price != ""
                    else "0"
                )
        except ValueError:
            logger.error(f"Incorrect digits: {price=}, {prev_price=}")

        cells = [
            Cell(row, SLAVE_PRICE_COL, price),  # E
            Cell(row, SLAVE_PREV_PRICE_COL, prev_price),  # F
            Cell(row, SLAVE_DIFF_PRICE_COL, diff_price),  # G
            Cell(row, TIMESTAMP_COL, self._get_timestamp()),  # I
        ]
        try:
            self.sheet.sheet1.update_cells(cells)
        except APIError as e:
            if e.code == 429:
                logger.error("Overdraft limit connections to SG")
                time.sleep(DELAY_FOR_GS_LIMITS)
                return None
            logger.error(f"Error while write to GS: {e}")

    def set_no_valid_url(self, row: int):
        self.sheet.sheet1.update_cell(
            row, NO_VALID_COL, "! НЕВАЛИДНАЯ ССЫЛКА !"
        )


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
        os.path.join(os.getcwd(), "services", "credentials.json"), SHEET_ID
    )

    if client.authorised:
        # data = client.get_sheet_data("Лист1")
        data = client.sheet.sheet1.get_all_values()
        print(data[0])
        # data1 = client.sheet.sheet1.get_all_values(f"C3:")
        exit()
