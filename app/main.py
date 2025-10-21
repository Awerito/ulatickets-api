from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import MongoDBConnectionManager
from app.config import FastAPIConfig, CorsConfig, ENV

from app.routers.tickets.endpoints import router as tickets_router


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
    return {"status": "ok", "name": app.title, "version": app.version, "env": ENV}


# Routers
app.include_router(tickets_router)
