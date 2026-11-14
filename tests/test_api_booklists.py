from app.models import Book, BookList, User


def test_mark_as_read_creates_entry(client, db):
    user = User(name="Ana García", email="ana@example.com", password="password-cifrada")
    book = Book(
        ISBN="9780132350884",
        book_title="Clean Code",
        book_author="Robert C. Martin",
        year_of_publication=2008,
        publisher="Prentice Hall",
    )
    db.add_all([user, book])
    db.commit()

    response = client.patch(
        f"/booklists/{user.id_user}/books/{book.id_book}/read-status",
        params={"is_read": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True
    assert data["id_user"] == user.id_user
    assert data["id_book"] == book.id_book


def test_mark_as_pending(client, db):
    user = User(name="Ana García", email="ana@example.com", password="password-cifrada")
    book = Book(
        ISBN="9780132350884",
        book_title="Clean Code",
        book_author="Robert C. Martin",
        year_of_publication=2008,
        publisher="Prentice Hall",
    )
    db.add_all([user, book])
    db.commit()

    response = client.patch(
        f"/booklists/{user.id_user}/books/{book.id_book}/read-status",
        params={"is_read": False},
    )

    assert response.status_code == 200
    assert response.json()["is_read"] is False
