from app.models import Book, User


def test_create_review_book_not_marked_as_read(client, db):
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

    response = client.post(
        "/reviews",
        json={
            "user_id": user.id_user,
            "book_id": book.id_book,
            "qualifications": 5,
            "description": "Excelente lectura.",
        },
    )

    assert response.status_code == 404


def test_mark_as_read_then_create_review(client, db):
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

    mark_response = client.patch(
        f"/booklists/{user.id_user}/books/{book.id_book}/read-status",
        params={"is_read": True},
    )
    assert mark_response.status_code == 200

    response = client.post(
        "/reviews",
        json={
            "user_id": user.id_user,
            "book_id": book.id_book,
            "qualifications": 5,
            "description": "Excelente lectura.",
        },
    )
    assert response.status_code == 200
    assert response.json()["qualifications"] == 5
