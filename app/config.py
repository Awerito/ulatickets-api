import os

from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "dev")


class FastAPIConfig:
    @classmethod
    def dict(cls):
        return {
            "title": os.getenv("API_TITLE", "FastAPI"),
            "description": os.getenv("API_DESCRIPTION", "FastAPI application"),
            "version": os.getenv("API_VERSION", "1.0.0"),
            "contact": {
                "name": os.getenv("API_CONTACT_NAME", "API Support"),
                "email": os.getenv("API_CONTACT_EMAIL", "example@email.com"),
            },
            "docs_url": os.getenv("API_DOCS_URL", "/docs"),
            "redoc_url": os.getenv("API_REDOC_URL", "/redoc"),
        }


class CorsConfig:
    origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    allow_methods = [m.strip() for m in os.getenv("CORS_ALLOW_METHODS", "*").split(",")]
    allow_headers = [h.strip() for h in os.getenv("CORS_ALLOW_HEADERS", "*").split(",")]
    max_age = int(os.getenv("CORS_MAX_AGE", "600"))


class DatabaseConfig:
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    name = os.getenv("DATABASE_NAME", "mongodb")
