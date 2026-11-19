"""Rutas relacionadas con las listas de lectura (/booklists)."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.models import BookList, User
from app.repositories import get_db
from app.services import BookListService

router = APIRouter()


@router.get("/booklists/{user_id}", response_model=None)
def get_reading_list(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BookList]:
    """Retorna la lista de lectura del usuario."""
    if user_id != current_user.id_user:
        raise HTTPException(status_code=403, detail="No puedes consultar la biblioteca de otra persona.")
    return BookListService(db).get_reading_list(user_id)


@router.patch("/booklists/{user_id}/books/{book_id}/read-status", response_model=None)
def update_read_status(
    user_id: int,
    book_id: int,
    is_read: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BookList:
    """Marca un libro como leído (is_read=True) o pendiente (is_read=False)."""
    if user_id != current_user.id_user:
        raise HTTPException(status_code=403, detail="No puedes modificar la biblioteca de otra persona.")
    return BookListService(db).set_is_read(user_id, book_id, is_read)


@router.delete(
    "/booklists/{user_id}/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_from_reading_list(
    user_id: int,
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    if user_id != current_user.id_user:
        raise HTTPException(status_code=403, detail="No puedes modificar la biblioteca de otra persona.")
    BookListService(db).remove_from_reading_list(user_id, book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
