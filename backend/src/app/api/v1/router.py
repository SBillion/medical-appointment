from fastapi import APIRouter

from app.api.v1.endpoints import appointments, health

api_router = APIRouter(prefix="/api", tags=["appointments"])
api_router.include_router(health.router)
api_router.include_router(appointments.router)
