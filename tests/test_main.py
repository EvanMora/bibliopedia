from fastapi.testclient import TestClient

from app.main import app
from app.models import Book, Review, User
from app.seed import DEMO_BOOKS, DEMO_USER_EMAIL, seed_demo_data

# Creamos el cliente de pruebas basado en nuestra aplicación de FastAPI
client = TestClient(app)

def test_read_home():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Bibliopedia" in response.text


def test_frontend_assets_are_served():
    script_response = client.get("/static/app.js")
    stylesheet_response = client.get("/static/styles.css")

    assert script_response.status_code == 200
    assert "javascript" in script_response.headers["content-type"]
    assert stylesheet_response.status_code == 200
    assert "text/css" in stylesheet_response.headers["content-type"]


def test_seeded_catalog_supports_frontend_workflows(client, db):
    seed_demo_data(db)
    seed_demo_data(db)

    user = db.query(User).filter_by(email=DEMO_USER_EMAIL).one()
    assert db.query(Book).count() == len(DEMO_BOOKS)

    search_response = client.get("/books/search", params={"keyword": "Clean"})
    assert search_response.status_code == 200
    book = search_response.json()[0]

    list_response = client.get(f"/booklists/{user.id_user}")
    assert list_response.status_code == 200
    assert list_response.json() == []

    status_response = client.patch(
        f"/booklists/{user.id_user}/books/{book['id_book']}/read-status",
        params={"is_read": True},
    )
    assert status_response.status_code == 200

    review_response = client.post(
        "/reviews",
        json={
            "user_id": user.id_user,
            "book_id": book["id_book"],
            "qualifications": 5,
            "description": "Excelente lectura",
        },
    )
    assert review_response.status_code == 200
    assert db.query(Review).one().description == "Excelente lectura"
