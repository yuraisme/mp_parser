import os
import random
import time

from dotenv import load_dotenv
from DrissionPage import Chromium
from DrissionPage.common import ChromiumOptions, Settings
from DrissionPage.errors import BrowserConnectError, ElementNotFoundError
from loguru import logger

load_dotenv()


def kill_chromium_processes():
    if os.name == "nt":  # Windows
        os.system("taskkill /im chrome.exe /f")
    else:  # Linux/Mac
        os.system("pkill -9 chrome")


class Parser:

    def __init__(self, headless: bool = True) -> None:
        logger.info("Create Parser object, set settings for Browser")
        self.settings = Settings()
        self.settings.set_language("en")
        self.settings.set_raise_when_wait_failed(True)
        self.settings.set_raise_when_ele_not_found(True)
        self.co = ChromiumOptions().new_env()  # new_env for new browser
        window_size = (
            f"{random.randrange(800,1200)},{random.randrange(600,920)}"
        )

        self.co.set_argument("--window-size", window_size)

        # self.co.set_argument(
        #     "--blink-settings=autoplayPolicy=DocumentUserActivationRequired"
        # )
        self.co.set_argument("--no-sandbox")
        self.co.set_argument("--disable-accelerated-video-decode")
        self.co.set_argument("--disable-gpu")
        self.co.set_argument("--disable-dev-shm-usage")
        self.co.set_argument("--disable-software-rasterizer")

        # co.set_browser_path(r"chromium\bin\chrome.exe")
        self.co.headless(headless)
        self.co.no_imgs(True).mute(True)
        self.co.auto_port(True)
        # self.co.set_paths(address="chromium", local_port='9222')
        # self.co.set_browser_path('')
        # self.co.set_debugger_address('chromium:3000')
        self.co.set_user_agent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        )
        self.browser = None
        while not self.browser:
            try:
                self.browser = Chromium(self.co)
                logger.success("Browser object was succefully create!")
            except BrowserConnectError:
                logger.error(
                    "can't connect to browser - try killing browser process..."
                )
                kill_chromium_processes()
                time.sleep(3)

        # self.co.set_argument('--disable-image-animation')
        # self.co.save(path=r"settings.ini")

    def __del__(self):
        # self.browser.quit()
        kill_chromium_processes()
        logger.info(
            "Parser object was deleted, chromium process has been killed"
        )

    def _restart_browser(self):
        """Есть нужда перезапускать, если брузер 'застрял'"""
        kill_chromium_processes()
        self.browser = Chromium(self.co)

    def _parse_price(self, marketplace_response: str | None) -> str | None:
        """универсальная для ozon и wb"""
        if marketplace_response:
            if isinstance(marketplace_response, str):
                if marketplace_response != "":
                    if "₽" in marketplace_response:
                        ruble_index = marketplace_response.find("₽")
                        return "".join(
                            marketplace_response[0:ruble_index].split()
                        )
        return None

    def get_data(self, url):
        match url:
            case url if "ozon" in url:
                return self.get_ozon_price(url)
            case url if "wildberries" in url:
                return self.get_wb_price(url)
            case _:
                return None

    def get_ozon_price(self, url: str) -> dict[str, str] | None:
        try:
            self.tab = self.browser.latest_tab
        except Exception as e:
            logger.error(f"problem then open tab: {e}")

        if not isinstance(self.tab, str):
            try:
                logger.info("loading page ozon....")
                if self.tab.get(url):
                    res = self.tab.ele(
                        'xpath://div[@data-widget="webPrice"]'
                    ).text
                    price = self._parse_price(res)
                    res = (
                        self.tab.ele(
                            'xpath://div[@data-widget="webProductHeading"]'
                        )
                        .ele("tag:h1")
                        .text  # type: ignore
                    )
                    name = res
                    if price:
                        if price.isdigit() and isinstance(price, str):
                            return {"Price": price, "Name": name}
            except ElementNotFoundError:
                logger.error(
                    f"No element find on the page - page does not exits or wrong"
                )
            except Exception as e:
                logger.error(f"Problem browser: {e}")
                self._restart_browser()
        else:
            return None
        return None

    def get_wb_price(self, url: str) -> dict[str, str] | None:
        try:
            self.tab = self.browser.latest_tab
        except Exception as e:
            logger.error(f"problem then open tab: {e}")

        if not isinstance(self.tab, str):
            try:
                logger.info("loading page wb....")
                if self.tab.get(url):
                    res = self.tab.ele("@class=price-block__price")
                    price = self._parse_price(res.text)
                    res = self.tab.ele("@class=product-page__title")
                    name = res.text
                    if price:
                        if price.isdigit():
                            return {"Price": price, "Name": name}
            except ElementNotFoundError:
                logger.error(
                    f"No element find on the page - page does not exits or wrong"
                )
            except Exception as e:
                logger.error(f"Problem browser: {e}")
                self._restart_browser()
        else:
            return None
        return None


if __name__ == "__main__":
    parser = Parser()
    res = parser.get_ozon_price(
        "https://www.ozon.ru/product/makarony-makfa-makfa-rozhki-gladkie-vysshiy-sort-400g-makaronnye-izdeliya-komplekt-iz-4-sht-197877686/"
    )
    print(res)

    # res = parser.get_wb_price(
    #     "https://www.wildberries.ru/catalog/272792079/detail.aspx"
    # )
    # print(res)
    logger.info("End")
