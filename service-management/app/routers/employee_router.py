from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Location, Employee, Service
from app.schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse, AssignServiceToEmployeeRequest
from app.security import require_admin

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("/locations/{location_id}/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    location_id: int,
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warsztat nie został znaleziony")
    new_employee = Employee(location_id=location_id, **employee_data.dict())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


@router.get("/", response_model=list[EmployeeResponse])
def get_all_employees(active_only: bool = Query(default=True), db: Session = Depends(get_db)):
    query = db.query(Employee)
    if active_only:
        query = query.filter(Employee.is_active == True)
    return query.order_by(Employee.last_name.asc()).all()


@router.get("/locations/{location_id}/employees", response_model=list[EmployeeResponse])
def get_employees_by_location(location_id: int, active_only: bool = Query(default=True), db: Session = Depends(get_db)):
    query = db.query(Employee).filter(Employee.location_id == location_id)
    if active_only:
        query = query.filter(Employee.is_active == True)
    return query.order_by(Employee.last_name.asc()).all()


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mechanik nie został znaleziony")
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, employee_data: EmployeeUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mechanik nie został znaleziony")
    for field, value in employee_data.dict(exclude_unset=True).items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


@router.post("/{employee_id}/services", status_code=status.HTTP_200_OK)
def assign_service_to_employee(
    employee_id: int,
    request: AssignServiceToEmployeeRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mechanik nie został znaleziony")
    service = db.query(Service).filter(Service.id == request.service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usługa nie została znaleziona")
    if service not in employee.services:
        employee.services.append(service)
        db.commit()
    return {"message": "Usługa przypisana do mechanika"}


@router.delete("/{employee_id}/services/{service_id}", status_code=status.HTTP_200_OK)
def remove_service_from_employee(
    employee_id: int,
    service_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mechanik nie został znaleziony")
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usługa nie została znaleziona")
    if service in employee.services:
        employee.services.remove(service)
        db.commit()
    return {"message": "Usługa odpięta od mechanika"}


@router.get("/services/{service_id}/employees", response_model=list[EmployeeResponse])
def get_employees_for_service(service_id: int, active_only: bool = Query(default=True), db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usługa nie została znaleziona")
    employees = service.employees
    if active_only:
        employees = [e for e in employees if e.is_active]
    return employees