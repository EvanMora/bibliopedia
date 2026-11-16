"""Creación de cuentas, inicio de sesión y sesiones revocables."""

import re
import time

from fastapi import HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import SESSION_COOKIE, cookie_secure
from app.core.security import hash_password, hash_session_token, new_session_token, verify_password
from app.models import AuthSession, User

SESSION_DURATION_SECONDS = 60 * 60 * 12
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def public_user(user: User) -> dict[str, int | str]:
    return {
        "id_user": user.id_user,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


def create_account(db: Session, name: str, email: str, password: str) -> User:
    normalized_email = email.strip().lower()
    if not EMAIL_PATTERN.fullmatch(normalized_email):
        raise HTTPException(status_code=422, detail="Ingresa un correo electrónico válido.")
    if len(password) < 10:
        raise HTTPException(
            status_code=422,
            detail="La contraseña debe tener al menos 10 caracteres.",
        )
    if db.query(User).filter(User.email == normalized_email).first():
        raise HTTPException(status_code=409, detail="Ya existe una cuenta con ese correo.")

    user = User(
        name=name.strip(),
        email=normalized_email,
        password=hash_password(password),
        role="reader",
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una cuenta con ese correo.") from exc
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if user is None or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El correo o la contraseña no son correctos.",
            headers={"WWW-Authenticate": "Cookie"},
        )
    return user


def start_session(db: Session, response: Response, user: User, secure: bool) -> None:
    token = new_session_token()
    db.add(
        AuthSession(
            token_hash=hash_session_token(token),
            id_user=user.id_user,
            expires_at=int(time.time()) + SESSION_DURATION_SECONDS,
        )
    )
    db.commit()
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_DURATION_SECONDS,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )


def end_session(db: Session, request: Request, response: Response) -> None:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        session = db.get(AuthSession, hash_session_token(token))
        if session is not None:
            db.delete(session)
            db.commit()
    response.delete_cookie(
        key=SESSION_COOKIE,
        httponly=True,
        secure=cookie_secure(),
        samesite="lax",
        path="/",
    )


def bootstrap_admin(db: Session, email: str | None, password: str | None) -> None:
    if not email and not password:
        return
    if not email or not password:
        raise RuntimeError(
            "BIBLIOPEDIA_ADMIN_EMAIL y BIBLIOPEDIA_ADMIN_PASSWORD deben configurarse juntos."
        )
    normalized_email = email.strip().lower()
    if not EMAIL_PATTERN.fullmatch(normalized_email) or len(password) < 10:
        raise RuntimeError(
            "El administrador necesita un correo válido y una contraseña de al menos 10 caracteres."
        )

    user = db.query(User).filter(User.email == normalized_email).first()
    if user is None:
        user = User(
            name="Administrador",
            email=normalized_email,
            password=hash_password(password),
            role="admin",
        )
        db.add(user)
    else:
        is_admin = user.role == "admin"
        user.role = "admin"
        if not is_admin:
            user.password = hash_password(password)
    db.commit()
