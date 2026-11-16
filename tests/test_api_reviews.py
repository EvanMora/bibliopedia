from app.models import Book, Review, User


def test_create_review_book_not_marked_as_read(client, db, register_user):
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
    account = register_user(name="Ana García", email="ana-review@example.com")

    response = client.post(
        "/reviews",
        json={
            "book_id": book.id_book,
            "qualifications": 5,
            "description": "Excelente lectura.",
        },
    )

    assert response.status_code == 404


def test_mark_as_read_then_create_review(client, db, register_user):
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
    account = register_user(name="Ana García", email="ana-review-update@example.com")

    mark_response = client.patch(
        f"/booklists/{account['id_user']}/books/{book.id_book}/read-status",
        params={"is_read": True},
    )
    assert mark_response.status_code == 200

    response = client.post(
        "/reviews",
        json={
            "book_id": book.id_book,
            "qualifications": 5,
            "description": "Excelente lectura.",
        },
    )
    assert response.status_code == 200
    assert response.json()["qualifications"] == 5


def test_review_can_be_read_and_updated(client, db, register_user):
    user = User(name="Ana García", email="ana@example.com", password="unused")
    book = Book(
        ISBN="9780132350884",
        book_title="Clean Code",
        book_author="Robert C. Martin",
        year_of_publication=2008,
        publisher="Prentice Hall",
    )
    db.add_all([user, book])
    db.commit()
    account = register_user(name="Ana García", email="ana-review-upsert@example.com")
    client.patch(
        f"/booklists/{account['id_user']}/books/{book.id_book}/read-status",
        params={"is_read": True},
    )

    first = client.post(
        "/reviews",
        json={"book_id": book.id_book, "qualifications": 4, "description": "Muy bueno"},
    )
    second = client.post(
        "/reviews",
        json={"book_id": book.id_book, "qualifications": 5, "description": "Excelente"},
    )

    assert first.status_code == second.status_code == 200
    assert db.query(Review).filter_by(id_user=account["id_user"], id_book=book.id_book).count() == 1
    assert client.get("/reviews/me").json() == [
        {
            "id_review": first.json()["id_review"],
            "id_book": book.id_book,
            "qualifications": 5,
            "description": "Excelente",
        }
    ]


def test_review_can_be_deleted_without_removing_book_from_library(client, db, register_user):
    book = Book(
        ISBN="9780132350884",
        book_title="Clean Code",
        book_author="Robert C. Martin",
        year_of_publication=2008,
        publisher="Prentice Hall",
    )
    db.add(book)
    db.commit()
    account = register_user(email="review-delete@example.com")
    client.patch(
        f"/booklists/{account['id_user']}/books/{book.id_book}/read-status",
        params={"is_read": True},
    )
    created = client.post(
        "/reviews",
        json={"book_id": book.id_book, "qualifications": 5, "description": "Excelente"},
    )
    assert created.status_code == 200

    response = client.delete(f"/reviews/{book.id_book}")

    assert response.status_code == 204
    assert db.get(Review, created.json()["id_review"]) is None
    assert client.get("/reviews/me").json() == []
    assert client.get(f"/reviews/{book.id_book}").json() is None
    assert len(client.get(f"/booklists/{account['id_user']}").json()) == 1


def test_review_deletion_requires_ownership_and_authentication(client, db, register_user):
    book = Book(
        ISBN="9780132350884",
        book_title="Clean Code",
        book_author="Robert C. Martin",
        year_of_publication=2008,
        publisher="Prentice Hall",
    )
    db.add(book)
    db.commit()
    owner = register_user(email="review-owner@example.com")
    client.patch(
        f"/booklists/{owner['id_user']}/books/{book.id_book}/read-status",
        params={"is_read": True},
    )
    client.post(
        "/reviews",
        json={"book_id": book.id_book, "qualifications": 5, "description": "Excelente"},
    )
    client.post("/auth/logout")
    register_user(email="review-other@example.com")

    assert client.delete(f"/reviews/{book.id_book}").status_code == 404
    assert db.query(Review).count() == 1

    client.post("/auth/logout")
    assert client.delete(f"/reviews/{book.id_book}").status_code == 401
    assert db.query(Review).count() == 1
