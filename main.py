
import os

from dotenv import load_dotenv
from services.spreadsheet import GoogleSheetsClient, get_wb_art


load_dotenv()
SHEET_ID = os.getenv("SPREADSHEET_ID")

def main():
    print("Hello from parsing!")


if __name__ == "__main__":
    main()
    client = GoogleSheetsClient(
        os.path.join("services", "credentials.json"),
        SHEET_ID,
    )

    if client.authorised:
        data = client.get_sheet_data("Лист1")
        for _ in data[2:]:
            try:
                print(get_wb_art(_[2]))
            except:
                pass
        # print(data)
