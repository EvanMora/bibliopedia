from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.models import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Repositorio genérico con las operaciones CRUD comunes."""

    def __init__(self, db: Session, entity_type: type[T]) -> None:
        self.db = db
        self.entity = entity_type

    def create(self, entity: T) -> T:
        """Guarda una nueva entidad en la base de datos."""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_by_id(self, id: int) -> T | None:
        """Busca una entidad por su clave primaria."""
        return self.db.get(self.entity, id)

    def get_all(self) -> list[T]:
        """Retorna todas las entidades registradas."""
        return self.db.query(self.entity).all()

    def delete(self, entity: T) -> None:
        """Elimina una entidad de la base de datos."""
        self.db.delete(entity)
        self.db.commit()

    def update(self, entity: T) -> T:
        """Confirma los cambios pendientes de una entidad."""
        self.db.commit()
        return entity
