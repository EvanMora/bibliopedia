"""Dependencias para autenticar usuarios y validar permisos."""

import os
import time

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.models import AuthSession, User
from app.repositories import get_db
from app.core.security import hash_session_token

SESSION_COOKIE = "bibliopedia_session"


def cookie_secure() -> bool:
    return os.getenv("BIBLIOPEDIA_COOKIE_SECURE", "").lower() == "true"


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inicia sesión para continuar.",
        )

    session = db.get(AuthSession, hash_session_token(token))
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión no es válida. Inicia sesión de nuevo.",
        )
    if session.expires_at <= int(time.time()):
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión venció. Inicia sesión de nuevo.",
        )
    if session.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La cuenta asociada a esta sesión ya no existe.",
        )
    return session.user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operación requiere permisos de administrador.",
        )
    return user
