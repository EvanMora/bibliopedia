from app.models import Book, BookList, User


def test_mark_as_read_creates_entry(client, db, register_user):
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
    account = register_user(name="Ana García", email="ana-list@example.com")

    response = client.patch(
        f"/booklists/{account['id_user']}/books/{book.id_book}/read-status",
        params={"is_read": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_read"] is True
    assert data["id_user"] == account["id_user"]
    assert data["id_book"] == book.id_book


def test_mark_as_pending(client, db, register_user):
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
    account = register_user(name="Ana García", email="ana-pending@example.com")

    response = client.patch(
        f"/booklists/{account['id_user']}/books/{book.id_book}/read-status",
        params={"is_read": False},
    )

    assert response.status_code == 200
    assert response.json()["is_read"] is False


def test_book_can_be_removed_from_own_library(client, db, register_user):
    account = register_user(email="remove@example.com")
    book = Book(
        ISBN="9780132350884",
        book_title="Clean Code",
        book_author="Robert C. Martin",
        year_of_publication=2008,
        publisher="Prentice Hall",
    )
    db.add(book)
    db.commit()
    client.patch(
        f"/booklists/{account['id_user']}/books/{book.id_book}/read-status",
        params={"is_read": False},
    )

    response = client.delete(f"/booklists/{account['id_user']}/books/{book.id_book}")

    assert response.status_code == 204
    assert client.get(f"/booklists/{account['id_user']}").json() == []
    assert client.delete(
        f"/booklists/{account['id_user']}/books/{book.id_book}"
    ).status_code == 404
