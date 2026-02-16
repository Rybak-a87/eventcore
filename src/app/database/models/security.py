from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    token_type: Mapped[str] = mapped_column(default="bearer")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship("User" ,back_populates="refresh_tokens")

    def __repr__(self):
        return f"Refresh Token ID: {self.id}"
