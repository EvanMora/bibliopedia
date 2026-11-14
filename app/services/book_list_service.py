from sqlalchemy.orm import Session

from app.core.exceptions import UserNotFoundError
from app.models import BookList
from app.repositories import BookListRepository, BookRepository, UserRepository


class BookListService:
    """Lógica de negocio de las listas de lectura de los usuarios."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.book_repository = BookRepository(db)
        self.book_list_repository = BookListRepository(db)

    def mark_as_read(self, user_id: int, book_id: int) -> BookList:
        """Marca un libro como leído en la lista de lectura del usuario.

        Si el usuario aún no tiene la entrada en su lista, se crea con is_read=True.
        """
        book_list = self.book_list_repository.get_by_user_and_book(user_id, book_id)
        if book_list is None:
            return self.book_list_repository.create(
                BookList(id_user=user_id, id_book=book_id, is_read=True)
            )

        book_list.is_read = True
        return self.book_list_repository.update(book_list)

    def mark_as_pending(self, user_id: int, book_id: int) -> BookList:
        """Marca un libro como pendiente (por leer) en la lista de lectura del usuario.

        Si el usuario aún no tiene la entrada en su lista, se crea con is_read=False.
        """
        book_list = self.book_list_repository.get_by_user_and_book(user_id, book_id)
        if book_list is None:
            return self.book_list_repository.create(
                BookList(id_user=user_id, id_book=book_id, is_read=False)
            )

        book_list.is_read = False
        return self.book_list_repository.update(book_list)

    def get_reading_list(self, user_id: int) -> list[BookList]:
        """Retorna los libros registrados en la lista de lectura del usuario."""
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User con id_user={user_id} no encontrado")
        return self.book_list_repository.get_by_user(user_id)
