from typing import Annotated, Any

from fastapi import APIRouter, Depends, Form, Response, Request

# from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service, get_current_user
from app.schemas.auth import Authenticate, Register
from app.schemas.oauth2_form import OAuth2AdminForm
from app.schemas.security import TokenResponse, AccessTokenResponse
from app.services.auth import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Registration / Authentication"],
)


@router.post("/sign-up", response_model=TokenResponse, status_code=201)
async def sign_up(
    response: Response,
    payload: Register,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """
    ## Create new user
    
    :param payload:
    :param service:
    :return: Token
    """
    return await service.register_user(data=payload, response=response)


@router.post("/sign-in", response_model=TokenResponse)
async def sign_in(
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    payload: OAuth2AdminForm = Depends(),
) -> TokenResponse:
    """
    ## Login user
    
    :param payload:
    :param service:
    :return: Token
    """
    return await service.authenticate_user(login=payload.username, password=payload.password, response=response)


@router.post("/logout")
async def logout(
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)]
) -> dict[str, Any]:
    """
    ## Logout user
    """
    return await service.logout_user(user_id=user_id)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_access_token(
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: str | None = None
) -> AccessTokenResponse:
    """
    ## Update Access Token
    """
    return await service.refresh_access_token(request=request, refresh_token=refresh_token)
