from sqlalchemy.orm import Session

from app.models import BookList
from app.repositories.base import BaseRepository


class BookListRepository(BaseRepository[BookList]):
    """Repositorio encargado de las listas de lectura de los usuarios."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, BookList)

    def get_by_user_and_book(self, id_user: int, id_book: int) -> BookList | None:
        """Busca el estado de lectura de un libro en la lista de un usuario."""
        return (
            self.db.query(BookList)
            .filter(BookList.id_user == id_user, BookList.id_book == id_book)
            .first()
        )

    def get_by_user(self, id_user: int) -> list[BookList]:
        """Retorna todas las entradas de la lista de lectura de un usuario."""
        return self.db.query(BookList).filter(BookList.id_user == id_user).all()
