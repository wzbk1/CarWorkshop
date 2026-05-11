from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Location, BusinessHours
from app.schemas import BusinessHoursCreate, BusinessHoursUpdate, BusinessHoursResponse
from app.security import require_admin

router = APIRouter(prefix="/business-hours", tags=["Business Hours"])


@router.post("/locations/{location_id}/business-hours", response_model=BusinessHoursResponse, status_code=status.HTTP_201_CREATED)
def create_business_hours(
    location_id: int,
    hours_data: BusinessHoursCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warsztat nie został znaleziony")
    existing = db.query(BusinessHours).filter(
        BusinessHours.location_id == location_id,
        BusinessHours.day_of_week == hours_data.day_of_week
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Godziny dla tego dnia już istnieją")
    new_hours = BusinessHours(location_id=location_id, **hours_data.dict())
    db.add(new_hours)
    db.commit()
    db.refresh(new_hours)
    return new_hours


@router.get("/locations/{location_id}/business-hours", response_model=list[BusinessHoursResponse])
def get_business_hours(location_id: int, db: Session = Depends(get_db)):
    return db.query(BusinessHours).filter(BusinessHours.location_id == location_id).order_by(BusinessHours.day_of_week).all()


@router.get("/locations/{location_id}/business-hours/{day_of_week}", response_model=BusinessHoursResponse)
def get_business_hours_for_day(location_id: int, day_of_week: int, db: Session = Depends(get_db)):
    hours = db.query(BusinessHours).filter(
        BusinessHours.location_id == location_id,
        BusinessHours.day_of_week == day_of_week
    ).first()
    if not hours:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Godziny pracy nie zostały znalezione")
    return hours


@router.put("/{business_hours_id}", response_model=BusinessHoursResponse)
def update_business_hours(
    business_hours_id: int,
    hours_data: BusinessHoursUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    hours = db.query(BusinessHours).filter(BusinessHours.id == business_hours_id).first()
    if not hours:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Godziny pracy nie zostały znalezione")
    for field, value in hours_data.dict(exclude_unset=True).items():
        setattr(hours, field, value)
    db.commit()
    db.refresh(hours)
    return hours