from app.core.security import verify_password
from app.models import AuthSession, User
from app.services.auth_service import bootstrap_admin


def test_registration_creates_hashed_reader_and_revocable_session(client, db):
    response = client.post(
        "/auth/register",
        json={
            "name": "Lector",
            "email": " LECTOR@example.com ",
            "password": "una-clave-segura-123",
        },
    )

    assert response.status_code == 201
    user_data = response.json()["user"]
    user = db.get(User, user_data["id_user"])
    assert user.email == "lector@example.com"
    assert user.role == "reader"
    assert user.password != "una-clave-segura-123"
    assert verify_password("una-clave-segura-123", user.password)
    assert "httponly" in response.headers["set-cookie"].lower()
    assert len(db.query(AuthSession).all()) == 1
    assert client.get("/auth/me").json()["user"]["id_user"] == user.id_user

    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 204
    assert client.get("/auth/me").status_code == 401
    assert db.query(AuthSession).count() == 0


def test_authentication_validation_and_private_routes(client, register_user):
    user = register_user(email="private@example.com")
    client.post("/auth/logout")

    assert client.post(
        "/auth/login",
        json={"email": "private@example.com", "password": "wrong-password"},
    ).status_code == 401
    assert client.get(f"/booklists/{user['id_user']}").status_code == 401
    assert client.post(
        "/auth/register",
        json={
            "name": "Otro lector",
            "email": "private@example.com",
            "password": "another-secure-password",
        },
    ).status_code == 409
    assert client.post(
        "/auth/register",
        json={"name": "Short", "email": "short@example.com", "password": "short"},
    ).status_code == 422


def test_readers_cannot_access_other_users_or_admin_routes(client, register_user):
    first_user = register_user(email="first@example.com")
    client.post("/auth/logout")
    register_user(email="second@example.com")

    assert client.get(f"/booklists/{first_user['id_user']}").status_code == 403
    assert client.get("/admin/users").status_code == 403


def test_configured_admin_can_manage_roles_but_not_demote_self(client, db, register_user):
    admin = register_user(email="admin@example.com")
    client.post("/auth/logout")
    reader = register_user(email="reader@example.com")
    client.post("/auth/logout")
    bootstrap_admin(db, "admin@example.com", "configured-admin-password")
    login_response = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "configured-admin-password"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["user"]["role"] == "admin"
    assert client.get("/admin/users").status_code == 200
    assert client.patch(
        f"/admin/users/{reader['id_user']}/role",
        json={"role": "admin"},
    ).json()["user"]["role"] == "admin"
    assert client.patch(
        f"/admin/users/{admin['id_user']}/role",
        json={"role": "reader"},
    ).status_code == 400
