from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body

from app.database import MongoDBConnectionManager
from app.models.event import Event, PaginatedEvents
from app.models.common import to_oid, parse_mongo, PatchResponse

router = APIRouter(tags=["Events"])


@router.get("/events", response_model=PaginatedEvents)
async def list_events(
    q: str | None = None,
    category: str | None = None,
    sort: str | None = Query(None, pattern="^(-?date)$"),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
):
    """
    ## 📚 Listar eventos

    Devuelve todos los eventos disponibles con filtros opcionales y paginación.

    **Parámetros de consulta**
    - `q`: texto a buscar en el nombre del evento (búsqueda parcial)
    - `category`: filtra por categoría exacta
    - `sort`: `date` o `-date` para ordenar por fecha asc/desc, `category` o
      `-category` para ordenar por categoría asc/desc
    - `limit`: número máximo de resultados por página
    - `page`: número de página

    **Ejemplo de respuesta**
    ```json
    {
      "data": [
        {
          "_id": "68f7b9d771fbcc686dd144e8",
          "name": "Rock en el Parque",
          "category": "music",
          "date": "2025-12-05T20:00:00Z",
          "location": "Estadio Nacional",
          "image": "https://placehold.co/600x400?text=Rock+en+el+Parque",
          "tickets": [
            {"type": "General", "price": 25000.0, "available": 120},
            {"type": "VIP", "price": 60000.0, "available": 30}
          ]
        }
      ],
      "page": 1,
      "limit": 20,
      "total": 1
    }
    ```
    """
    async with MongoDBConnectionManager() as db:
        query: dict = {}
        if q:
            query["name"] = {"$regex": q, "$options": "i"}
        if category:
            query["category"] = category

        cursor = db.events.find(query)
        if sort:
            field = sort.lstrip("-")
            direction = -1 if sort.startswith("-") else 1
            cursor = cursor.sort(field, direction)

        total = await db.events.count_documents(query)
        skip = (page - 1) * limit

        docs = [Event(**doc) async for doc in cursor.skip(skip).limit(limit)]
        return {"data": docs, "page": page, "limit": limit, "total": total}


@router.post("/events", response_model=Event, status_code=201)
async def create_event(event: Event = Body(...)):
    """
    ## 🆕 Crear evento

    Crea un nuevo evento con sus tipos de ticket y disponibilidad inicial.

    **Ejemplo de solicitud**
    ```json
    {
      "name": "Orquesta Sinfónica",
      "category": "music",
      "date": "2025-12-20T19:00:00Z",
      "location": "Teatro del Lago",
      "image": "https://placehold.co/600x400?text=Orquesta+Sinfónica",
      "tickets": [
        {"type": "Platea", "price": 40000, "available": 120},
        {"type": "Balcón", "price": 25000, "available": 150}
      ]
    }
    ```

    **Respuesta**
    - `201 Created` → Objeto del evento creado con su `_id`
    """
    payload = event.model_dump(by_alias=True, exclude={"id"})
    payload.pop("_id", None)

    if isinstance(payload.get("date"), str):
        payload["date"] = datetime.fromisoformat(payload["date"].replace("Z", "+00:00"))

    async with MongoDBConnectionManager() as db:
        res = await db.events.insert_one(payload)
        created = await db.events.find_one({"_id": res.inserted_id})
        return parse_mongo(created, Event)


@router.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """
    ## 🔎 Obtener evento

    Retorna los datos completos de un evento a partir de su `event_id`
    (de tipo [ObjectId][oid]).

    **Errores**
    - `404` → Evento no encontrado

    [oid]: https://www.mongodb.com/docs/manual/reference/bson-types/#objectid
    """
    async with MongoDBConnectionManager() as db:
        doc = await db.events.find_one({"_id": to_oid(event_id)})
        return parse_mongo(doc, Event)


@router.patch("/events/{event_id}", response_model=PatchResponse)
async def update_event(event_id: str, updates: dict = Body(...)):
    """
    ## ✏️ Actualizar evento

    Permite modificar campos específicos de un evento existente.

    **Ejemplo**
    ```json
    {
      "name": "Rock 2025 – Edición Verano",
      "tickets": [
        {"type": "General", "price": 28000, "available": 100}
      ]
    }
    ```

    **Errores**
    - `404` → Evento no encontrado
    """
    if "date" in updates and isinstance(updates["date"], str):
        updates["date"] = datetime.fromisoformat(updates["date"].replace("Z", "+00:00"))

    async with MongoDBConnectionManager() as db:
        res = await db.events.update_one({"_id": to_oid(event_id)}, {"$set": updates})
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"updated": True}


@router.delete("/events/{event_id}", status_code=204)
async def delete_event(event_id: str):
    """
    ## 🗑️ Eliminar evento

    Elimina un evento por su identificador.

    **Respuesta**
    - `204 No Content` → Eliminado exitosamente
    - `404 Not Found` → No existe el evento
    """
    async with MongoDBConnectionManager() as db:
        res = await db.events.delete_one({"_id": to_oid(event_id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        return None
