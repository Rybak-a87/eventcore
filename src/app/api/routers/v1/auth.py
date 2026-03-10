from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response, Request, HTTPException

# from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service, get_current_user
from app.schemas.auth import Authenticate, Register
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
    request: Request,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """
    ## Login user
    """
    content_type = (request.headers.get("content-type") or "").lower()

    login: str | None = None
    password: str | None = None

    if "application/json" in content_type:
        data = await request.json()
        if not isinstance(data, dict):
            raise HTTPException(status_code=422, detail="Invalid JSON payload")
        # Support multiple client shapes:
        # - {login, password} (preferred)
        # - {username, password} or {email, password}
        # - {username, email, password} (use email as login fallback)
        login = data.get("login") or data.get("email") or data.get("username")
        password = data.get("password")
        if login is not None and password is not None:
            Authenticate(login=login, password=password)
    else:
        form = await request.form()
        login = form.get("username") or form.get("login")
        password = form.get("password")

    if not login or not password:
        raise HTTPException(status_code=422, detail="Fields 'login' (or 'username'/'email') and 'password' are required")

    return await service.authenticate_user(login=str(login), password=str(password), response=response)


@router.post("/logout")
async def logout(
    response: Response,
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)]
) -> dict[str, Any]:
    """
    ## Logout user
    """
    result = await service.logout_user(user_id=user_id)
    response.delete_cookie("refresh_token", path="/")
    response.delete_cookie("access_token", path="/")
    return result


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
