from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.models.common import MongoBase


class ReservationItem(BaseModel):
    type: str
    quantity: int


class Reservation(MongoBase):
    event_id: str
    items: List[ReservationItem]
    total_price: float
    status: str = "PENDING"
    created_at: datetime
    expires_at: datetime
