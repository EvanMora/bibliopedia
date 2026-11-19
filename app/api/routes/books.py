"""Rutas relacionadas con el catálogo de libros (/books)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import Book
from app.repositories import get_db
from app.services import BookService

router = APIRouter()


@router.get("/books/search", response_model=None)
def search_books(keyword: str, db: Session = Depends(get_db)) -> list[Book]:
    """Busca libros por título, autor o ISBN (búsqueda parcial)."""
    return BookService(db).search_books(keyword)


@router.get("/books/{id_book}", response_model=None)
def get_book(id_book: int, db: Session = Depends(get_db)) -> Book:
    """Retorna un libro por su id."""
    return BookService(db).get_book_by_id(id_book)
