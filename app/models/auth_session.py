"""Sesiones opacas de autenticación con vencimiento."""

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AuthSession(Base):
    """Sesión revocable; solo se persiste el hash del token del navegador."""

    __tablename__ = "AuthSession"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    id_user: Mapped[int] = mapped_column(
        ForeignKey("User.id_user", ondelete="CASCADE"), nullable=False, index=True
    )
    expires_at: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    user: Mapped["User"] = relationship(back_populates="auth_sessions")
