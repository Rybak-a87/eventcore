from datetime import datetime
from typing import Optional, List

from fastapi import UploadFile
from pydantic import BaseModel, Field, field_serializer

from app.core.settings import settings
from app.database.models import EventType


class EventImageRead(BaseModel):
    id: int = Field(..., title="Image ID")
    image_url: str = Field(..., title="Image URL")
    is_primary: bool = Field(..., title="Image primary status")
    # event_id: int = Field(..., title="Event ID")

    model_config = {
        "extra": "forbid",  # for .model_dump()
        "from_attributes": True
    }

    @field_serializer("image_url")
    def serialize_datetime(self, value: str):
        return f"{settings.domain}/media/users/{value}"

class EventTypeRead(BaseModel):
    id: int = Field(...)
    name: str = Field(...)

    model_config = {
        "from_attributes": True
    }

class EventCreate(BaseModel):
    type: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    event_datetime: datetime
    is_email_sent: bool | None = None

    model_config = {
        "from_attributes": True
    }


class EventRead(BaseModel):
    id: int = Field(...)
    type_name: str =  Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    event_datetime: datetime | None = None
    # images: List[EventImageRead] | None = []

    model_config = {
        "from_attributes": True
    }

    @field_serializer("event_datetime")
    def serialize_datetime(self, value: datetime | None):
        return value.strftime("%d.%m.%Y %H:%M:%S") if value else None


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    event_datetime: datetime | None = None
    type: str | None = None

    model_config = {
        "extra": "forbid",
        "from_attributes": True
    }


class EventsDelete(BaseModel):
    event_ids: list[int]


class EventPhotoResponse(BaseModel):
    id: int
    image_url: str

    model_config = {
        "from_attributes": True  # for EventPhotoResponse.model_validate(obj)
    }
