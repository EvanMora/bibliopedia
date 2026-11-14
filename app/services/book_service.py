from sqlalchemy.orm import Session

from app.core.exceptions import BookNotFoundError
from app.models import Book
from app.repositories import BookRepository


class BookService:
    """Lógica de negocio del catálogo de libros."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.book_repository = BookRepository(db)

    def search_books(self, keyword: str) -> list[Book]:
        """Busca libros por título, autor o ISBN (búsqueda parcial)."""
        keyword = (keyword or "").strip()
        if not keyword:
            return []
        return self.book_repository.search(keyword)

    def get_book_by_id(self, id_book: int) -> Book:
        """Retorna un libro por su id o lanza excepción si no existe."""
        book = self.book_repository.get_by_id(id_book)
        if book is None:
            raise BookNotFoundError(f"Book con id_book={id_book} no encontrado")
        return book
