from fastapi import APIRouter, HTTPException


router = APIRouter(tags=["Sample Endpoint"])


@router.get("/")
async def read_root(sumulate_error: bool = False):
    if sumulate_error:
        raise HTTPException(status_code=400, detail="Simulated error occurred")

    return {"message": "Hello, World!"}
