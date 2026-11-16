"""Rutas para consultar y guardar las reseñas del usuario autenticado."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.models import User
from app.repositories import get_db
from app.services import ReviewService

router = APIRouter()


class ReviewCreate(BaseModel):
    """Payload para crear una reseña/calificación."""

    book_id: int
    qualifications: int = Field(ge=1, le=5)
    description: str | None = Field(default=None, max_length=2000)


@router.post("/reviews", response_model=None)
def create_review(
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, int | str | None]:
    """Crea o actualiza la reseña del usuario (el libro debe estar leído)."""
    review = ReviewService(db).create_review(
        user_id=current_user.id_user,
        book_id=payload.book_id,
        qualifications=payload.qualifications,
        description=payload.description,
    )
    return {
        "id_review": review.id_review,
        "id_book": review.id_book,
        "qualifications": review.qualifications,
        "description": review.description,
    }


@router.get("/reviews/me", response_model=None)
def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, int | str | None]]:
    reviews = ReviewService(db).get_reviews_by_user(current_user.id_user)
    return [
        {
            "id_review": review.id_review,
            "id_book": review.id_book,
            "qualifications": review.qualifications,
            "description": review.description,
        }
        for review in reviews
    ]


@router.get("/reviews/{book_id}", response_model=None)
def get_my_review(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, int | str | None] | None:
    review = ReviewService(db).get_review(current_user.id_user, book_id)
    if review is None:
        return None
    return {
        "id_review": review.id_review,
        "id_book": review.id_book,
        "qualifications": review.qualifications,
        "description": review.description,
    }


@router.delete(
    "/reviews/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_my_review(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    deleted = ReviewService(db).delete_review(current_user.id_user, book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="No tienes una reseña para este libro.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
