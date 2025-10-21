# ---------- Base stage ----------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# ---------- Builder stage ----------
FROM base AS builder

WORKDIR /install

COPY requirements.txt .

RUN python -m venv /venv \
 && /venv/bin/pip install --upgrade pip \
 && /venv/bin/pip install -r requirements.txt

# ---------- Final stage ----------
FROM base

ENV PATH="/venv/bin:$PATH"
WORKDIR /app

COPY --from=builder /venv /venv
COPY . /app

EXPOSE 8000

CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000", "main:app"]
