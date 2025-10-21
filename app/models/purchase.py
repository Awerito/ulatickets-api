from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.models.common import MongoBase


class Ticket(BaseModel):
    code: str
    type: str


class BuyerInfo(BaseModel):
    name: str = Field(..., description="Full name of the buyer")
    email: EmailStr = Field(..., description="Valid email address of the buyer")


class Purchase(MongoBase):
    reservation_id: str
    event_id: str
    tickets: list[Ticket]
    buyer: BuyerInfo
    total_price: float
    confirmed_at: datetime


class ReservationBuyerInput(BaseModel):
    reservation_id: str = Field(..., description="Reservation ObjectId as string")
    buyer: BuyerInfo = Field(..., description="Buyer information")

    model_config = {
        "json_schema_extra": {
            "example": {
                "reservation_id": "68f7bb32b3d1304d0e014070",
                "buyer": {"name": "Cliente Demo", "email": "demo@example.com"},
            }
        }
    }
