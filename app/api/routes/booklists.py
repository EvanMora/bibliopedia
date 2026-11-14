"""Rutas relacionadas con las listas de lectura (/booklists)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import BookList
from app.repositories import get_db
from app.services import BookListService

router = APIRouter()


@router.get("/booklists/{user_id}", response_model=None)
def get_reading_list(user_id: int, db: Session = Depends(get_db)) -> list[BookList]:
    """Retorna la lista de lectura del usuario."""
    return BookListService(db).get_reading_list(user_id)


@router.patch("/booklists/{user_id}/books/{book_id}/read-status", response_model=None)
def update_read_status(
    user_id: int,
    book_id: int,
    is_read: bool = True,
    db: Session = Depends(get_db),
) -> BookList:
    """Marca un libro como leído (is_read=True) o pendiente (is_read=False)."""
    return BookListService(db).set_is_read(user_id, book_id, is_read)
