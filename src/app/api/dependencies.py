from fastapi import Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SecurityService, TokenExtractor
from app.database.session import get_session
from app.schemas.accounts import UserCheck
from app.services.auth import AuthService
from app.services.accounts import UserService
from app.services.events import EventService


token_extractor = TokenExtractor()


def get_current_user(token: str = Depends(token_extractor)) -> int:
    return SecurityService().get_current_user(token)


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(session)


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


def get_event_service(session: AsyncSession = Depends(get_session)) -> EventService:
    return EventService(session)
