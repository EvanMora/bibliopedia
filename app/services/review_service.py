from sqlalchemy.orm import Session

from app.core.exceptions import (
    BookListNotFoundError,
    BookNotFoundError,
    BusinessRuleViolationError,
    UserNotFoundError,
)
from app.models import Review
from app.repositories import (
    BookListRepository,
    BookRepository,
    ReviewRepository,
    UserRepository,
)


class ReviewService:
    """Lógica de negocio de las reseñas y calificaciones de libros."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.book_repository = BookRepository(db)
        self.book_list_repository = BookListRepository(db)
        self.review_repository = ReviewRepository(db)

    def create_review(
        self,
        user_id: int,
        book_id: int,
        qualifications: int,
        description: str | None = None,
    ) -> Review:
        """Crea una reseña/calificación para un libro.

        Reglas de negocio:
        - El usuario debe existir.
        - El libro debe existir.
        - El usuario debe haber marcado el libro como leído (BookList.is_read=True).
        - La calificación es obligatoria y la reseña (descripción) es opcional.
        """
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User con id_user={user_id} no encontrado")

        book = self.book_repository.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError(f"Book con id_book={book_id} no encontrado")

        book_list = self.book_list_repository.get_by_user_and_book(user_id, book_id)
        if book_list is None:
            raise BookListNotFoundError(
                f"El user {user_id} no tiene una entrada en su lista de lectura para el book {book_id}"
            )

        if not book_list.is_read:
            raise BusinessRuleViolationError(
                f"El user {user_id} no puede calificar el book {book_id} porque no lo marcó como leído"
            )

        return self.review_repository.create(
            Review(
                id_user=user_id,
                id_book=book_id,
                qualifications=qualifications,
                description=description,
            )
        )
