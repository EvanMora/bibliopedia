"""Registro, sesiones y perfil del usuario autenticado."""

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import cookie_secure, get_current_user
from app.models import User
from app.repositories import get_db
from app.services.auth_service import (
    authenticate,
    create_account,
    end_session,
    public_user,
    start_session,
)

router = APIRouter(prefix="/auth", tags=["autenticación"])


class RegisterPayload(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=10, max_length=128)


class LoginPayload(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)


@router.post("/register", status_code=201)
def register(
    payload: RegisterPayload,
    response: Response,
    db: Session = Depends(get_db),
) -> dict[str, dict[str, int | str]]:
    user = create_account(db, payload.name, payload.email, payload.password)
    start_session(db, response, user, cookie_secure())
    return {"user": public_user(user)}


@router.post("/login")
def login(
    payload: LoginPayload,
    response: Response,
    db: Session = Depends(get_db),
) -> dict[str, dict[str, int | str]]:
    user = authenticate(db, payload.email, payload.password)
    start_session(db, response, user, cookie_secure())
    return {"user": public_user(user)}


@router.post("/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> Response:
    end_session(db, request, response)
    response.status_code = 204
    return response


@router.get("/me")
def get_me(user: User = Depends(get_current_user)) -> dict[str, dict[str, int | str]]:
    return {"user": public_user(user)}

