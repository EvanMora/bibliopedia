from sqlalchemy.orm import Session

from app.core.exceptions import BookListNotFoundError, UserNotFoundError
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
        """Marca un libro como leído en la lista de lectura del usuario."""
        return self.set_is_read(user_id, book_id, True)

    def mark_as_pending(self, user_id: int, book_id: int) -> BookList:
        """Marca un libro como pendiente (por leer) en la lista de lectura del usuario."""
        return self.set_is_read(user_id, book_id, False)

    def set_is_read(self, user_id: int, book_id: int, is_read: bool) -> BookList:
        """Actualiza el estado de lectura de un libro en la lista del usuario.

        Si el usuario aún no tiene la entrada en su lista, se crea con el estado indicado.
        """
        book_list = self.book_list_repository.get_by_user_and_book(user_id, book_id)
        if book_list is None:
            return self.book_list_repository.create(
                BookList(id_user=user_id, id_book=book_id, is_read=is_read)
            )

        book_list.is_read = is_read
        return self.book_list_repository.update(book_list)

    def get_reading_list(self, user_id: int) -> list[BookList]:
        """Retorna los libros registrados en la lista de lectura del usuario."""
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User con id_user={user_id} no encontrado")
        return self.book_list_repository.get_by_user(user_id)

    def remove_from_reading_list(self, user_id: int, book_id: int) -> None:
        """Elimina un libro de la lista del usuario sin borrar su reseña."""
        if not self.book_list_repository.delete_by_user_and_book(user_id, book_id):
            raise BookListNotFoundError(
                f"El user {user_id} no tiene el book {book_id} en su lista de lectura"
            )
