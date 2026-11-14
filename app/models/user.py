from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    """Usuario registrado en la aplicación."""

    __tablename__ = "User"

    id_user: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Un usuario puede tener muchas reseñas (1:N)
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # Un usuario puede tener muchas entradas en su lista de lectura (1:N)
    book_lists: Mapped[list["BookList"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
