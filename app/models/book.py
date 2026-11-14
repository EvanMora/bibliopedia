from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Book(Base):
    """Libro del catálogo de la biblioteca."""

    __tablename__ = "Book"

    id_book: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ISBN: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    book_title: Mapped[str] = mapped_column(String(255), nullable=False)
    book_author: Mapped[str] = mapped_column(String(255), nullable=False)
    year_of_publication: Mapped[int] = mapped_column(Integer, nullable=False)
    publisher: Mapped[str] = mapped_column(String(255), nullable=True)

    # Un libro puede recibir muchas reseñas (1:N)
    reviews: Mapped[list["Review"]] = relationship(back_populates="book")

    # Un libro puede estar en las listas de lectura de muchos usuarios (1:N)
    book_lists: Mapped[list["BookList"]] = relationship(back_populates="book")
