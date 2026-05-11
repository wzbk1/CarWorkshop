from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Car, CarBrand
from app.schemas import CarCreate, CarUpdate, CarResponse
from app.security import get_current_user_payload

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
def create_car(
    car_data: CarCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    user_email = payload.get("sub")
    brand = db.query(CarBrand).filter(CarBrand.id == car_data.brand_id, CarBrand.is_active == True).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marka nie została znaleziona lub jest nieaktywna")
    if car_data.vin:
        existing = db.query(Car).filter(Car.vin == car_data.vin).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Samochód z tym VIN już istnieje")
    new_car = Car(user_email=user_email, **car_data.dict())
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    result = CarResponse.from_orm(new_car)
    result.brand_name = brand.name
    return result


@router.get("/", response_model=list[CarResponse])
def get_all_cars(db: Session = Depends(get_db), payload: dict = Depends(get_current_user_payload)):
    if payload.get("role") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tylko admin może pobrać wszystkie auta")
    cars = db.query(Car).all()
    results = []
    for car in cars:
        car_resp = CarResponse.from_orm(car)
        car_resp.brand_name = car.brand.name if car.brand else None
        results.append(car_resp)
    return results


@router.get("/me", response_model=list[CarResponse])

def get_my_cars(db: Session = Depends(get_db), payload: dict = Depends(get_current_user_payload)):
    user_email = payload.get("sub")
    cars = db.query(Car).filter(Car.user_email == user_email).all()
    results = []
    for car in cars:
        car_resp = CarResponse.from_orm(car)
        car_resp.brand_name = car.brand.name if car.brand else None
        results.append(car_resp)
    return results


@router.get("/{car_id}", response_model=CarResponse)
def get_car(car_id: int, db: Session = Depends(get_db), payload: dict = Depends(get_current_user_payload)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Samochód nie został znaleziony")
    if car.user_email != payload.get("sub") and payload.get("role") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu")
    result = CarResponse.from_orm(car)
    result.brand_name = car.brand.name if car.brand else None
    return result


@router.put("/{car_id}", response_model=CarResponse)
def update_car(car_id: int, car_data: CarUpdate, db: Session = Depends(get_db), payload: dict = Depends(get_current_user_payload)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Samochód nie został znaleziony")
    if car.user_email != payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu")
    for field, value in car_data.dict(exclude_unset=True).items():
        setattr(car, field, value)
    db.commit()
    db.refresh(car)
    result = CarResponse.from_orm(car)
    result.brand_name = car.brand.name if car.brand else None
    return result


@router.delete("/{car_id}", status_code=status.HTTP_200_OK)
def delete_car(car_id: int, db: Session = Depends(get_db), payload: dict = Depends(get_current_user_payload)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Samochód nie został znaleziony")
    if car.user_email != payload.get("sub") and payload.get("role") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu")
    db.delete(car)
    db.commit()
    return {"message": "Samochód został usunięty"}