from typing import Sequence, Any

from fastapi import Depends, Response, Request
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.database.models import RefreshToken
from app.database.session import get_session
from app.domain.accounts.entities import PasswordEntity, WeakPasswordError
from app.database.models.accounts import User
from app.core.security import SecurityService
from app.schemas.accounts import UserRead
from app.schemas.auth import Register, Authenticate
from app.schemas.oauth2_form import OAuth2AdminForm
from app.schemas.security import TokenResponse, AccessTokenResponse
from app.shared.exceptions import (UserAlreadyTaken, InvalidCredentials, PasswordMustBeDifferent, InvalidToken,
                                   WeakPassword, NotAuthenticated)


class AuthService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.security = SecurityService()

    @staticmethod
    def set_token_cookie(response: Response | None, key: str, token: str) -> None:
        if response:
            response.set_cookie(
                key=key,
                value=token,
                httponly=True,
                secure=settings.is_production,  # True for HTTPS
                samesite="lax",
                path="/",
            )

    async def register_user(self, data: Register, response: Response) -> UserRead:
        has_user = await User.exists(session=self.session, email=data.email)
        if has_user:
            raise UserAlreadyTaken()
        # entity = PasswordEntity(email=data.email, password=data.password)
        # try:
        #     entity.validate_password()
        # except WeakPasswordError as e:
        #     raise WeakPassword(e)
        user = await User.create(session=self.session, username=data.email, email=data.email,
                                 password_hash=self.security.hash_password(data.password))
        refresh_token = self.security.create_refresh_token(user)
        access_token = self.security.create_access_token(user)
        refresh, _ = await RefreshToken.update_or_create(session=self.session, user_id=user.id, token_type="refresh",
                                                         defaults={"token": refresh_token})

        self.set_token_cookie(response=response, key="refresh_token", token=refresh_token)
        self.set_token_cookie(response=response, key="access_token", token=access_token)

        return UserRead.model_validate(user)

    async def authenticate_user(self, data: OAuth2AdminForm, response: Response) -> UserRead:
        user: Any | None = await User.find_first(session=self.session, email=data.username)
        if not user or not self.security.verify_password(data.password, user.password_hash):
            raise InvalidCredentials()
        refresh_token = self.security.create_refresh_token(user)
        access_token = self.security.create_access_token(user)
        await RefreshToken.update_or_create(session=self.session, user_id=user.id, token_type="refresh",
                                            defaults={"token": refresh_token})

        self.set_token_cookie(response=response, key="refresh_token", token=refresh_token)
        self.set_token_cookie(response=response, key="access_token", token=access_token)

        # refresh_token, created = self.security.check_create_refresh_token(user)
        # if created:
            # await RefreshToken.update_or_create(session=self.session, user_id=user.id, token_type="refresh",
            #                                     defaults={"token": refresh_token})
        setattr(user, "access_token", access_token)
        return UserRead.model_validate(user)

    async def password_update(self, user_id: int, current_password: str, new_password: str):
        user: Any | None = await User.get(session=self.session, id=user_id)
        if not user or not self.security.verify_password(current_password, user.password_hash):
            raise InvalidCredentials()
        if self.security.verify_password(new_password, user.password_hash):
            raise PasswordMustBeDifferent()
        user.password_hash = self.security.hash_password(new_password)
        await self.session.commit()
        await RefreshToken.bulk_delete(session=self.session, user_id=user.id)

        return {"detail": "Password changed"}


    async def logout_user(self, response: Response, user_id: int) -> dict[str, Any]:
        deleted = await RefreshToken.bulk_delete(session=self.session, user_id=user_id)

        if deleted == 0:
            raise InvalidToken()

        response.delete_cookie("refresh_token", path="/")
        response.delete_cookie("access_token", path="/")

        return {"detail": "Logged out successfully"}

    async def refresh_access_token(
            self, request: Request, response: Response | None = None, refresh_token: str | None = None
    ) -> AccessTokenResponse:
        token = refresh_token or request.cookies.get("refresh_token")
        user_id = self.security.get_current_user(token)

        token_in_db = await RefreshToken.exists(session=self.session, token=token)
        if not token_in_db:
            raise NotAuthenticated()
        user = await User.get_first(session=self.session, id=user_id)
        if not user:
            raise NotAuthenticated()

        access_token = self.security.create_access_token(user)
        return AccessTokenResponse(access_token=access_token)

    async def authenticate_admin(self, username: str, password: str) -> TokenResponse:
        pass
