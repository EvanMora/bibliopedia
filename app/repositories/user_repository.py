from sqlalchemy.orm import Session

from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repositorio encargado de las operaciones sobre los usuarios."""

    def __init__(self, db: Session) -> None:
        super().__init__(db, User)

    def get_user_by_email(self, email: str) -> User | None:
        """Busca un usuario por su correo electrónico."""
        return self.db.query(User).filter(User.email == email).first()
