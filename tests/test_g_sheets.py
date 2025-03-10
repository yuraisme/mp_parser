from unittest.mock import MagicMock, patch

import pytest

from services.spreadsheet import GoogleSheetsClient, get_ozon_art, get_wb_art


@pytest.fixture
def mock_gspread():
    """Создает заглушку для gspread"""
    with patch("parsing.services.spreadsheet.gspread") as mock_gspread:
        yield mock_gspread


@pytest.fixture
def mock_credentials():
    """Создает заглушку для Credentials"""
    with patch("parsing.services.spreadsheet.Credentials") as mock_creds:
        yield mock_creds




@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://www.ozon.ru/product/vneshniy-akkumulyator-123456789/",
            "123456789",
        ),
        ("https://www.ozon.ru/product/item-987654321/", "987654321"),
        ("https://www.ozon.ru/product/other-5634821/", "5634821"),
        ("https://www.ozon.ru/category/some-other-url/", None),
    ],
)
def test_get_ozon_art(url, expected):
    """Тестирование извлечения артикула Ozon"""
    assert get_ozon_art(url) == expected


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://www.wildberries.ru/catalog/12295464/detail.aspx",
            "12295464",
        ),
        ("https://www.wildberries.ru/catalog/999999/detail.aspx", "999999"),
        (
            "https://www.wildberries.ru/catalog/54321/detail.aspx?extra=data",
            "54321",
        ),
        ("https://www.wildberries.ru/other-page", None),
    ],
)
def test_get_wb_art(url, expected):
    """Тестирование извлечения артикула Wildberries"""
    assert get_wb_art(url) == expected


def test_get_ozon_art_invalid_url():
    """Тестирование обработки некорректных URL Ozon"""
    with pytest.raises(ValueError, match="No url for ozon SKU"):
        get_ozon_art()

    with pytest.raises(ValueError, match="No CORRECT url for ozon SKU"):
        get_ozon_art("https://www.example.com/product/123")


def test_get_wb_art_invalid_url():
    """Тестирование обработки некорректных URL Wildberries"""
    with pytest.raises(ValueError, match="No url for wildberries SKU"):
        get_wb_art("")

    with pytest.raises(
        ValueError, match="No CORRECT url for wildberries SKU"
    ):
        get_wb_art("https://www.example.com/catalog/456")
        get_wb_art("https://www.example.com/catalog/456")
        get_wb_art("https://www.example.com/catalog/456")
