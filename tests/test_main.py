from fastapi.testclient import TestClient

from app.main import app

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
