from fastapi import APIRouter
from app.routers.tickets.events import router as events_router
from app.routers.tickets.reservations import router as reservations_router
from app.routers.tickets.purchases import router as purchases_router

router = APIRouter()
router.include_router(events_router)
router.include_router(reservations_router)
router.include_router(purchases_router)
