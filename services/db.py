"""

    opponents: для хранения данных о конкурентах.
    goods: для хранения данных о товарах.
    goods_opponents: для обработки связи "многие ко многим" массив  связка "нашего товара" и товара конкурента
    для корректной работы ON DELETE CASCADE обзятельно сделать
    PRAGMA foreign_keys = ON;

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
    FOREIGN KEY (good_sku) REFERENCES goods(sku) ON DELETE CASCADE,
    FOREIGN KEY (opponent_id) REFERENCES opponents(id) ON DELETE CASCADE,
    PRIMARY KEY (good_sku, opponent_id)
);

"""

import datetime
import os
import random
import sqlite3

from loguru import logger

from ..models import Item, Opponents

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.sqlite3")
TIME_ZONE = datetime.timezone(datetime.timedelta(hours=5))  #  (UTC+5)


def db_connection(func):
    """Декоратор для всех соединений с БД"""

    def wrapper(*args, **kwargs):
        logger.info("Открываем соединение с базой")
        try:
            conn = sqlite3.connect(db_path)
            conn.execute(
                "PRAGMA foreign_keys = ON;"
            )  # Включаем внешние ключи
            curs = conn.cursor()
            result = func(curs=curs, *args, **kwargs)
            conn.commit()
            conn.close()
            logger.info("Закрыли соединение с базой")
            return result
        except Exception as e:
            logger.error(f"Ошибка работы с базой: {e}")
            conn.close()

    return wrapper


@db_connection
def add_good(item: Item, curs: sqlite3.Cursor | None = None) -> bool | None:
    if curs is not None:
        sql_check = "SELECT COUNT(*) FROM goods WHERE sku = ?"
        curs.execute(sql_check, (item.sku,))
        if curs.fetchone()[0] > 0:
            logger.warning(f"Товар с SKU {item.sku} уже существует в базе")
            return None
        sql_insert = "INSERT INTO goods (sku, name, url, price, timestamp) VALUES (?, ?, ?, ?, ?)"
        curs.execute(
            sql_insert,
            (item.sku, item.name, item.url, item.price, item.timestamp),
        )
        logger.info(f"Товар с SKU {item.sku} успешно добавлен.")
        return True


@db_connection
def add_opponent(
    sku: str, opponent: Opponents, curs: sqlite3.Cursor | None = None
):
    """добавляем конкурента в базу конкурентов и в таблицу для связки"""
    if curs is None:
        raise ValueError("Курсор базы данных не был передан в функцию.")

    # logger.info(opponent)
    sql_check = "SELECT COUNT(*) FROM opponents WHERE  id = ?"
    curs.execute(sql_check, (opponent.id,))
    if curs.fetchone()[0] > 0:
        logger.warning(f"Товар с SKU {sku} уже существует в таблице")
        return None
    sql_insert = "INSERT INTO opponents (id, url, current_price, prev_price, price_change) VALUES (?, ?, ?, ?, ?)"
    # logger.debug(sql_insert)
    curs.execute(
        sql_insert,
        (
            opponent.id,
            opponent.url,
            opponent.current_price,
            opponent.prev_price,
            opponent.price_change,
        ),
    )
    logger.info(f"Товар с SKU {sku} успешно добавлен в opponents.")
    sql_insert = (
        "INSERT INTO goods_opponents (good_sku, opponent_id) VALUES (?, ?)"
    )
    curs.execute(
        sql_insert,
        (sku, opponent.id),
    )
    logger.info(
        f"Товар конкурентов  с SKU {opponent.id} успешно добавлен в goods_opponents."
    )
    return True


@db_connection
def remove_opponent(
    id: str, curs: sqlite3.Cursor | None = None
) -> bool | None:
    if curs is None:
        logger.error("Cursor not exist during delete opponent")
        raise ValueError("Курсор базы данных не был передан в функцию.")

    sql_check = "SELECT COUNT(*) FROM opponents WHERE  id = ?;"
    curs.execute(sql_check, (id,))

    if curs.fetchone()[0] == 0:
        logger.warning(f"Товар  конкурента с SKU {id} отсутсвует в таблице")
        return None
    else:
        sql_delete = "DELETE FROM opponents where id = ?;"
        curs.execute(sql_delete, (id,))
        logger.info(f"Success delete oponent {id}")
        return True


@db_connection
def remove_good(sku: str, curs: sqlite3.Cursor | None = None) -> bool | None:
    if curs is None:
        logger.error("Cursor not exist during delete good with sku: {sku}")
        raise ValueError("Курсор базы данных не был передан в функцию.")

    sql_check = "SELECT COUNT(*) FROM goods WHERE  sku = ?;"
    curs.execute(sql_check, (sku,))

    if curs.fetchone()[0] == 0:
        logger.warning(f"Товар с SKU {sku} отсутсвует в таблице")
        return None
    else:
        sql_delete = "DELETE FROM goods where sku = ?;"
        curs.execute(sql_delete, (sku,))
        logger.info(f"Success delete oponent {sku}")
        return True


if __name__ == "__main__":
    # for i in range(10):
    #     add_good(
    #         Goods(
    #             sku=str(random.randrange(1000000, 10000000000)),
    #             name="Памперсы",
    #             url="https://www.ozon.ru/product/mysh-besprovodnaya-logitech-m170-grey-1731812484/?at=36tWvgxp7uPE5Y6wCEZk8ELhQQYw4mHvAL8VkIlr9EoV",
    #             price=123.1,
    #             opponents_id=[],
    #             timestamp=str(datetime.datetime.now(TIME_ZONE)),
    #         ),
    #     )
    add_opponent(
        "8642362",
        Opponents(
            id=str("123"),
            url="https://www.ozon.ru/product/mysh-besprovodnaya-logitech-m170-grey-1731812484/?at=36tWvgxp7uPE5Y6wCEZk8ELhQQYw4mHvAL8VkIlr9EoV",
            current_price=12.0,
        ),
    )
    remove_opponent("123")
    remove_good("2323234324")
