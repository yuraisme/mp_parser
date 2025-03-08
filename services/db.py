"""
    
    opponents: для хранения данных о конкурентах.
    goods: для хранения данных о товарах.
    goods_opponents: для обработки связи "многие ко многим" массив  связка "нашего товара" и товара конкурента

CREATE TABLE opponents (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL DEFAULT '',
    current_price REAL NOT NULL DEFAULT 0.0,
    prev_price REAL NOT NULL DEFAULT 0.0,
    price_change REAL NOT NULL DEFAULT 0.0
);

CREATE TABLE goods (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    price REAL NOT NULL DEFAULT 0.0,
    timestamp DATE NOT NULL
);

CREATE TABLE goods_opponents (
    good_sku TEXT,
    opponent_id TEXT,
    FOREIGN KEY (good_sku) REFERENCES goods(sku),
    FOREIGN KEY (opponent_id) REFERENCES opponents(id),
    PRIMARY KEY (good_sku, opponent_id)
);

"""

import datetime
import os
import sqlite3

from loguru import logger

from ..models import Goods

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.sqlite3")


def db_connection(func):
    """Декоратор для всех соединений с БД"""

    def wrapper(*args, **kwargs):
        logger.info("Открываем соединение с базой")
        print(os.getcwd())
        conn = sqlite3.connect(db_path)
        curs = conn.cursor()
        result = func(curs, *args, **kwargs)
        conn.commit()
        conn.close()
        return result

    return wrapper


@db_connection
def add_good(curs, good: Goods):
    if curs is not None:
        sql_check = "SELECT COUNT(*) FROM goods WHERE sku = ?"
        curs.execute(sql_check, (good.sku,))
        if curs.fetchone()[0] > 0:
            print(f"Товар с SKU {good.sku} уже существует.")
            return
        sql_insert = "INSERT INTO goods (sku, name, url, price, timestamp) VALUES (?, ?, ?, ?, ?)"
        curs.execute(
            sql_insert,
            (good.sku, good.name, good.url, good.price, good.timestamp),
        )
        print(f"Товар с SKU {good.sku} успешно добавлен.")


if __name__ == "__main__":
    add_good(
        good=Goods(
            sku="12314324",
            name="Памперсы",
            url="https://www.ozon.ru/product/mysh-besprovodnaya-logitech-m170-grey-1731812484/?at=36tWvgxp7uPE5Y6wCEZk8ELhQQYw4mHvAL8VkIlr9EoV",
            price=123.1,
            opponents_id=[],
            timestamp=datetime.datetime.now(),
        ),
    )
