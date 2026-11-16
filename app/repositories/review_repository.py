from sqlalchemy.orm import Session

from app.models import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    """Repositorio encargado de las operaciones sobre las reseñas y calificaciones."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, Review)

    def get_reviews_by_book(self, id_book: int) -> list[Review]:
        """Retorna todas las reseñas de un libro."""
        return self.db.query(Review).filter(Review.id_book == id_book).all()

    def get_reviews_by_user(self, id_user: int) -> list[Review]:
        """Retorna todas las reseñas hechas por un usuario."""
        return self.db.query(Review).filter(Review.id_user == id_user).all()

    def get_by_user_and_book(self, id_user: int, id_book: int) -> Review | None:
        """Retorna la reseña del usuario para un libro si existe."""
        return (
            self.db.query(Review)
            .filter(Review.id_user == id_user, Review.id_book == id_book)
            .order_by(Review.id_review.desc())
            .first()
        )

    def delete_by_user_and_book(self, id_user: int, id_book: int) -> bool:
        """Elimina la reseña del usuario para un libro si existe."""
        review = self.get_by_user_and_book(id_user, id_book)
        if review is None:
            return False
        self.db.delete(review)
        self.db.commit()
        return True
