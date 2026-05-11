from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CarBrand, Location
from app.schemas import CarBrandCreate, CarBrandResponse  
from app.security import require_admin, get_current_user_payload

router = APIRouter(prefix="/car-brands", tags=["Car Brands"])


@router.get("/", response_model=list[CarBrandResponse])
def get_all_brands(active_only: bool = True, db: Session = Depends(get_db)):
    query = db.query(CarBrand)
    if active_only:
        query = query.filter(CarBrand.is_active == True)
    return query.order_by(CarBrand.name.asc()).all()


@router.get("/{brand_id}", response_model=CarBrandResponse)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(CarBrand).filter(CarBrand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marka nie została znaleziona")
    return brand


@router.post("/", response_model=CarBrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand_data: CarBrandCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    existing = db.query(CarBrand).filter(CarBrand.name == brand_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Marka o tej nazwie już istnieje"
        )
    new_brand = CarBrand(**brand_data.dict())
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    return new_brand


@router.post("/locations/{location_id}/brands", status_code=status.HTTP_200_OK)
def assign_brand_to_location(
    location_id: int,
    brand_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warsztat nie został znaleziony")
    brand = db.query(CarBrand).filter(CarBrand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marka nie została znaleziona")
    if brand not in location.serviced_brands:
        location.serviced_brands.append(brand)
        db.commit()
    return {"message": "Marka przypisana do warsztatu"}


@router.get("/locations/{location_id}/brands", response_model=list[CarBrandResponse])
def get_brands_for_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warsztat nie został znaleziony")
    return location.serviced_brands

@router.delete("/{brand_id}", status_code=status.HTTP_200_OK)
def delete_car_brand(brand_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    brand = db.query(CarBrand).filter(CarBrand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marka nie zostala znaleziona")
    db.delete(brand)
    db.commit()
    return {"message": "Marka usunieta"}
