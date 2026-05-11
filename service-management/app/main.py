import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.location_router import router as location_router
from app.routers.service_router import router as service_router
from app.routers.employee_router import router as employee_router
from app.routers.business_hours_router import router as business_hours_router
from app.routers.location_exception_router import router as location_exception_router
from app.routers.employee_absence_router import router as employee_absence_router
from app.routers.car_brand_router import router as car_brand_router
from app.routers.car_router import router as car_router

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app = FastAPI(
    title="Service Management",
    description="Mikroserwis zarządzania warsztatami, usługami, mechanikami, markami i samochodami",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(location_router)
app.include_router(service_router)
app.include_router(employee_router)
app.include_router(business_hours_router)
app.include_router(location_exception_router)
app.include_router(employee_absence_router)
app.include_router(car_brand_router)
app.include_router(car_router)


@app.get("/")
def root():
    return {"message": "Service Management działa poprawnie"}