import enum

from sqlalchemy import String, Enum, Boolean, text, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.enums import LanguageEnum
from app.database.models.events import SharedEvent, Event
from app.database.session import Base
from app.schemas.accounts import UserGet


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), unique=True, nullable=True)
    is_phone_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[LanguageEnum] = mapped_column(Enum(LanguageEnum, name="language_enum"), nullable=False,
                                                   default=LanguageEnum.RU)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user",
                                                                cascade="all, delete-orphan")
    events: Mapped[list["Event"]] = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    categories: Mapped[list["EventCategory"]] = relationship("EventCategory", back_populates="user",
                                                             cascade="all, delete-orphan")
    event_types: Mapped[list["EventType"]] = relationship("EventType", back_populates="user",
                                                           cascade="all, delete-orphan")
    roles: Mapped[list["Role"]] = relationship("Role", secondary="user_roles", back_populates="users")
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="user",
                                                     foreign_keys="[Contact.user_id]", cascade="all, delete-orphan")
    shared_events: Mapped[list["SharedEvent"]] = relationship("SharedEvent",
                                                              back_populates="for_user", cascade="all, delete-orphan")

    async def get_shared_events(self, session: AsyncSession, active_only: bool = True) -> list["Event"]:
        events = await Event.find_join(session=session, related=SharedEvent,
                                       related_filters={"for_user_id": self.id, "active": active_only})
        return events


    async def get_contact_users(self, session: AsyncSession, accepted: bool = False) -> list["UserGet"]:
        contacts = await Contact.get(session=session, user_id=self.id, accepted=accepted)
        return [UserGet.model_validate(c.contact_user) for c in contacts]

    def __repr__(self):
        return f"User ID: {self.id} - {self.email}"


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship("User", secondary="user_roles", back_populates="roles")

    def __repr__(self):
        return self.name


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)


class Contact(Base):
    __tablename__ = "contacts"

    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    contact_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    contact_user: Mapped["User"] = relationship("User", foreign_keys=[contact_user_id], backref="contacted_by")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="contacts")
