from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), nullable=False, index=True)
    location_id = Column(Integer, nullable=False, index=True)
    location_name = Column(String(150), nullable=False)
    service_id = Column(Integer, nullable=False, index=True)
    service_name = Column(String(150), nullable=False)
    service_duration_minutes = Column(Integer, nullable=False)
    employee_id = Column(Integer, nullable=False, index=True)
    employee_name = Column(String(220), nullable=False)
    car_id = Column(Integer, nullable=True)
    appointment_date = Column(String(10), nullable=False)  
    appointment_time = Column(String(5), nullable=False)   
    status = Column(String(20), nullable=False, default="BOOKED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())