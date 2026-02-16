from pydantic import BaseModel, Field, EmailStr


class Register(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(
        min_length=3,
        max_length=72,
        description="Password must be strong"
    )


class Authenticate(BaseModel):
    login: str = Field(min_length=3, max_length=64)
    password: str = Field(
        min_length=3,
        max_length=128,
    )
