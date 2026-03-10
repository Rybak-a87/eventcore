from fastapi import Form
from pydantic import EmailStr


class OAuth2AdminForm:
    """
    Form for Swagger Authorize
    """
    def __init__(
        self,
        username: EmailStr = Form(...),
        password: str = Form(...),
    ):
        self.username = username
        self.password = password
