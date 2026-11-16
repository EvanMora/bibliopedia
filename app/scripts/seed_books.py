"""Siembra de libros por defecto a partir de un CSV.

El archivo esperado es ``data/books.csv`` con separador ``;`` y las
columnas:

    ISBN;book_title;book_author;year_of_publication;publisher;image_URL_S;image_URL_M;image_URL_L

Las columnas de imagen se ignoran porque el modelo ``Book`` no las usa.
El proceso es idempotente: los ISBN que ya existen no se vuelven a insertar.
"""

import csv
import sys
from pathlib import Path

# Aseguramos que la raíz del proyecto esté en sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.models.book import Book
from app.repositories.database import engine, SessionLocal
from app.models import Base

# Ruta del CSV en el proyecto (data/books.csv, no ignorado por .gitignore)
CSV_PATH = PROJECT_ROOT / "data" / "books.csv"


def _to_int(value: str | None) -> int | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        # Algunos años vienen como "1998.0"
        try:
            return int(float(value))
        except ValueError:
            return None


def _to_str(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _iter_rows(csv_path: Path):
    """Abre el CSV intentando UTF-8 y cae a Latin-1 si no puede."""
    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as fh:
            yield from csv.DictReader(fh, delimiter=";")
    except UnicodeDecodeError:
        with open(csv_path, newline="", encoding="latin-1") as fh:
            yield from csv.DictReader(fh, delimiter=";")


def seed_books(csv_path: Path = CSV_PATH) -> dict[str, int]:
    """Lee el CSV y crea los registros que falten.

    Returns un dict con ``insertados`` y ``omitidos``.
    """
    insertados = 0
    omitidos = 0

    if not csv_path.exists():
        print(f"[seed] CSV no encontrado en {csv_path}; se omite la siembra.")
        return {"insertados": 0, "omitidos": 0}

    # Asegurar que las tablas existan antes de sembrar
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        # ISBNs existentes para evitar duplicados
        existentes = {row[0] for row in session.query(Book.ISBN).all()}

        for fila in _iter_rows(csv_path):
            # Normalizar claves del encabezado (p. ej. "Book-Title" -> "book_title")
            fila = {str(k).strip().lower().replace("-", "_"): (v or "").strip() for k, v in fila.items() if k is not None}
            isbn = _to_str(fila.get("isbn"))
            titulo = _to_str(fila.get("book_title"))
            autor = _to_str(fila.get("book_author"))
            anio = _to_int(fila.get("year_of_publication"))
            publisher = _to_str(fila.get("publisher"))

            # Campos obligatorios según el modelo Book
            if not isbn or not titulo or not autor or anio is None:
                print(f"[seed] Fila inválida omitida (ISBN={isbn}): faltan campos obligatorios.")
                omitidos += 1
                continue

            if isbn in existentes:
                omitidos += 1
                continue

            session.add(
                Book(
                    ISBN=isbn,
                    book_title=titulo,
                    book_author=autor,
                    year_of_publication=anio,
                    publisher=publisher,
                )
            )
            existentes.add(isbn)
            insertados += 1

        session.commit()

    print(f"[seed] Siembra completada: {insertados} libros insertados, {omitidos} omitidos.")
    return {"insertados": insertados, "omitidos": omitidos}


if __name__ == "__main__":
    seed_books()
