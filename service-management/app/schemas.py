from pydantic import BaseModel, Field



class LocationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    address: str = Field(..., min_length=2, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool = True
    serviced_brand_ids: list[int] = Field(default_factory=list)


class LocationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    address: str | None = Field(default=None, min_length=2, max_length=255)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None
    serviced_brand_ids: list[int] | None = None


class LocationResponse(BaseModel):
    id: int
    name: str
    address: str
    city: str
    description: str | None
    is_active: bool

    class Config:
        from_attributes = True



class CarBrandCreate(BaseModel):   
    name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class CarBrandResponse(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True



class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(..., gt=0)
    duration_minutes: int = Field(..., gt=0, le=480)
    is_active: bool = True


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, gt=0)
    duration_minutes: int | None = Field(default=None, gt=0, le=480)
    is_active: bool | None = None


class ServiceResponse(BaseModel):
    id: int
    location_id: int
    name: str
    description: str | None
    price: float
    duration_minutes: int
    is_active: bool

    class Config:
        from_attributes = True


class ServiceWithLocationResponse(BaseModel):
    id: int
    location_id: int
    location_name: str
    location_address: str
    location_city: str
    name: str
    description: str | None
    price: float
    duration_minutes: int
    is_active: bool



class EmployeeCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    specialization: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=2, max_length=100)
    last_name: str | None = Field(default=None, min_length=2, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    specialization: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class EmployeeResponse(BaseModel):
    id: int
    location_id: int
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    specialization: str | None
    is_active: bool

    class Config:
        from_attributes = True


class EmployeeWithLocationResponse(BaseModel):
    id: int
    location_id: int
    location_name: str
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    specialization: str | None
    is_active: bool


class AssignServiceToEmployeeRequest(BaseModel):
    service_id: int = Field(..., gt=0)


class AssignBrandToLocationRequest(BaseModel):
    brand_id: int = Field(..., gt=0)



class BusinessHoursCreate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    open_time: str | None = Field(default=None, min_length=5, max_length=5, description="Format HH:MM")
    close_time: str | None = Field(default=None, min_length=5, max_length=5, description="Format HH:MM")
    lunch_start: str | None = Field(default=None, min_length=5, max_length=5, description="Przerwa obiadowa start HH:MM")
    lunch_end: str | None = Field(default=None, min_length=5, max_length=5, description="Przerwa obiadowa koniec HH:MM")
    is_closed: bool = False


class BusinessHoursUpdate(BaseModel):
    open_time: str | None = Field(default=None, min_length=5, max_length=5)
    close_time: str | None = Field(default=None, min_length=5, max_length=5)
    lunch_start: str | None = Field(default=None, min_length=5, max_length=5)
    lunch_end: str | None = Field(default=None, min_length=5, max_length=5)
    is_closed: bool | None = None


class BusinessHoursResponse(BaseModel):
    id: int
    location_id: int
    day_of_week: int
    open_time: str | None
    close_time: str | None
    lunch_start: str | None
    lunch_end: str | None
    is_closed: bool

    class Config:
        from_attributes = True



class LocationExceptionCreate(BaseModel):
    exception_date: str = Field(..., min_length=10, max_length=10, description="YYYY-MM-DD")
    open_time: str | None = Field(default=None, min_length=5, max_length=5)
    close_time: str | None = Field(default=None, min_length=5, max_length=5)
    is_closed: bool = True
    reason: str | None = Field(default=None, max_length=255)


class LocationExceptionUpdate(BaseModel):
    open_time: str | None = Field(default=None, min_length=5, max_length=5)
    close_time: str | None = Field(default=None, min_length=5, max_length=5)
    is_closed: bool | None = None
    reason: str | None = Field(default=None, max_length=255)


class LocationExceptionResponse(BaseModel):
    id: int
    location_id: int
    exception_date: str
    open_time: str | None
    close_time: str | None
    is_closed: bool
    reason: str | None

    class Config:
        from_attributes = True



class EmployeeAbsenceCreate(BaseModel):
    absence_date: str = Field(..., min_length=10, max_length=10, description="YYYY-MM-DD")
    reason: str | None = Field(default=None, max_length=255)


class EmployeeAbsenceUpdate(BaseModel):
    reason: str | None = Field(default=None, max_length=255)


class EmployeeAbsenceResponse(BaseModel):
    id: int
    employee_id: int
    absence_date: str
    reason: str | None

    class Config:
        from_attributes = True



class CarCreate(BaseModel):
    brand_id: int = Field(..., gt=0)
    model: str = Field(..., min_length=1, max_length=100)
    vin: str | None = Field(default=None, min_length=17, max_length=17)
    color: str | None = Field(default=None, max_length=50)
    mileage: int | None = Field(default=None, ge=0)
    year: int | None = Field(default=None, ge=1900, le=2030)


class CarUpdate(BaseModel):
    model: str | None = Field(default=None, min_length=1, max_length=100)
    vin: str | None = Field(default=None, min_length=17, max_length=17)
    color: str | None = Field(default=None, max_length=50)
    mileage: int | None = Field(default=None, ge=0)
    year: int | None = Field(default=None, ge=1900, le=2030)


class CarResponse(BaseModel):
    id: int
    user_email: str
    brand_id: int
    brand_name: str | None = None
    model: str
    vin: str | None
    color: str | None
    mileage: int | None
    year: int | None

    class Config:
        from_attributes = True