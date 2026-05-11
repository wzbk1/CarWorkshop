from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Location, Service
from app.schemas import ServiceCreate, ServiceUpdate, ServiceResponse
from app.security import require_admin

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("/locations/{location_id}/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    location_id: int,
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warsztat nie został znaleziony")
    new_service = Service(location_id=location_id, **service_data.dict())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service


@router.get("/locations/{location_id}/services", response_model=list[ServiceResponse])
def get_services_by_location(location_id: int, active_only: bool = Query(default=True), db: Session = Depends(get_db)):
    query = db.query(Service).filter(Service.location_id == location_id)
    if active_only:
        query = query.filter(Service.is_active == True)
    return query.order_by(Service.name.asc()).all()


@router.get("/", response_model=list[ServiceResponse])
def get_all_services(active_only: bool = Query(default=True), db: Session = Depends(get_db)):
    query = db.query(Service)
    if active_only:
        query = query.filter(Service.is_active == True)
    return query.order_by(Service.name.asc()).all()


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usługa nie została znaleziona")
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, service_data: ServiceUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usługa nie została znaleziona")
    for field, value in service_data.dict(exclude_unset=True).items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_200_OK)
def delete_service(service_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usługa nie została znaleziona")
    db.delete(service)
    db.commit()
    return {"message": f"Usługa o ID {service_id} została usunięta"}