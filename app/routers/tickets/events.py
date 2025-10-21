from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body
from app.database import MongoDBConnectionManager
from app.models.event import Event
from app.models.common import to_oid, parse_mongo

router = APIRouter(tags=["Events"])


@router.get("/events", response_model=dict)
async def list_events(
    q: str | None = None,
    category: str | None = None,
    sort: str | None = Query(None, pattern="^(-?date)$"),
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
):
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
    async with MongoDBConnectionManager() as db:
        doc = await db.events.find_one({"_id": to_oid(event_id)})
        return parse_mongo(doc, Event)


@router.patch("/events/{event_id}", response_model=dict)
async def update_event(event_id: str, updates: dict = Body(...)):
    if "date" in updates and isinstance(updates["date"], str):
        updates["date"] = datetime.fromisoformat(updates["date"].replace("Z", "+00:00"))

    async with MongoDBConnectionManager() as db:
        res = await db.events.update_one({"_id": to_oid(event_id)}, {"$set": updates})
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"updated": True}


@router.delete("/events/{event_id}", status_code=204)
async def delete_event(event_id: str):
    async with MongoDBConnectionManager() as db:
        res = await db.events.delete_one({"_id": to_oid(event_id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Event not found")
        return None
