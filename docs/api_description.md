# 🎟️ Flujo de Venta de Entradas

Esta API sigue el estilo [REST][rest] utilizando [HTTP Methods][http] estándar
(`GET`, `POST`, `PATCH`, `DELETE`) y formato [JSON][json] para la comunicación.

Los identificadores de documentos son de tipo [ObjectId][oid],
las fechas se expresan en formato [ISO 8601][iso8601],
y las respuestas usan [HTTP Status Codes][status] para indicar resultados.

1) **Creación de eventos** (`POST /events`)  
   Define nombre, categoría, fecha, ubicación, imagen y **tipos de ticket**
(precio y disponibilidad).

2) **Exploración/listado** (`GET /events`)  
   Filtra por categoría o busca por nombre. El frontend muestra detalle:
imagen, fecha, ubicación y stock por tipo de ticket.

3) **Reserva temporal** (`POST /reservations`)  
   El cliente "bloquea" tickets indicando `event_id`, `type` y `quantity`.  
   - Estado inicial: `PENDING`  
   - La reserva **expira** a los 2 minutos (`expires_at`) si no se confirma.
   - Durante la reserva, el stock del evento ya **se descuenta** (hold de
   inventario).

4) **Checkout** (`POST /checkout`)  
   Confirma la reserva (simula pago).  
   - Cambia la reserva a `CONFIRMED`  
   - Genera un **purchase** con los **tickets** emitidos (códigos únicos).

5) **Consulta de compras** (`GET /purchases/{id}`)  
   Permite ver los detalles de una compra: total, buyer, lista de tickets
emitidos.

## 🔁 Estados y vencimientos

- `Reservation.status`:
  - `PENDING`: recién creada, con `expires_at`.
  - `CONFIRMED`: luego de `POST /checkout`.
  - `EXPIRED`: si se consulta después de `expires_at` o se implementa un
  proceso de limpieza.
- **Vencimiento**: si una reserva vence **sin confirmar**, el estado pasa a
`EXPIRED`.  

  **Nota**: actualmente el stock **no se repone automáticamente** al expirar
(diseño intencional para simplificar el desafío frontend).

## 🧱 Esquemas (resumen)

- **Event**:
  - `name`, `category`, `date`, `location`, `image?`
  - `tickets[]`: `{ type, price, available }`

- **Reservation**:
  - `event_id`, `items[]`: `{ type, quantity }`
  - `total_price`, `status`, `created_at`, `expires_at`

- **Purchase**:
  - `reservation_id`, `event_id`, `buyer`, `total_price`, `confirmed_at`
  - `tickets[]`: `{ code, type }`

## 🧪 Flujo resumido (ejemplo)

```
Cliente → POST /events → (Crea evento)
Cliente → GET /events → (Lista eventos)
Cliente → POST /reservations → (Reserva PENDING; stock descontado)
Cliente → POST /checkout → (Confirma; genera Purchase y tickets)
Cliente → GET /purchases/{id} → (Consulta compra)
```

## ⚠️ Errores frecuentes

- `400 Invalid ObjectId` → IDs deben ser [ObjectId][oid] válidos.
- `400 Not enough 'TYPE' tickets` → stock insuficiente al reservar.
- `404 Event/Reservation/Purchase not found` → recurso inexistente.

## 🔗 Enlaces

- 🌐 **Producción:** [tickets.grye.org][api-url]
- 📘 **Docs:** [tickets.grye.org/docs][docs-url]
- 💻 **Repositorio:** [GitHub][github-repo]

## 📚 Referencias

- [**MongoDB ObjectId**][oid] — Identificador único para documentos en MongoDB.  
- [**REST API**][rest] — Definición y fundamentos del estilo arquitectónico REST.  
- [**HTTP Methods**][http] — Métodos estándar utilizados en APIs REST (`GET`, `POST`, `PATCH`, `DELETE`).  
- [**JSON Format**][json] — Formato de intercambio de datos entre cliente y servidor.  
- [**ISO 8601**][iso8601] — Estándar internacional para fechas y horas.  
- [**HTTP Status Codes**][status] — Códigos de estado que indican el resultado de una solicitud HTTP.

[api-url]: https://tickets.grye.org/
[docs-url]: https://tickets.grye.org/docs
[github-repo]: https://github.com/Awerito/ulatickets-api.git
[oid]: https://www.mongodb.com/docs/manual/reference/bson-types/#objectid  
[rest]: https://developer.mozilla.org/en-US/docs/Glossary/REST  
[http]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods  
[json]: https://www.json.org/json-en.html  
[iso8601]: https://en.wikipedia.org/wiki/ISO_8601  
[status]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
