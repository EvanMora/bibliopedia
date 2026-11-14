import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.exceptions import (
    BookListNotFoundError,
    BusinessRuleViolationError,
    UserNotFoundError,
)
from app.models import Base, Book, BookList, User
from app.services import BookListService, BookService, ReviewService


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
def user(db_session):
    user = User(name="Ana García", email="ana@example.com", password="password-cifrada")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def other_user(db_session):
    user = User(name="Luis Pérez", email="luis@example.com", password="password-cifrada")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def book(db_session):
    book = Book(
        ISBN="9780132350884",
        book_title="Clean Code",
        book_author="Robert C. Martin",
        year_of_publication=2008,
        publisher="Prentice Hall",
    )
    db_session.add(book)
    db_session.commit()
    return book


@pytest.fixture()
def review_service(db_session):
    return ReviewService(db_session)


@pytest.fixture()
def book_list_service(db_session):
    return BookListService(db_session)


@pytest.fixture()
def book_service(db_session):
    return BookService(db_session)


def test_cannot_review_without_reading_list(review_service, user, book):
    """No puede calificar un libro si no tiene una entrada en su lista de lectura."""
    with pytest.raises(BookListNotFoundError):
        review_service.create_review(user.id_user, book.id_book, qualifications=5)


def test_cannot_review_unread_book(review_service, db_session, user, book):
    """No puede calificar un libro que no fue marcado como leído."""
    db_session.add(BookList(id_user=user.id_user, id_book=book.id_book, is_read=False))
    db_session.commit()

    with pytest.raises(BusinessRuleViolationError):
        review_service.create_review(user.id_user, book.id_book, qualifications=5)


def test_can_review_read_book_with_rating_and_review(review_service, db_session, user, book):
    """Puede calificar y escribir reseña cuando el libro fue marcado como leído."""
    db_session.add(BookList(id_user=user.id_user, id_book=book.id_book, is_read=True))
    db_session.commit()

    review = review_service.create_review(
        user.id_user,
        book.id_book,
        qualifications=5,
        description="Excelente lectura.",
    )

    assert review.id_review is not None
    assert review.qualifications == 5
    assert review.description == "Excelente lectura."
    assert review.id_user == user.id_user
    assert review.id_book == book.id_book


def test_can_rate_read_book_without_review_text(review_service, db_session, user, book):
    """Puede calificar sin escribir reseña (la reseña es opcional)."""
    db_session.add(BookList(id_user=user.id_user, id_book=book.id_book, is_read=True))
    db_session.commit()

    review = review_service.create_review(user.id_user, book.id_book, qualifications=3)

    assert review.qualifications == 3
    assert review.description is None


def test_create_review_user_not_found(review_service):
    with pytest.raises(UserNotFoundError):
        review_service.create_review(99999, 1, qualifications=5)


def test_mark_as_read_creates_entry(book_list_service, user, book):
    """Si no existe la entrada, al marcar como leído se crea con is_read=True."""
    book_list = book_list_service.mark_as_read(user.id_user, book.id_book)

    assert book_list.id_user == user.id_user
    assert book_list.id_book == book.id_book
    assert book_list.is_read is True


def test_mark_as_read_updates_entry(book_list_service, db_session, user, book):
    """Si existe la entrada, marca el libro como leído."""
    db_session.add(BookList(id_user=user.id_user, id_book=book.id_book, is_read=False))
    db_session.commit()

    book_list = book_list_service.mark_as_read(user.id_user, book.id_book)

    assert book_list.is_read is True


def test_mark_as_pending(book_list_service, db_session, user, book):
    """Marca un libro como pendiente (por leer)."""
    db_session.add(BookList(id_user=user.id_user, id_book=book.id_book, is_read=True))
    db_session.commit()

    book_list = book_list_service.mark_as_pending(user.id_user, book.id_book)

    assert book_list.is_read is False


def test_full_flow_user_reads_then_reviews(book_list_service, review_service, db_session, user, book):
    """Flujo completo: marcar como leído -> calificar y reseñar."""
    book_list_service.mark_as_read(user.id_user, book.id_book)

    review = review_service.create_review(
        user.id_user,
        book.id_book,
        qualifications=5,
        description="Gran libro.",
    )

    assert review.id_review is not None


def test_search_books(book_service, book):
    assert len(book_service.search_books("Clean")) == 1
    assert len(book_service.search_books("Martin")) == 1
    assert book_service.search_books("") == []
    assert book_service.search_books("Inexistente") == []
