from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import MongoDBConnectionManager
from app.config import FastAPIConfig, CorsConfig, ENV


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Lifespan context for application startup and shutdown.
    """
    # Check database connection on startup
    async with MongoDBConnectionManager() as db:
        pass
    yield


# Initialize FastAPI application
app = FastAPI(**FastAPIConfig.dict(), lifespan=lifespan)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CorsConfig.origins,
    allow_credentials=CorsConfig.allow_credentials,
    allow_methods=CorsConfig.allow_methods,
    allow_headers=CorsConfig.allow_headers,
    max_age=CorsConfig.max_age,
)


# Healthcheck Endpoint
@app.get("/", tags=["Healthcheck"])
def healthcheck():
    """
    Healthcheck endpoint.

    Returns:
        dict: Basic API status including:
            - status: Always "ok" if the API is reachable.
            - name: API name.
            - version: Current API version.
            - env: Current environment (dev, qa, prod).
    """
    return {"status": "ok", "name": app.title, "version": app.version, "env": ENV}


# Routers
