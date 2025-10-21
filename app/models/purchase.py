from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.models.common import MongoBase


class Ticket(BaseModel):
    code: str
    type: str


class Purchase(MongoBase):
    reservation_id: str
    event_id: str
    tickets: List[Ticket]
    buyer: dict
    total_price: float
    confirmed_at: datetime
