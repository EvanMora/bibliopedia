import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, User, Book, Review, BookList
from app.repositories import (
    UserRepository,
    BookRepository,
    ReviewRepository,
    BookListRepository,
)


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


@pytest.fixture()
def user_repository(db_session):
    return UserRepository(db_session)


@pytest.fixture()
def book_repository(db_session):
    return BookRepository(db_session)


@pytest.fixture()
def review_repository(db_session):
    return ReviewRepository(db_session)


@pytest.fixture()
def book_list_repository(db_session):
    return BookListRepository(db_session)


def test_create_and_get_user(user_repository):
    user = User(name="Ana García", email="ana@example.com", password="password-cifrada")
    created_user = user_repository.create(user)

    assert created_user.id_user is not None
    assert user_repository.get_user_by_email("ana@example.com") is not None
    assert user_repository.get_by_id(created_user.id_user) is not None
    assert user_repository.get_all() == [created_user]


def test_create_and_get_book(book_repository):
    book = Book(
        ISBN="9780132350884",
        book_title="Clean Code",
        book_author="Robert C. Martin",
        year_of_publication=2008,
        publisher="Prentice Hall",
    )
    created_book = book_repository.create(book)

    assert created_book.id_book is not None
    assert book_repository.get_book_by_isbn("9780132350884") is not None
    assert book_repository.get_by_id(created_book.id_book) is not None
    assert book_repository.get_all() == [created_book]


def test_create_and_get_review(review_repository, db_session):
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
        qualifications=4,
        description="Buen libro.",
    )
    created_review = review_repository.create(review)

    assert created_review.id_review is not None
    assert review_repository.get_reviews_by_user(user.id_user) == [created_review]
    assert review_repository.get_reviews_by_book(book.id_book) == [created_review]


def test_book_list_lifecycle(book_list_repository, db_session):
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
    created_book_list = book_list_repository.create(book_list)

    found_book_list = book_list_repository.get_by_user_and_book(user.id_user, book.id_book)

    assert found_book_list is not None
    assert found_book_list.id_user == user.id_user
    assert found_book_list.id_book == book.id_book
    assert found_book_list.is_read is False
