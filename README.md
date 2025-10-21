# 🎟️ Ticketing API – FastAPI Event & Purchase System

[![Version][ver-badge]][api-url]
[![Status][status-badge]][api-url]

FastAPI backend for managing **events**, **reservations**, and **purchases** in
a simple ticket-selling platform. Includes MongoDB integration and async logic
with Motor and httpx.

(repo)

---

## 🚀 Requirements

- Python 3.12+
- MongoDB
- Docker (optional)
- `fastapi` CLI for dev mode (`pip install fastapi[standard]`)

---

## 🛠️ Setup (Local)

### 1. Clone the repository

```bash
git clone https://github.com/Awerito/ulatickets.git
cd ulatickets
````

### 2. Create and activate virtualenv

```bash
python -m venv env
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root folder:

```env
ENV=dev

MONGO_URI=mongodb://localhost:27017
MONGO_DB=ticketing
```

---

## 🧪 Run the API (Local)

```bash
fastapi dev --host 127.0.0.1 --port 8000
```

> The server runs at [http://127.0.0.1:8000](http://127.0.0.1:8000)
> Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧩 Example Scripts

### Populate with demo data

```bash
python -m scripts.bootstrap_data
```

Creates sample events, reservations, and a checkout to verify the flow.

### Simulate random purchases

```bash
python -m scripts.simulate_purchases
```

Fetches events from the API and performs a couple of test reservations and
checkouts.

---

## 🐳 Run with Docker

### Build image

```bash
docker build -t ticketing-api .
```

### Run container (using `.env`)

```bash
docker run --env-file .env --network host -p 8000:8000 ticketing-api
```

---

## 📚 API Endpoints

### Events

* `GET /events` → list available events
* `POST /events` → create new event
* `PATCH /events/{id}` → update event
* `DELETE /events/{id}` → remove event

### Reservations

* `POST /reservations` → create reservation
* `GET /reservations/{id}` → view reservation
* `DELETE /reservations/{id}` → cancel reservation

### Purchases

* `POST /checkout` → confirm reservation and create purchase
* `GET /purchases/{id}` → retrieve purchase details

---

## 🧰 Tech Stack

* **FastAPI** – web framework
* **Motor (Async MongoDB)** – persistence layer
* **httpx** – async HTTP client (used in demo scripts)
* **Pydantic v2** – models and validation

---

## 📌 Notes

* Subdocuments (`tickets`, `items`) do not carry `_id`; only top-level
documents have it.
* The included `scripts/bootstrap_data.py` and `scripts/simulate_purchases.py`
demonstrate how to consume the API programmatically.
* Ideal as a classroom or interview-level project for practicing React/Frontend
consumption of async APIs.

---

## 📎 Enlaces

- 🌐 **Producción:** [tickets.grye.org][api-url]
- 📘 **Docs:** [tickets.grye.org/docs][docs-url]
- 💻 **Repositorio:** [GitHub][github-repo]

[api-url]: https://tickets.grye.org/
[docs-url]: https://tickets.grye.org/docs
[github-repo]: https://github.com/Awerito/ulatickets-api.git

[ver-badge]: https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ftickets.grye.org%2F&query=%24.version&label=version&cacheSeconds=300&style=flat-square
[status-badge]: https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Ftickets.grye.org%2F&query=%24.status&label=tickets.grye.org&color=brightgreen&cacheSeconds=300&style=flat-square
