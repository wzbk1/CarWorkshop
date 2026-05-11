from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Location, CarBrand, location_car_brands
from app.schemas import LocationCreate, LocationUpdate, LocationResponse
from app.security import require_admin, get_current_user_payload

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    location_data: LocationCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    new_location = Location(
        name=location_data.name,
        address=location_data.address,
        city=location_data.city,
        description=location_data.description,
        is_active=location_data.is_active
    )
    if location_data.serviced_brand_ids:
        brands = db.query(CarBrand).filter(CarBrand.id.in_(location_data.serviced_brand_ids)).all()
        new_location.serviced_brands = brands

    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location

@router.get("/", response_model=list[LocationResponse])
def get_locations(
    active_only: bool = Query(default=True),
    city: str | None = Query(default=None),
    brand_id: int | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(Location)
    if active_only:
        query = query.filter(Location.is_active == True)
    if city:
        query = query.filter(Location.city.ilike(f"%{city}%"))
    if brand_id:
        query = query.join(location_car_brands).filter(location_car_brands.c.car_brand_id == brand_id)
    return query.order_by(Location.name.asc()).all()

@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warsztat nie został znaleziony")
    return location

@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    location_data: LocationUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warsztat nie został znaleziony")
    for field, value in location_data.dict(exclude_unset=True).items():
        if field == "serviced_brand_ids":
            brands = db.query(CarBrand).filter(CarBrand.id.in_(value)).all()
            location.serviced_brands = brands
        else:
            setattr(location, field, value)
    db.commit()
    db.refresh(location)
    return location

@router.delete("/{location_id}", status_code=status.HTTP_200_OK)
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warsztat nie został znaleziony")
    db.delete(location)
    db.commit()
    return {"message": f"Warsztat o ID {location_id} został usunięty"}