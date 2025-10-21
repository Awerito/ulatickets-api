import os
import asyncio
import httpx
from datetime import datetime

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")


def get_id(d: dict) -> str:
    return d.get("id") or d.get("_id") or ""


EVENTS = [
    {
        "name": "Rock en el Parque",
        "category": "music",
        "date": datetime(2025, 12, 5, 20, 0, 0).isoformat(),
        "location": "Estadio Nacional",
        "image": "https://placehold.co/600x400?text=Rock+en+el+Parque",
        "tickets": [
            {"type": "General", "price": 25000.0, "available": 120},
            {"type": "VIP", "price": 60000.0, "available": 30},
        ],
    },
    {
        "name": "Festival de Comedia",
        "category": "theater",
        "date": datetime(2025, 11, 2, 21, 0, 0).isoformat(),
        "location": "Teatro Municipal",
        "image": "https://placehold.co/600x400?text=Festival+de+Comedia",
        "tickets": [
            {"type": "General", "price": 15000.0, "available": 200},
            {"type": "Premium", "price": 35000.0, "available": 50},
        ],
    },
]


async def create_events(client: httpx.AsyncClient):
    print("🎟️ Creating events...")
    event_ids: list[str] = []
    for ev in EVENTS:
        r = await client.post("/events", json=ev)
        if r.status_code == 201:
            data = r.json()
            eid = get_id(data)
            print(f"  ✅ {data.get('name','<no-name>')} created ({eid})")
            if eid:
                event_ids.append(eid)
        else:
            print(f"  ❌ Failed to create {ev['name']}: {r.status_code} {r.text}")
    return event_ids


async def create_reservation(client: httpx.AsyncClient, event_id: str):
    print(f"\n📦 Creating reservation for event {event_id}...")
    payload = {"event_id": event_id, "items": [{"type": "General", "quantity": 2}]}
    r = await client.post("/reservations", json=payload)
    if r.status_code == 201:
        data = r.json()
        print(
            f"  ✅ Reservation created: {data['reservation_id']} total={data['total_price']}"
        )
        return data["reservation_id"]
    print(f"  ❌ Failed to create reservation: {r.status_code} {r.text}")
    return None


async def checkout_reservation(client: httpx.AsyncClient, reservation_id: str):
    print(f"\n💳 Performing checkout for {reservation_id}...")
    payload = {
        "reservation_id": reservation_id,
        "buyer": {"name": "Diego Muñoz", "email": "diego@example.com"},
    }
    r = await client.post("/checkout", json=payload)
    if r.status_code == 201:
        data = r.json()
        pid = get_id(data)
        print(f"  ✅ Checkout complete, purchase {pid} total={data['total_price']}")
        return pid
    print(f"  ❌ Checkout failed: {r.status_code} {r.text}")
    return None


async def main():
    async with httpx.AsyncClient(base_url=API_BASE, timeout=10.0) as client:
        events = await create_events(client)
        if not events:
            print("⚠️ No events created, aborting.")
            return
        reservation_id = await create_reservation(client, events[0])
        if reservation_id:
            await checkout_reservation(client, reservation_id)
    print("\n✅ Bootstrap process complete.")


if __name__ == "__main__":
    asyncio.run(main())
