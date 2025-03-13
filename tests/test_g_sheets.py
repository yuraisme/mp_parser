import unittest
from unittest.mock import MagicMock, patch

from services.spreadsheet import GoogleSheetsClient, get_sku


class TestGoogleSheetsClient(unittest.TestCase):

    @patch("services.spreadsheet.Credentials.from_service_account_file")
    @patch("services.spreadsheet.gspread.authorize")
    def test_authentication(self, mock_authorize, mock_creds):
        mock_client = MagicMock()
        mock_authorize.return_value = mock_client
        client = GoogleSheetsClient("test_credentials.json", "test_sheet_id")
        self.assertTrue(client.authorised)
        self.assertIsNotNone(client.sheet)

    @patch("services.spreadsheet.GoogleSheetsClient._authenticate")
    def test_get_sheet_data(self, mock_authenticate):
        mock_client = MagicMock()
        mock_authenticate.return_value = mock_client
        mock_client.open_by_key().sheet1.get_all_values.return_value = [
            ["Test Data"]
        ]

        client = GoogleSheetsClient("test_credentials.json", "test_sheet_id")
        data = client.get_sheet_data()
        self.assertEqual(data, [["Test Data"]])

    @patch("services.spreadsheet.GoogleSheetsClient._authenticate")
    def test_update_master(self, mock_authenticate):
        mock_client = MagicMock()
        mock_authenticate.return_value = mock_client
        client = GoogleSheetsClient("test_credentials.json", "test_sheet_id")

        client.update_master(1, "Test Name", 100, "12345")
        mock_client.open_by_key().sheet1.update_cells.assert_called_once()


class TestGetSkuFunction(unittest.TestCase):
    def test_get_sku_valid_ozon(self):
        url = "https://www.ozon.ru/product/test-product-12345678/"
        sku = get_sku(url)
        self.assertEqual(sku, "12345678")

    def test_get_sku_valid_wb(self):
        url = "https://www.wildberries.ru/catalog/12345678/detail"
        sku = get_sku(url)
        self.assertEqual(sku, "12345678")

    def test_get_sku_invalid_url(self):
        url = "https://www.example.com"
        with self.assertRaises(ValueError):
            get_sku(url)

    def test_get_sku_no_url(self):
        with self.assertRaises(ValueError):
            get_sku()


if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
