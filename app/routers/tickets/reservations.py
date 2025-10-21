from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Body
from app.database import MongoDBConnectionManager
from app.models.reservation import Reservation
from app.models.common import to_oid, parse_mongo

router = APIRouter(tags=["Reservations"])


@router.post("/reservations", response_model=dict, status_code=201)
async def create_reservation(payload: dict = Body(...)):
    event_id = payload.get("event_id")
    items = payload.get("items", [])
    if not event_id or not items:
        raise HTTPException(status_code=400, detail="Invalid request")

    async with MongoDBConnectionManager() as db:
        event = await db.events.find_one({"_id": to_oid(event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        tickets = event.get("tickets", [])
        type_index = {t["type"]: i for i, t in enumerate(tickets)}
        total = 0.0

        for it in items:
            ttype = it["type"]
            qty = int(it["quantity"])
            if ttype not in type_index:
                raise HTTPException(
                    status_code=400, detail=f"Unknown ticket type '{ttype}'"
                )
            t = tickets[type_index[ttype]]
            if t["available"] < qty:
                raise HTTPException(
                    status_code=400, detail=f"Not enough '{ttype}' tickets"
                )
            total += float(t["price"]) * qty

        for it in items:
            idx = type_index[it["type"]]
            tickets[idx]["available"] -= int(it["quantity"])

        await db.events.update_one(
            {"_id": event["_id"]}, {"$set": {"tickets": tickets}}
        )

        reservation_doc = Reservation(
            event_id=str(event["_id"]),
            items=items,
            total_price=total,
            status="PENDING",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=2),
        ).model_dump(by_alias=True, exclude={"id"})

        res = await db.reservations.insert_one(reservation_doc)
        reservation_id = str(res.inserted_id)
        print("DEBUG reservation_id:", reservation_id)  # opcional
        return {
            "reservation_id": reservation_id,
            "expires_at": reservation_doc["expires_at"].isoformat(),
            "total_price": total,
            "status": "PENDING",
        }


@router.get("/reservations/{res_id}", response_model=Reservation)
async def get_reservation(res_id: str):
    async with MongoDBConnectionManager() as db:
        doc = await db.reservations.find_one({"_id": to_oid(res_id)})
        if doc and doc["status"] == "PENDING" and datetime.utcnow() > doc["expires_at"]:
            await db.reservations.update_one(
                {"_id": doc["_id"]}, {"$set": {"status": "EXPIRED"}}
            )
            doc["status"] = "EXPIRED"
        return parse_mongo(doc, Reservation)


@router.delete("/reservations/{res_id}", status_code=204)
async def cancel_reservation(res_id: str):
    async with MongoDBConnectionManager() as db:
        res = await db.reservations.delete_one({"_id": to_oid(res_id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return None
