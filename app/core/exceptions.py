"""Excepciones personalizadas de la aplicación Bibliopedia."""


class BibliopediaError(Exception):
    """Excepción base de la aplicación."""


class EntityNotFoundError(BibliopediaError):
    """Recurso no encontrado en la base de datos."""


class UserNotFoundError(EntityNotFoundError):
    """Usuario no encontrado."""


class BookNotFoundError(EntityNotFoundError):
    """Libro no encontrado."""


class BookListNotFoundError(EntityNotFoundError):
    """Entrada de lista de lectura no encontrada."""


class BusinessRuleViolationError(BibliopediaError):
    """La operación solicitada viola una regla de negocio."""
