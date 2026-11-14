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
