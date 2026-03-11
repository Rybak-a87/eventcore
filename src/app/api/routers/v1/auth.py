from typing import Annotated, Any

from fastapi import APIRouter, Depends, Form, Response, Request

# from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service, get_current_user
from app.schemas.accounts import UserRead
from app.schemas.auth import Authenticate, RegisterAuthenticate
from app.schemas.oauth2_form import OAuth2AdminForm
from app.schemas.security import TokenResponse, AccessTokenResponse
from app.services.auth import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Registration / Authentication"],
)


@router.post("/sign-up", response_model=UserRead, status_code=201)
async def sign_up(
    response: Response,
    payload: RegisterAuthenticate,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserRead:
    """
    ## Create new user
    
    :param payload:
    :param service:
    :return: User
    """
    return await service.register_user(data=payload, response=response)


@router.post("/sign-in", response_model=UserRead)
async def sign_in(
    response: Response,
    payload: RegisterAuthenticate,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserRead:
    """
    ## Login user
    
    :param payload:
    :param service:
    :return: User
    """
    return await service.authenticate_user(data=payload, response=response)


@router.post("/logout")
async def logout(
    response: Response,
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)]
) -> dict[str, Any]:
    """
    ## Logout user
    """
    return await service.logout_user(response=response, user_id=user_id)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_access_token(
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: str | None = None
) -> AccessTokenResponse:
    """
    ## Update Access Token
    """
    return await service.refresh_access_token(request=request, response=response, refresh_token=refresh_token)


@router.post("/sign-in-admin", response_model=TokenResponse)
async def sign_in(
        service: Annotated[AuthService, Depends(get_auth_service)],
        payload: OAuth2AdminForm = Depends(),
) -> TokenResponse:
    """
    ## Login Admin
    
    :param payload:
    :param service:
    :return: Token
    """
    return await service.authenticate_admin(data=payload)