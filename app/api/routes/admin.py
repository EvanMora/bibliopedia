"""Operaciones de administración protegidas por rol."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.models import User
from app.repositories import get_db
from app.services.auth_service import public_user

router = APIRouter(prefix="/admin", tags=["administración"])


class RoleUpdate(BaseModel):
    role: str = Field(pattern="^(reader|admin)$")


@router.get("/users")
def list_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[dict[str, int | str]]:
    users = db.query(User).order_by(User.id_user).all()
    return [public_user(user) for user in users]


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: RoleUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, dict[str, int | str]]:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="No se encontró el usuario.")
    if user.id_user == admin.id_user and payload.role != "admin":
        raise HTTPException(status_code=400, detail="No puedes quitarte tu propio rol de administrador.")
    if user.role == "admin" and payload.role == "reader":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="No puedes quitar el último rol de administrador.",
            )
    user.role = payload.role
    db.commit()
    return {"user": public_user(user)}
