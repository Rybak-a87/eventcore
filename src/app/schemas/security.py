from pydantic import BaseModel


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenResponse(AccessTokenResponse):
    refresh_token: str
