# 🏓 Inscription API - Table Tennis Tournament (Backend)

FastAPI backend for managing tournament participant registrations, category
assignments, and Flow payment integration.

---

## 🚀 Requirements

- Python 3.10+
- PostgreSQL instance running
- [Flow.cl](https://sandbox.flow.cl) sandbox account
- `ngrok` (optional, for testing webhooks)
- Docker (optional, for containerized setup)

---

## 🛠️ Setup (Local)

### 1. Clone the repo

```bash
git clone https://github.com/Awerito/austral-tt-inscriptions.git
cd inscriptions/backend
```

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

## ⚙️ Environment variables

Create a `.env` file:

```env
ENV=dev

POSTGRES_DATABASE_URL=postgresql://user:password@localhost:5432/dbname

FLOW_API_KEY_DEV=your_sandbox_api_key
FLOW_SECRET_DEV=your_sandbox_secret
FLOW_COMMERCE_ID_DEV=your_commerce_id

FLOW_RETURN_URL_DEV=http://localhost:3000/payment/return
FLOW_CALLBACK_URL_DEV=https://your-ngrok-url.ngrok-free.app/flow/confirmation
```

> Replace `your-ngrok-url` with the output from `ngrok http 8000`

---

## 🧪 Run the API (Local)

```bash
uvicorn app.main:app --reload
```

> FastAPI will run on http://localhost:8000

---

## 🐳 Run with Docker

### Build the image

```bash
docker build -t inscriptions-backend .
```

### Run the container with `.env`

```bash
docker run --env-file .env --network host -p 8000:8000 inscriptions-backend
```

> This assumes PostgreSQL is running on the host machine. Use Docker networking
> or `docker-compose` otherwise.

---

## 🌐 Expose your server (for Flow callbacks)

In another terminal:

```bash
ngrok http 8000
```

Update `.env` with your new `FLOW_CALLBACK_URL_DEV`.

---

## 📬 API Endpoints

### Registration

- `POST /registrations` → creates registration and returns Flow payment URL

### Flow webhook

- `POST /flow/confirmation` → Flow sends payment confirmation here

### Admin

- `GET /admin/registrations`
- `GET /admin/categories`
- `POST /admin/categories`
- `PUT /admin/categories/{id}`
- `DELETE /admin/categories/{id}`

---

## ✅ Flow test card (sandbox)

- Card: `4051885600446623`
- Expiry: any valid date (e.g. 12/29)
- CVV: `123`
- RUT: `11.111.111-1`
- Webpay key: `123`

---

## 📌 Notes

- Use the same email registered in Flow sandbox for testing payments.
- `getStatus` verification is skipped for now, webhook trust is based on token
match.
