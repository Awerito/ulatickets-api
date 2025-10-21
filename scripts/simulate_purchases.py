import os
import asyncio
import httpx

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")


async def list_events(client: httpx.AsyncClient) -> list[dict]:
    r = await client.get("/events", params={"limit": 50})
    r.raise_for_status()
    return r.json().get("data", [])


def pick_item(event: dict) -> dict | None:
    for t in event.get("tickets", []):
        if int(t.get("available", 0)) >= 2:
            return {"type": t["type"], "quantity": 2}
    return None


async def reserve(client: httpx.AsyncClient, event_id: str, item: dict) -> str | None:
    print(
        f"\n📦 Creando reserva para evento {event_id} ({item['type']} x{item['quantity']})..."
    )
    r = await client.post("/reservations", json={"event_id": event_id, "items": [item]})
    if r.status_code != 201:
        print(f"❌ Error creando reserva: {r.status_code} {r.text}")
        return None
    data = r.json()
    print(
        f"✅ Reserva creada: {data.get('reservation_id')} total={data.get('total_price')}"
    )
    return data.get("reservation_id")


async def checkout(client: httpx.AsyncClient, reservation_id: str) -> dict | None:
    print(f"\n💳 Realizando checkout para reserva {reservation_id}...")
    payload = {
        "reservation_id": reservation_id,
        "buyer": {"name": "Cliente Demo", "email": "demo@example.com"},
    }
    r = await client.post("/checkout", json=payload)
    if r.status_code != 201:
        print(f"❌ Error en checkout: {r.status_code} {r.text}")
        return None
    data = r.json()
    pid = data.get("purchase_id") or data.get("id") or data.get("_id")
    print(f"🎉 Compra confirmada: {pid} total={data.get('total_price')}")
    return data


async def main():
    async with httpx.AsyncClient(base_url=API_BASE, timeout=10.0) as client:
        print("🎟️ Listando eventos disponibles...")
        events = await list_events(client)
        if not events:
            print("⚠️ No hay eventos disponibles.")
            return

        purchases: list[dict] = []
        for ev in events[:2]:
            ev_id = ev.get("id") or ev.get("_id")
            item = pick_item(ev)
            if not ev_id or not item:
                print(
                    f"⚠️ Evento sin stock suficiente: {ev.get('name', '<sin nombre>')}"
                )
                continue

            res_id = await reserve(client, ev_id, item)
            if not res_id:
                continue

            p = await checkout(client, res_id)
            if p:
                purchases.append(p)

        print(f"\n✅ Simulación completa: {len(purchases)} compras exitosas.")


if __name__ == "__main__":
    asyncio.run(main())
