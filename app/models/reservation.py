from datetime import datetime
from pydantic import BaseModel, Field

from app.models.common import MongoBase


class ReservationItem(BaseModel):
    type: str
    quantity: int = Field(..., gt=0, description="Number of tickets to reserve")


class Reservation(MongoBase):
    event_id: str
    items: list[ReservationItem]
    total_price: float
    status: str = "PENDING"
    created_at: datetime
    expires_at: datetime


class ReservationCreateInput(BaseModel):
    event_id: str = Field(..., description="Event ObjectId as string")
    items: list[ReservationItem] = Field(
        ..., min_length=1, description="List of ticket types and quantities to reserve"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": "68f7b9d771fbcc686dd144e8",
                "items": [{"type": "General", "quantity": 2}],
            }
        }
    }


class ReservationCreateResponse(BaseModel):
    reservation_id: str = Field(
        ..., description="Unique identifier for the reservation"
    )
    expires_at: datetime = Field(
        ..., description="Timestamp when the reservation expires"
    )
    total_price: float = Field(..., description="Total price of the reservation")
    status: str = Field(..., description="Current status of the reservation")
