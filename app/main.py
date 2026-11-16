"""Punto de entrada de la aplicación Bibliopedia."""

from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect

from app.api.router import router
from app.core.exceptions import (
    BibliopediaError,
    BookListNotFoundError,
    BookNotFoundError,
    BusinessRuleViolationError,
    UserNotFoundError,
)
from app.models import Base
from app.repositories.database import SessionLocal, engine
from app.seed import seed_demo_data
from app.services.auth_service import bootstrap_admin


def migrate_user_role_column() -> None:
    """Añade el rol por defecto a bases existentes creadas antes de autenticación."""
    columns = {column["name"] for column in inspect(engine).get_columns("User")}
    if "role" not in columns:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                'ALTER TABLE "User" ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT \'reader\''
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea las tablas y siembra los libros iniciales al arrancar la aplicación."""
    Base.metadata.create_all(bind=engine)
    migrate_user_role_column()
    with SessionLocal() as db:
        seed_demo_data(db)
        bootstrap_admin(
            db,
            os.getenv("BIBLIOPEDIA_ADMIN_EMAIL"),
            os.getenv("BIBLIOPEDIA_ADMIN_PASSWORD"),
        )

    # Completa el catálogo desde data/books.csv sin volver a insertar ISBN existentes.
    from app.scripts.seed_books import seed_books

    seed_books()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.exception_handler(BibliopediaError)
async def bibliopedia_exception_handler(request: Request, exc: BibliopediaError):
    """Mapea las excepciones del dominio a códigos de estado HTTP."""
    if isinstance(exc, BusinessRuleViolationError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, (BookNotFoundError, BookListNotFoundError, UserNotFoundError)):
        status_code = status.HTTP_404_NOT_FOUND
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "static" / "index.html")
