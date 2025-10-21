from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from app.database import MongoDBConnectionManager
from app.models.purchase import Purchase
from app.models.common import to_oid, parse_mongo

router = APIRouter(tags=["Purchases"])


@router.post("/checkout", response_model=Purchase, status_code=201)
async def checkout(payload: dict = Body(...)):
    res_id = payload.get("reservation_id")
    buyer = payload.get("buyer", {})
    if not res_id or not buyer.get("email"):
        raise HTTPException(status_code=400, detail="Invalid checkout request")

    async with MongoDBConnectionManager() as db:
        reservation = await db.reservations.find_one({"_id": to_oid(res_id)})
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")
        if reservation["status"] != "PENDING":
            raise HTTPException(status_code=400, detail="Reservation is not active")

        await db.reservations.update_one(
            {"_id": reservation["_id"]}, {"$set": {"status": "CONFIRMED"}}
        )

        tlist: list[dict] = []
        seq = 1
        for it in reservation["items"]:
            qty = int(it["quantity"])
            for _ in range(qty):
                tlist.append(
                    {
                        "code": f"T-{str(reservation['event_id'])[-3:]}-{seq:04}",
                        "type": it["type"],
                    }
                )
                seq += 1

        purchase_doc = Purchase(
            reservation_id=str(reservation["_id"]),
            event_id=str(reservation["event_id"]),
            tickets=tlist,
            buyer=buyer,
            total_price=float(reservation["total_price"]),
            confirmed_at=datetime.utcnow(),
        ).model_dump(by_alias=True, exclude={"id"})

        res = await db.purchases.insert_one(purchase_doc)
        created = await db.purchases.find_one({"_id": res.inserted_id})
        return parse_mongo(created, Purchase)


@router.get("/purchases/{purchase_id}", response_model=Purchase)
async def get_purchase(purchase_id: str):
    async with MongoDBConnectionManager() as db:
        doc = await db.purchases.find_one({"_id": to_oid(purchase_id)})
        return parse_mongo(doc, Purchase)
