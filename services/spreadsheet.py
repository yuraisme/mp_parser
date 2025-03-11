import os
import re
from typing import List

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from loguru import logger

load_dotenv()
SHEET_ID = os.getenv("SPREADSHEET_ID")


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


def get_ozon_art(url: str | None = None) -> str | None:
    """return article as string"""

    pattern = r"https:\/\/www\.ozon\.ru\/product\/[^\/]+-(\d+)\/"
    if not url:
        logger.error("No url for ozon SKU")
        raise ValueError("No url for ozon SKU")
    if "ozon.ru" not in url.lower():
        logger.error("No CORRECT url for ozon SKU")
        raise ValueError("No CORRECT url for ozon SKU")
    match = re.search(pattern, url)
    if match:
        return match.group(1)


def get_wb_art(url: str | None = None) -> str | None:
    pattern = r"https:\/\/www\.wildberries\.ru\/catalog\/(\d+)\/detail"
    if not url:
        logger.error("No url for wildberries SKU")
        raise ValueError("No url for wildberries SKU")
    if "wildberries.ru" not in url.lower():
        logger.error("No CORRECT url for wildberries SKU")
        raise ValueError("No CORRECT url for wildberries SKU")
    match = re.search(pattern, url)
    if match:
        return match.group(1)


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
