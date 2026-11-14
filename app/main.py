from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.router import router
from app.core.exceptions import (
    BibliopediaError,
    BookListNotFoundError,
    BookNotFoundError,
    BusinessRuleViolationError,
    UserNotFoundError,
)

app = FastAPI()

app.include_router(router)


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
    return {"mensaje": "Hola bibliopedia"}
