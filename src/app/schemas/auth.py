from pydantic import BaseModel, Field, EmailStr, model_validator


class RegisterAuthenticate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=3,
        max_length=72,
        description="Password must be strong"
    )


class PasswordUpdate(BaseModel):
    current_password: str = Field(min_length=3, max_length=72)
    new_password: str = Field(min_length=3, max_length=72)
    confirm_new_password: str = Field(min_length=3, max_length=72)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError("Passwords do not match")
        return self
