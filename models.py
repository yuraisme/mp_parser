import datetime
from typing import List

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class Opponents(BaseModel):
    """Храним в отдельном классе"""

    id: str = ""
    url: str = ""
    current_price: float = 0.0
    prev_price: float = 0.0
    price_change: float = 0.0


class Item(BaseModel):
    """Наши товары, на конкурентов храним ссылки"""

    sku: str = ""
    name: str = ""
    url: str = ""
    price: float = 0.0
    opponents_id: List[str] = []
    timestamp: datetime.datetime
