import os
from typing import Any
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8000")
SERVICE_MANAGEMENT_URL = os.getenv("SERVICE_MANAGEMENT_URL", "http://127.0.0.1:8001")
BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://127.0.0.1:8002")
REVIEW_SERVICE_URL = os.getenv("REVIEW_SERVICE_URL", "http://127.0.0.1:8003")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost")

app = FastAPI(
    title="CarWorkshop API Gateway",
    description="Centralny punkt wejścia do mikroserwisów CarWorkshop",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_target_service(path: str) -> tuple[str, str]:
    if path.startswith("/auth"):
        return USER_SERVICE_URL, path
    if any(path.startswith(p) for p in ["/locations", "/services", "/employees",
                                          "/employee-absences", "/business-hours",
                                          "/location-exceptions", "/car-brands", "/cars"]):
        return SERVICE_MANAGEMENT_URL, path
    if path.startswith("/bookings"):
        return BOOKING_SERVICE_URL, path
    if path.startswith("/reviews"):
        return REVIEW_SERVICE_URL, path
    raise ValueError(f"Brak routingu dla ścieżki: {path}")


def filter_headers(headers: dict[str, Any]) -> dict[str, str]:
    excluded = {"host", "content-length", "connection", "accept-encoding"}
    return {k: v for k, v in headers.items() if k.lower() not in excluded}


@app.get("/")
def root():
    return {
        "message": "CarWorkshop API Gateway działa poprawnie",
        "routes": {
            "/auth/*": "user-service",
            "/locations/*": "service-management",
            "/services/*": "service-management",
            "/employees/*": "service-management",
            "/employee-absences/*": "service-management",
            "/business-hours/*": "service-management",
            "/location-exceptions/*": "service-management",
            "/car-brands/*": "service-management",
            "/cars/*": "service-management",
            "/bookings/*": "booking-service",
            "/reviews/*": "review-service",
        }
    }


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_request(full_path: str, request: Request):
    path = "/" + full_path
    try:
        target_base_url, target_path = get_target_service(path)
    except ValueError as e:
        return Response(content=str(e), status_code=404, media_type="text/plain")

    target_url = f"{target_base_url}{target_path}"
    if request.url.query:
        target_url = f"{target_url}?{request.url.query}"

    body = await request.body()
    headers = filter_headers(dict(request.headers))

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:   
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
        except httpx.RequestError as e:
            return Response(
                content=f"Błąd komunikacji z mikroserwisem: {str(e)}",
                status_code=503,
                media_type="text/plain"
            )