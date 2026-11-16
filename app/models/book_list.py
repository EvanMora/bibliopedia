from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.book import Book
from app.models.user import User


class BookList(Base):
    """Lista de lectura del usuario: estado (leído / por leer) de un libro."""

    __tablename__ = "BookList"

    # Clave primaria compuesta (id_user, id_book)
    id_user: Mapped[int] = mapped_column(ForeignKey("User.id_user"), primary_key=True)
    id_book: Mapped[int] = mapped_column(ForeignKey("Book.id_book"), primary_key=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user: Mapped[User] = relationship(back_populates="book_lists")
    book: Mapped[Book] = relationship(back_populates="book_lists")
