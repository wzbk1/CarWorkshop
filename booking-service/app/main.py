import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.booking_router import router as booking_router

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app = FastAPI(
    title="Booking Service",
    description="Mikroserwis obsługi rezerwacji wizyt w warsztatach",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(booking_router)


@app.get("/")
def root():
    return {"message": "Booking Service działa poprawnie"}