import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Book, BookList, Review, User


@pytest.fixture()
def db_session():
    """Sesión de base de datos SQLite en memoria para los tests."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    session = session_factory()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_create_user(db_session):
    user = User(name="Ana García", email="ana@example.com", password="password-cifrada")
    db_session.add(user)
    db_session.commit()

    assert user.id_user is not None
    assert user.name == "Ana García"
    assert user.email == "ana@example.com"


def test_create_book(db_session):
    book = Book(
        ISBN="9780132350884",
        book_title="Clean Code",
        book_author="Robert C. Martin",
        year_of_publication=2008,
        publisher="Prentice Hall",
    )
    db_session.add(book)
    db_session.commit()

    assert book.id_book is not None
    assert book.ISBN == "9780132350884"
    assert book.book_title == "Clean Code"


def test_create_review(db_session):
    user = User(name="Ana García", email="ana@example.com", password="password-cifrada")
    book = Book(
        ISBN="9780132350884",
        book_title="Clean Code",
        book_author="Robert C. Martin",
        year_of_publication=2008,
        publisher="Prentice Hall",
    )
    db_session.add_all([user, book])
    db_session.commit()

    review = Review(
        id_user=user.id_user,
        id_book=book.id_book,
        qualifications=5,
        description="Excelente lectura.",
    )
    db_session.add(review)
    db_session.commit()

    assert review.id_review is not None
    assert review.qualifications == 5
    assert review.description == "Excelente lectura."
    assert review.user.email == user.email
    assert review.book.book_title == book.book_title


def test_book_list_composite_primary_key(db_session):
    user = User(name="Ana García", email="ana@example.com", password="password-cifrada")
    book = Book(
        ISBN="9780132350884",
        book_title="Clean Code",
        book_author="Robert C. Martin",
        year_of_publication=2008,
        publisher="Prentice Hall",
    )
    db_session.add_all([user, book])
    db_session.commit()

    book_list = BookList(id_user=user.id_user, id_book=book.id_book, is_read=False)
    db_session.add(book_list)
    db_session.commit()

    assert book_list.id_user == user.id_user
    assert book_list.id_book == book.id_book
    assert book_list.is_read is False
