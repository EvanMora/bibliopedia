"""Rutas relacionadas con las reseñas y calificaciones (/reviews)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import Review
from app.repositories import get_db
from app.services import ReviewService

router = APIRouter()


class ReviewCreate(BaseModel):
    """Payload para crear una reseña/calificación."""

    user_id: int
    book_id: int
    qualifications: int
    description: str | None = None


@router.post("/reviews", response_model=None)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)) -> Review:
    """Crea una reseña/calificación (el libro debe estar marcado como leído)."""
    return ReviewService(db).create_review(
        user_id=payload.user_id,
        book_id=payload.book_id,
        qualifications=payload.qualifications,
        description=payload.description,
    )
