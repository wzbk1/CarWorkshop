from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


location_car_brands = Table(
    "location_car_brands",
    Base.metadata,
    Column("location_id", Integer, ForeignKey("locations.id"), primary_key=True),
    Column("car_brand_id", Integer, ForeignKey("car_brands.id"), primary_key=True)
)


employee_services = Table(
    "employee_services",
    Base.metadata,
    Column("employee_id", Integer, ForeignKey("employees.id"), primary_key=True),
    Column("service_id", Integer, ForeignKey("services.id"), primary_key=True)
)

class CarBrand(Base):
    __tablename__ = "car_brands"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    
    locations = relationship("Location", secondary=location_car_brands, back_populates="serviced_brands")
    cars = relationship("Car", back_populates="brand")

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    serviced_brands = relationship("CarBrand", secondary=location_car_brands, back_populates="locations")
    services = relationship("Service", back_populates="location", cascade="all, delete-orphan")
    employees = relationship("Employee", back_populates="location", cascade="all, delete-orphan")
    business_hours = relationship("BusinessHours", back_populates="location", cascade="all, delete-orphan")
    exceptions = relationship("LocationException", back_populates="location", cascade="all, delete-orphan")

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    is_active = Column(Boolean, default=True)

    location = relationship("Location", back_populates="services")
    employees = relationship("Employee", secondary=employee_services, back_populates="services")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    specialization = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)


    location = relationship("Location", back_populates="employees")
    services = relationship("Service", secondary=employee_services, back_populates="employees")
    absences = relationship("EmployeeAbsence", back_populates="employee", cascade="all, delete-orphan")

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), nullable=False, index=True)
    brand_id = Column(Integer, ForeignKey("car_brands.id"), nullable=False)
    model = Column(String(100), nullable=False)
    vin = Column(String(17), nullable=True, unique=True)
    color = Column(String(50), nullable=True)
    mileage = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    brand = relationship("CarBrand", back_populates="cars")

class BusinessHours(Base):
    __tablename__ = "business_hours"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False) 
    open_time = Column(String(8), nullable=True)
    close_time = Column(String(8), nullable=True)
    lunch_start = Column(String(8), nullable=True)
    lunch_end = Column(String(8), nullable=True)
    is_closed = Column(Boolean, default=False)

    location = relationship("Location", back_populates="business_hours")

class LocationException(Base):
    __tablename__ = "location_exceptions"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    exception_date = Column(String(10), nullable=False, index=True)
    open_time = Column(String(8), nullable=True)
    close_time = Column(String(8), nullable=True)
    is_closed = Column(Boolean, default=True)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    location = relationship("Location", back_populates="exceptions")

class EmployeeAbsence(Base):
    __tablename__ = "employee_absences"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    absence_date = Column(String(10), nullable=False, index=True)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="absences")