from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Booking
from app.schemas import BookingCreate, BookingResponse
from app.security import get_current_user_payload, require_admin
from app.validators import (
    validate_booking_datetime_basic,
    generate_daily_slots,
    filter_future_slots,
    can_service_fit_in_schedule,
    ranges_overlap,
    get_day_of_week,
)
from app.service_client import (
    get_service_by_id,
    get_employees_for_service,
    get_business_hours_for_location_and_day,
    get_location_exception_for_date,
    get_employee_absence_for_date,
    get_employee_full_name,
    get_location_by_id,
    validate_service_payload,
    validate_employee_payload,
    validate_business_hours_payload,
    validate_location_exception_payload,
    validate_employee_absence_payload,
)


router = APIRouter(prefix="/bookings", tags=["Bookings"])


def is_employee_available(
    db: Session,
    employee_id: int,
    appointment_date: str,
    candidate_time: str,
    duration_minutes: int
) -> bool:
    existing = db.query(Booking).filter(
        Booking.employee_id == employee_id,
        Booking.appointment_date == appointment_date,
        Booking.status == "BOOKED"
    ).all()
    for booking in existing:
        if ranges_overlap(candidate_time, duration_minutes, booking.appointment_time, booking.service_duration_minutes):
            return False
    return True


def is_employee_absent(employee_id: int, appointment_date: str) -> bool:
    try:
        absence = get_employee_absence_for_date(employee_id=employee_id, absence_date=appointment_date)
    except ConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    if not absence:
        return False
    try:
        validate_employee_absence_payload(absence)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return True



def load_service_or_error(service_id: int) -> dict:
    try:
        service = get_service_by_id(service_id)
    except ConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usługa nie istnieje")
    try:
        validate_service_payload(service)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    if not service.get("is_active", False):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usługa jest nieaktywna")
    return service


def load_employees_for_service_or_error(service_id: int) -> list[dict]:
    try:
        employees = get_employees_for_service(service_id)
    except ConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    if not employees:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Do tej usługi nie przypisano żadnego aktywnego mechanika")
    for emp in employees:
        try:
            validate_employee_payload(emp)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return employees


def load_business_hours_or_error(location_id: int, appointment_date: str) -> dict:
    try:
        location_exception = get_location_exception_for_date(location_id, appointment_date)
    except ConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    if location_exception:
        try:
            validate_location_exception_payload(location_exception)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        if location_exception.get("is_closed"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Warsztat zamknięty w dniu {appointment_date}: {location_exception.get('reason', 'Brak powodu')}"
            )
        return {
            "open_time": location_exception.get("open_time", "08:00"),
            "close_time": location_exception.get("close_time", "18:00"),
            "lunch_start": None,
            "lunch_end": None,
            "is_closed": False,
        }
    day_of_week = get_day_of_week(appointment_date)
    try:
        business_hours = get_business_hours_for_location_and_day(location_id, day_of_week)
    except ConnectionError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    if not business_hours:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brak godzin pracy dla wybranego dnia")
    try:
        validate_business_hours_payload(business_hours)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    if business_hours.get("is_closed"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Warsztat jest zamknięty w wybranym dniu")
    return business_hours


@router.get("/available-slots/{service_id}")
def get_available_slots(
    service_id: int,
    appointment_date: str = Query(..., description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    service = load_service_or_error(service_id)
    location_id = service["location_id"]
    duration_minutes = service["duration_minutes"]

    hours = load_business_hours_or_error(location_id, appointment_date)
    open_time = hours["open_time"]
    close_time = hours["close_time"]
    lunch_start = hours.get("lunch_start")
    lunch_end = hours.get("lunch_end")

    all_slots = generate_daily_slots(open_time, close_time, lunch_start, lunch_end)
    future_slots = filter_future_slots(appointment_date, all_slots)

    employees = load_employees_for_service_or_error(service_id)

    
    available_slots = []
    for slot in future_slots:
        if not can_service_fit_in_schedule(slot, duration_minutes, close_time, lunch_start, lunch_end):
            continue
        available_employees = []
        for emp in employees:
            if is_employee_absent(emp["id"], appointment_date):
                continue
            if not is_employee_available(db, emp["id"], appointment_date, slot, duration_minutes):
                continue
            available_employees.append({
                "employee_id": emp["id"],
                "employee_name": f"{emp['first_name']} {emp['last_name']}"
            })
        if available_employees:
            available_slots.append({
                "time": slot,
                "available_employees": available_employees
            })

    return {
        "service_id": service_id,
        "service_name": service["name"],
        "duration_minutes": duration_minutes,
        "appointment_date": appointment_date,
        "open_time": open_time,
        "close_time": close_time,
        "lunch_start": lunch_start,
        "lunch_end": lunch_end,
        "available_slots": available_slots,
    }


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    user_email = payload.get("sub")

    validate_booking_datetime_basic(booking_data.appointment_date, booking_data.appointment_time)

    service = load_service_or_error(booking_data.service_id)
    hours = load_business_hours_or_error(service["location_id"], booking_data.appointment_date)

    duration_minutes = service["duration_minutes"]

    
    if not can_service_fit_in_schedule(
        booking_data.appointment_time,
        duration_minutes,
        hours["close_time"],
        hours.get("lunch_start"),
        hours.get("lunch_end")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usługa nie mieści się w godzinach pracy lub koliduje z przerwą obiadową"
        )

    
    employees = load_employees_for_service_or_error(booking_data.service_id)

    if booking_data.employee_id:
        chosen_employee = next((e for e in employees if e["id"] == booking_data.employee_id), None)
        if not chosen_employee:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wybrany mechanik nie obsługuje tej usługi")
    else:
        chosen_employee = employees[0]

    employee_id = chosen_employee["id"]
    employee_name = f"{chosen_employee['first_name']} {chosen_employee['last_name']}"

    
    if is_employee_absent(employee_id, booking_data.appointment_date):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mechanik jest nieobecny w wybranym dniu")

    
    if not is_employee_available(db, employee_id, booking_data.appointment_date, booking_data.appointment_time, duration_minutes):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Wybrany termin jest już zajęty")

    
    location = get_location_by_id(service["location_id"])
    location_name = location["name"] if location else ""

    new_booking = Booking(
        user_email=user_email,
        location_id=service["location_id"],
        location_name=location_name,
        service_id=service["id"],
        service_name=service["name"],
        service_duration_minutes=duration_minutes,
        employee_id=employee_id,
        employee_name=employee_name,
        car_id=booking_data.car_id,
        appointment_date=booking_data.appointment_date,
        appointment_time=booking_data.appointment_time,
        status="BOOKED"
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking


@router.get("/me", response_model=list[BookingResponse])
def get_my_bookings(db: Session = Depends(get_db), payload: dict = Depends(get_current_user_payload)):
    user_email = payload.get("sub")
    return db.query(Booking).filter(Booking.user_email == user_email).order_by(Booking.appointment_date.desc(), Booking.appointment_time.desc()).all()


@router.get("/history", response_model=list[BookingResponse])
def get_booking_history(db: Session = Depends(get_db), payload: dict = Depends(get_current_user_payload)):
    user_email = payload.get("sub")
    return db.query(Booking).filter(Booking.user_email == user_email).order_by(Booking.appointment_date.desc()).all()


@router.get("/all", response_model=list[BookingResponse])
def get_all_bookings(db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    return db.query(Booking).order_by(Booking.appointment_date.desc(), Booking.appointment_time.desc()).all()


@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db), payload: dict = Depends(get_current_user_payload)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezerwacja nie została znaleziona")
    if booking.user_email != payload.get("sub") and payload.get("role") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu")
    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)
    return booking


@router.patch("/{booking_id}/complete", response_model=BookingResponse)
def complete_booking(booking_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rezerwacja nie została znaleziona")
    if booking.status != "BOOKED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tylko aktywne rezerwacje mogą być zakończone")
    booking.status = "COMPLETED"
    db.commit()
    db.refresh(booking)
    return booking