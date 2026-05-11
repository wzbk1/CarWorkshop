from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Employee, EmployeeAbsence
from app.schemas import EmployeeAbsenceCreate, EmployeeAbsenceUpdate, EmployeeAbsenceResponse
from app.security import require_admin

router = APIRouter(prefix="/employee-absences", tags=["Employee Absences"])


@router.post("/employees/{employee_id}/absences", response_model=EmployeeAbsenceResponse, status_code=status.HTTP_201_CREATED)
def create_absence(
    employee_id: int,
    absence_data: EmployeeAbsenceCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mechanik nie został znaleziony")
    new_absence = EmployeeAbsence(employee_id=employee_id, **absence_data.dict())
    db.add(new_absence)
    db.commit()
    db.refresh(new_absence)
    return new_absence


@router.get("/employees/{employee_id}/absences", response_model=list[EmployeeAbsenceResponse])
def get_absences(employee_id: int, db: Session = Depends(get_db)):
    return db.query(EmployeeAbsence).filter(EmployeeAbsence.employee_id == employee_id).order_by(EmployeeAbsence.absence_date).all()


@router.get("/employees/{employee_id}/absences/{absence_date}", response_model=EmployeeAbsenceResponse)
def get_absence_for_date(employee_id: int, absence_date: str, db: Session = Depends(get_db)):
    absence = db.query(EmployeeAbsence).filter(
        EmployeeAbsence.employee_id == employee_id,
        EmployeeAbsence.absence_date == absence_date
    ).first()
    if not absence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nieobecność nie została znaleziona")
    return absence


@router.get("/", response_model=list[EmployeeAbsenceResponse])
def get_all_absences(db: Session = Depends(get_db)):
    return db.query(EmployeeAbsence).order_by(EmployeeAbsence.absence_date).all()


@router.put("/{absence_id}", response_model=EmployeeAbsenceResponse)
def update_absence(absence_id: int, absence_data: EmployeeAbsenceUpdate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    absence = db.query(EmployeeAbsence).filter(EmployeeAbsence.id == absence_id).first()
    if not absence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nieobecność nie została znaleziona")
    for field, value in absence_data.dict(exclude_unset=True).items():
        setattr(absence, field, value)
    db.commit()
    db.refresh(absence)
    return absence


@router.delete("/{absence_id}", status_code=status.HTTP_200_OK)
def delete_absence(absence_id: int, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    absence = db.query(EmployeeAbsence).filter(EmployeeAbsence.id == absence_id).first()
    if not absence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nieobecność nie została znaleziona")
    db.delete(absence)
    db.commit()
    return {"message": "Nieobecność została usunięta"}