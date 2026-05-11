from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Review
from app.schemas import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewStatsResponse
from app.security import get_current_user_payload

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    user_email = payload.get("sub")
    user_name = f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip() or user_email


    
    existing = db.query(Review).filter(
        Review.user_email == user_email,
        Review.location_id == review_data.location_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Już wystawiłeś opinię dla tego warsztatu. Możesz ją edytować."
        )

    new_review = Review(
        user_email=user_email,
        user_name=user_name,
        location_id=review_data.location_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


@router.get("/location/{location_id}", response_model=list[ReviewResponse])
def get_reviews_for_location(location_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.location_id == location_id).order_by(Review.created_at.desc()).all()


@router.get("/location/{location_id}/stats", response_model=ReviewStatsResponse)
def get_review_stats(location_id: int, db: Session = Depends(get_db)):
    result = db.query(
        func.avg(Review.rating).label("average_rating"),
        func.count(Review.id).label("total_reviews")
    ).filter(Review.location_id == location_id).first()

    avg_rating = round(float(result.average_rating), 2) if result.average_rating else 0.0
    total = result.total_reviews if result.total_reviews else 0

    return ReviewStatsResponse(
        location_id=location_id,
        average_rating=avg_rating,
        total_reviews=total
    )


@router.get("/me", response_model=list[ReviewResponse])
def get_my_reviews(db: Session = Depends(get_db), payload: dict = Depends(get_current_user_payload)):
    user_email = payload.get("sub")
    return db.query(Review).filter(Review.user_email == user_email).order_by(Review.created_at.desc()).all()


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opinia nie została znaleziona")
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opinia nie została znaleziona")
    if review.user_email != payload.get("sub") and payload.get("role") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu")
    for field, value in review_data.dict(exclude_unset=True).items():
        setattr(review, field, value)
    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_200_OK)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opinia nie została znaleziona")
    if review.user_email != payload.get("sub") and payload.get("role") != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu")
    db.delete(review)
    db.commit()
    return {"message": "Opinia została usunięta"}