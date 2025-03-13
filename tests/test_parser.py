import unittest
from unittest.mock import MagicMock, patch

from services.parser import Parser, kill_chromium_processes
import pathlib
import os

if os.name == "nt":  # Windows
    PathClass = pathlib.WindowsPath
else:  # POSIX
    PathClass = pathlib.PosixPath


class TestParser(unittest.TestCase):

    @patch("services.parser.Chromium")
    @patch("services.parser.kill_chromium_processes")
    def test_parser_initialization(self, mock_kill, mock_chromium):
        # Проверяем создание объекта Parser и корректное инициализирование
        mock_browser = MagicMock()
        mock_chromium.return_value = mock_browser
        parser = Parser(headless=True)
        self.assertIsNotNone(parser.browser)
          # Проверяем наличие аргумента --headless в ChromiumOptions
        self.assertIn('--headless=new', parser.co.arguments)

    def test_parse_price_valid_input(self):
        parser = Parser()
        valid_response = "1 234 ₽"
        price = parser._parse_price(valid_response)
        self.assertEqual(price, "1234")

    def test_parse_price_invalid_input(self):
        parser = Parser()
        invalid_response = "No price found"
        price = parser._parse_price(invalid_response)
        self.assertIsNone(price)

    @patch("services.parser.Parser._parse_price")
    @patch("services.parser.Chromium")
    def test_get_ozon_price(self, mock_chromium, mock_parse_price):
        mock_browser = MagicMock()
        mock_tab = MagicMock()
        mock_browser.latest_tab = mock_tab
        mock_chromium.return_value = mock_browser
        mock_tab.get.return_value = True
        mock_tab.eles.return_value.filter_one.return_value.text = "1 000 ₽"
        mock_parse_price.return_value = "1000"

        parser = Parser()
        result = parser.get_ozon_price("https://www.ozon.ru/product/test")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["Price"], 1000)

    @patch("services.parser.Parser._parse_price")
    @patch("services.parser.Chromium")
    def test_get_wb_price(self, mock_chromium, mock_parse_price):
        mock_browser = MagicMock()
        mock_tab = MagicMock()
        mock_browser.latest_tab = mock_tab
        mock_chromium.return_value = mock_browser
        mock_tab.get.return_value = True
        mock_tab.ele.return_value.text = "500 ₽"
        mock_parse_price.return_value = "500"

        parser = Parser()
        result = parser.get_wb_price("https://www.wildberries.ru/catalog/123")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["Price"], 500)

    @patch.object(Parser, 'get_ozon_price')
    @patch.object(Parser, 'get_wb_price')
    def test_get_data(self, mock_get_wb_price, mock_get_ozon_price):
        parser = Parser()

        # Тестируем ozon URL
        mock_get_ozon_price.return_value = {"Price": 1000, "Name": "Test Product Ozon"}
        result = parser.get_data("https://www.ozon.ru/product/test")
        self.assertEqual(result, {"Price": 1000, "Name": "Test Product Ozon"})
        mock_get_ozon_price.assert_called_once_with("https://www.ozon.ru/product/test")

        # Тестируем wildberries URL
        mock_get_wb_price.return_value = {"Price": 500, "Name": "Test Product WB"}
        result = parser.get_data("https://www.wildberries.ru/catalog/test")
        self.assertEqual(result, {"Price": 500, "Name": "Test Product WB"})
        mock_get_wb_price.assert_called_once_with("https://www.wildberries.ru/catalog/test")

        # Тестируем некорректный URL
        result = parser.get_data("https://www.example.com")
        self.assertIsNone(result)

    @patch("services.parser.os.system")
    def test_kill_chromium_processes_windows(self, mock_os):
        os.name = "nt"
        kill_chromium_processes()
        mock_os.assert_called_with("taskkill /im chrome.exe /f")


if __name__ == "__main__":
    unittest.main()
