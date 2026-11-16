"""Router principal de la API de Bibliopedia."""

from fastapi import APIRouter

from app.api.routes import admin, auth, books, booklists, reviews

router = APIRouter()

router.include_router(auth.router)
router.include_router(admin.router)
router.include_router(books.router)
router.include_router(booklists.router)
router.include_router(reviews.router)
