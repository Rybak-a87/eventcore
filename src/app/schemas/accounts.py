import enum
from datetime import datetime
import re
from typing import Optional, Union, List

from pydantic import BaseModel, Field, validator, constr, EmailStr, field_serializer

from app.database.enums import LanguageEnum


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    # language: LanguageEnum | None = None

    model_config = {
        "extra": "forbid",  # for .model_dump()
        "from_attributes": True
    }


class UsersUpdate(BaseModel):
    username: list[str] | None = None
    email: list[str] | None = None
    phone_number: list[str] | None = None

    # model_config = {
    #     "extra": "forbid"  # for .model_dump()
    # }


class UserRead(BaseModel):
    id: int
    email: str  | None = None
    username: str  | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str  | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    access_token: str | None = None

    model_config = {
        "from_attributes": True
    }

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime | None):
        return value.strftime("%d.%m.%Y %H:%M:%S") if value else None


class UserGetBy(BaseModel):
    id: list[int] | None = None
    username: list[str] | None = None
    email: list[str] | None = None
    phone_number: list[str] | None = None
    order_by: Union[str, List[str], None] = None
    limit: int | None = None


class UserDelete(BaseModel):
    id: int


class UserCheck(BaseModel):
    id: int

    model_config = {
        "from_attributes": True
    }
