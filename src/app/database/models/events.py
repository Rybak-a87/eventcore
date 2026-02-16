from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, ForeignKey, UniqueConstraint, text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.database.session import Base


class Event(Base):
    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    event_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    is_email_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    type_id: Mapped[int] = mapped_column(ForeignKey("event_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    type: Mapped["EventType"] = relationship("EventType", backref="events")

    category_id: Mapped[int] = mapped_column(ForeignKey("event_categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    category: Mapped["EventCategory"] = relationship("EventCategory", backref="events")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="events")

    images: Mapped[list["EventImage"]] = relationship("EventImage", back_populates="event",
                                                         cascade="all, delete-orphan")
    shared_with: Mapped[list["SharedEvent"]] = relationship("SharedEvent", back_populates="event",
                                                            cascade="all, delete-orphan")

    def __repr__(self):
        return self.title

    __table_args__ = (
        UniqueConstraint("title", "user_id", name="uq_event_title_user"),
        Index("ix_event_user_active", "user_id", "active"),
        Index("ix_event_category_datetime", "category_id", "event_datetime"),
    )


class EventType(Base):
    __tablename__ = "event_types"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    user: Mapped["User | None"] = relationship("User", back_populates="event_types")

    __table_args__ = (
        UniqueConstraint("name", "user_id", name="uq_type_name_user"),
    )

    def __repr__(self):
        return self.name


class EventCategory(Base):
    __tablename__ = "event_categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    user: Mapped["User | None"] = relationship("User", back_populates="categories")

    __table_args__ = (
        UniqueConstraint("name", "user_id", name="uq_category_name_user"),
    )

    def __repr__(self):
        return self.name

class EventImage(Base):
    __tablename__ = "event_images"

    image_url: Mapped[str | None] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    event: Mapped["Event"] = relationship("Event", back_populates="images")

    # def get_url(self) -> str:
    #     return f"{settings.media_dir}/users/{self.image_url}"


class SharedEvent(Base):
    __tablename__ = "shared_events"

    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    event: Mapped["Event"] = relationship("Event", back_populates="shared_with")
    for_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    for_user: Mapped["User"] = relationship("User", back_populates="shared_events")

    __table_args__ = (
        UniqueConstraint("event_id", "for_user_id", name="uq_sharedevent_event_for_user"),
        Index("ix_shared_events_active", "active"),
    )
