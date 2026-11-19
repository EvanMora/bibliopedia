def test_search_books_empty(client):
    response = client.get("/books/search", params={"keyword": "Clean"})

    assert response.status_code == 200
    assert response.json() == []


def test_get_book_not_found(client):
    response = client.get("/books/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book con id_book=999 no encontrado"
