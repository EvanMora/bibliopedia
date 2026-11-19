from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.book import Book
from app.models.user import User


class Review(Base):
    """Reseña y calificación que un usuario hace sobre un libro."""

    __tablename__ = "Review"

    id_review: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Claves foráneas hacia User y Book
    id_user: Mapped[int] = mapped_column(ForeignKey("User.id_user"), nullable=False, index=True)
    id_book: Mapped[int] = mapped_column(ForeignKey("Book.id_book"), nullable=False, index=True)

    qualifications: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship(back_populates="reviews")
    book: Mapped[Book] = relationship(back_populates="reviews")
