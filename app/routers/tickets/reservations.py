from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Body

from app.database import MongoDBConnectionManager
from app.models.common import to_oid, parse_mongo
from app.models.reservation import (
    Reservation,
    ReservationCreateResponse,
    ReservationCreateInput,
)

router = APIRouter(tags=["Reservations"])


@router.post("/reservations", response_model=ReservationCreateResponse, status_code=201)
async def create_reservation(payload: ReservationCreateInput = Body(...)):
    """
    ## 📦 Crear reserva

    Crea una **reserva temporal** para un evento.
    El stock se **descuenta inmediatamente** del evento.

    **Ejemplo de solicitud**
    ```json
    {
      "event_id": "68f7b9d771fbcc686dd144e8",
      "items": [
        {"type": "General", "quantity": 2}
      ]
    }
    ```

    **Ejemplo de respuesta**
    ```json
    {
      "reservation_id": "68f7bb32b3d1304d0e014070",
      "expires_at": "2025-10-21T16:41:25.921Z",
      "total_price": 50000.0,
      "status": "PENDING"
    }
    ```

    **Errores frecuentes**
    - `400 Invalid ObjectId` → IDs deben ser [ObjectId][oid] válidos.
    - `400 Not enough 'TYPE' tickets` → stock insuficiente.
    - `404 Event not found` → evento no existe.

    [oid]: https://www.mongodb.com/docs/manual/reference/bson-types/#objectid
    """
    event_id = payload.event_id
    items = payload.items or []
    if not event_id or not items:
        raise HTTPException(status_code=400, detail="Invalid request")

    async with MongoDBConnectionManager() as db:
        event = await db.events.find_one({"_id": to_oid(event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        tickets = event.get("tickets", [])
        type_index = {t["type"]: i for i, t in enumerate(tickets)}
        total = 0.0

        for i in items:
            it = i.model_dump()
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

        for i in items:
            it = i.model_dump()
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
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=2),
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
    """
    ## 🧾 Consultar reserva

    Retorna los datos de una reserva.
    Si el tiempo de expiración (`expires_at`) ya pasó, el estado pasa a `EXPIRED`.

    **Ejemplo de respuesta**
    ```json
    {
      "_id": "68f7bb32b3d1304d0e014070",
      "event_id": "68f7b9d771fbcc686dd144e8",
      "items": [{"type": "General", "quantity": 2}],
      "total_price": 50000.0,
      "status": "PENDING",
      "created_at": "2025-10-21T16:39:25.921Z",
      "expires_at": "2025-10-21T16:41:25.921Z"
    }
    ```

    **Errores**
    - `404 Reservation not found`
    """
    async with MongoDBConnectionManager() as db:
        doc = await db.reservations.find_one({"_id": to_oid(res_id)})
        if (
            doc
            and doc["status"] == "PENDING"
            and datetime.now(timezone.utc) > doc["expires_at"]
        ):
            await db.reservations.update_one(
                {"_id": doc["_id"]}, {"$set": {"status": "EXPIRED"}}
            )
            doc["status"] = "EXPIRED"
        return parse_mongo(doc, Reservation)


@router.delete("/reservations/{res_id}", status_code=204)
async def cancel_reservation(res_id: str):
    """
    ## ❌ Cancelar reserva

    Elimina una reserva antes de su vencimiento.

    **Respuesta**
    - `204 No Content` → cancelada correctamente.
    - `404 Not Found` → no existe.
    """
    async with MongoDBConnectionManager() as db:
        res = await db.reservations.delete_one({"_id": to_oid(res_id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return None
