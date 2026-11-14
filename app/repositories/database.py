"""Configuración de la base de datos y sesión de SQLAlchemy."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base

load_dotenv()

# La ruta de la base de datos se puede sobreescribir mediante la variable de entorno DATABASE_URL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/bibliopedia.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)

# Crea las tablas definidas en los modelos si no existen.
Base.metadata.create_all(bind=engine)


def get_db():
    """Dependencia de FastAPI que provee una sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
