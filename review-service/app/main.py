import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.review_router import router as review_router

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app = FastAPI(
    title="Review Service",
    description="Mikroserwis obsługi opinii i ocen warsztatów",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review_router)


@app.get("/")
def root():
    return {"message": "Review Service działa poprawnie"}