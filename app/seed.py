"""Datos iniciales para que una instalación nueva pueda usarse inmediatamente."""

from sqlalchemy.orm import Session

from app.models import Book, User

DEMO_USER_EMAIL = "lector@bibliopedia.local"

DEMO_BOOKS = (
    {
        "ISBN": "9780132350884",
        "book_title": "Clean Code",
        "book_author": "Robert C. Martin",
        "year_of_publication": 2008,
        "publisher": "Prentice Hall",
    },
    {
        "ISBN": "9788498381494",
        "book_title": "El principito",
        "book_author": "Antoine de Saint-Exupéry",
        "year_of_publication": 1943,
        "publisher": "Salamandra",
    },
    {
        "ISBN": "9780307474728",
        "book_title": "Cien años de soledad",
        "book_author": "Gabriel García Márquez",
        "year_of_publication": 1967,
        "publisher": "Vintage Español",
    },
    {
        "ISBN": "9780141439471",
        "book_title": "Frankenstein",
        "book_author": "Mary Shelley",
        "year_of_publication": 1818,
        "publisher": "Penguin Classics",
    },
    {
        "ISBN": "9788491050297",
        "book_title": "Orgullo y prejuicio",
        "book_author": "Jane Austen",
        "year_of_publication": 1813,
        "publisher": "Penguin Clásicos",
    },
)


def seed_demo_data(db: Session) -> None:
    """Añade un usuario de prueba y libros solo si sus tablas están vacías."""
    if db.query(User).first() is None:
        db.add(
            User(
                name="Lector de prueba",
                email=DEMO_USER_EMAIL,
                password="!disabled",
            )
        )

    if db.query(Book).first() is None:
        db.add_all(Book(**book_data) for book_data in DEMO_BOOKS)

    db.commit()
