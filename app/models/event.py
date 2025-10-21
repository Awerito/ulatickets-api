from datetime import datetime
from pydantic import Field, BaseModel
from typing import List

from app.models.common import MongoBase


class TicketType(BaseModel):
    type: str
    price: float
    available: int


class Event(MongoBase):
    name: str
    category: str
    date: datetime
    location: str
    image: str | None = None
    tickets: List[TicketType] = Field(default_factory=list)
