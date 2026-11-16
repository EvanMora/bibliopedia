from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Book
from app.repositories.base import BaseRepository


class BookRepository(BaseRepository[Book]):
    """Repositorio encargado de las operaciones sobre el catálogo de libros."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Book)

    def get_book_by_isbn(self, isbn: str) -> Book | None:
        """Busca un libro por su ISBN."""
        return self.db.query(Book).filter(Book.ISBN == isbn).first()

    def search(self, keyword: str) -> list[Book]:
        """Busca libros por título, autor o ISBN (búsqueda parcial)."""
        pattern = f"%{keyword}%"
        return (
            self.db.query(Book)
            .filter(
                or_(
                    Book.book_title.ilike(pattern),
                    Book.book_author.ilike(pattern),
                    Book.ISBN.ilike(pattern),
                )
            )
            .all()
        )
