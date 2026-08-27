from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.settings import settings

tags_metadata = [
    {
        "name": "appointments",
        "description": "List available appointment slots and book a doctor "
        "for a selected time. Slots are aggregated by start time; the "
        "backend selects the doctor automatically.",
    },
]

app = FastAPI(
    title="Medical Appointment Booking API",
    description=(
        "Backend API for booking medical appointments.\n\n"
        "Doctor availability is seeded in PostgreSQL. Slots shown to the "
        "user are **aggregated by start time** — if multiple doctors are "
        "available at `10:00`, a single `10:00` slot is returned with the "
        "doctor count.\n\n"
        "When booking, the backend selects an available doctor using "
        "`SELECT ... FOR UPDATE SKIP LOCKED` to prevent double-booking under "
        "concurrent requests."
    ),
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "Backend Technical Exercise"},
    license_info={"name": "MIT"},
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["root"])
async def read_root() -> dict[str, str]:
    return {"message": "Backend is running. See /docs or /redoc for API documentation."}
