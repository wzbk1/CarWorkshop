from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Location, LocationException
from app.schemas import LocationExceptionCreate, LocationExceptionUpdate, LocationExceptionResponse
from app.security import require_admin

router = APIRouter(prefix="/location-exceptions", tags=["Location Exceptions"])


@router.post("/locations/{location_id}/exceptions", response_model=LocationExceptionResponse, status_code=status.HTTP_201_CREATED)
def create_exception(
    location_id: int,
    exception_data: LocationExceptionCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warsztat nie został znaleziony")
    new_exception = LocationException(location_id=location_id, **exception_data.dict())
    db.add(new_exception)
    db.commit()
    db.refresh(new_exception)
    return new_exception


@router.get("/locations/{location_id}/exceptions", response_model=list[LocationExceptionResponse])
def get_exceptions(location_id: int, db: Session = Depends(get_db)):
    return db.query(LocationException).filter(LocationException.location_id == location_id).order_by(LocationException.exception_date).all()


@router.get("/locations/{location_id}/exceptions/{exception_date}", response_model=LocationExceptionResponse)
def get_exception_for_date(location_id: int, exception_date: str, db: Session = Depends(get_db)):
    exception = db.query(LocationException).filter(
        LocationException.location_id == location_id,
        LocationException.exception_date == exception_date
    ).first()
    if not exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wyjątek nie został znaleziony")
    return exception


@router.put("/{exception_id}", response_model=LocationExceptionResponse)
def update_exception(exception_id: int, exception_data: LocationExceptionUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    exception = db.query(LocationException).filter(LocationException.id == exception_id).first()
    if not exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wyjątek nie został znaleziony")
    for field, value in exception_data.dict(exclude_unset=True).items():
        setattr(exception, field, value)
    db.commit()
    db.refresh(exception)
    return exception


@router.delete("/{exception_id}", status_code=status.HTTP_200_OK)
def delete_exception(exception_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    exception = db.query(LocationException).filter(LocationException.id == exception_id).first()
    if not exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wyjątek nie został znaleziony")
    db.delete(exception)
    db.commit()
    return {"message": "Wyjątek został usunięty"}