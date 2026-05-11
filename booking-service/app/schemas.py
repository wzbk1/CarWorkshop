from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    service_id: int = Field(..., gt=0)
    employee_id: int | None = Field(default=None, gt=0)
    car_id: int | None = Field(default=None, gt=0)
    appointment_date: str = Field(..., min_length=10, max_length=10, description="YYYY-MM-DD")
    appointment_time: str = Field(..., min_length=5, max_length=5, description="HH:MM")


class BookingResponse(BaseModel):
    id: int
    user_email: str
    location_id: int
    location_name: str
    service_id: int
    service_name: str
    service_duration_minutes: int
    employee_id: int
    employee_name: str
    car_id: int | None
    appointment_date: str
    appointment_time: str
    status: str

    class Config:
        from_attributes = True