from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Body

from app.database import MongoDBConnectionManager
from app.models.purchase import Purchase, ReservationBuyerInput, BuyerInfo
from app.models.common import to_oid, parse_mongo

router = APIRouter(tags=["Purchases"])


@router.post("/checkout", response_model=Purchase, status_code=201)
async def checkout(payload: ReservationBuyerInput = Body(...)):
    """
    ## 💳 Checkout

    Confirma una reserva pendiente (`PENDING`) y genera una **compra** (`Purchase`)
    con tickets emitidos.

    **Ejemplo de solicitud**
    ```json
    {
      "reservation_id": "68f7bb32b3d1304d0e014070",
      "buyer": {"name": "Cliente Demo", "email": "demo@example.com"}
    }
    ```

    **Ejemplo de respuesta**
    ```json
    {
      "_id": "68f7bb32b3d1304d0e014071",
      "reservation_id": "68f7bb32b3d1304d0e014070",
      "event_id": "68f7b9d771fbcc686dd144e8",
      "tickets": [
        {"code": "T-4e8-0001", "type": "General"},
        {"code": "T-4e8-0002", "type": "General"}
      ],
      "buyer": {"name": "Cliente Demo", "email": "demo@example.com"},
      "total_price": 50000.0,
      "confirmed_at": "2025-10-21T16:39:40.123Z"
    }
    ```

    **Errores**
    - `400 Invalid checkout request` → datos incompletos.
    - `400 Reservation is not active` → reserva expirada o ya confirmada.
    - `404 Reservation not found`.
    """
    res_id = payload.reservation_id
    buyer = payload.buyer.model_dump()
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

        tlist = []
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
            buyer=BuyerInfo(**buyer),
            total_price=float(reservation["total_price"]),
            confirmed_at=datetime.now(timezone.utc),
        ).model_dump(by_alias=True, exclude={"id"})

        res = await db.purchases.insert_one(purchase_doc)
        created = await db.purchases.find_one({"_id": res.inserted_id})
        return parse_mongo(created, Purchase)


@router.get("/purchases/{purchase_id}", response_model=Purchase)
async def get_purchase(purchase_id: str):
    """
    ## 🧾 Obtener compra

    Devuelve la información completa de una compra, incluyendo el comprador
    y los tickets generados.

    **Ejemplo de respuesta**
    ```json
    {
      "_id": "68f7bb32b3d1304d0e014071",
      "event_id": "68f7b9d771fbcc686dd144e8",
      "tickets": [
        {"code": "T-4e8-0001", "type": "General"}
      ],
      "buyer": {"name": "Cliente Demo", "email": "demo@example.com"},
      "total_price": 50000.0,
      "confirmed_at": "2025-10-21T16:39:40.123Z"
    }
    ```

    **Errores**
    - `404 Purchase not found`
    """
    async with MongoDBConnectionManager() as db:
        doc = await db.purchases.find_one({"_id": to_oid(purchase_id)})
        return parse_mongo(doc, Purchase)
