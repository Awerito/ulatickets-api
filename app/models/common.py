from typing import Annotated, Optional, Any, TypeVar, Type
from fastapi import HTTPException
from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]


class MongoBase(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class PatchResponse(BaseModel):
    updated: bool


def to_oid(value: str) -> ObjectId:
    """Convert string to ObjectId or raise HTTP 400."""
    try:
        return ObjectId(value)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")


T = TypeVar("T", bound=BaseModel)


def parse_mongo(doc: dict[str, Any] | None, model: Type[T]) -> T:
    """
    Convert a MongoDB document (dict) into a Pydantic model instance.

    Raises:
        HTTPException(404): if the document is None.
    """
    if not doc:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return model(**doc)
