from typing import Annotated, Sequence

from fastapi import APIRouter, Depends

from app.api.dependencies import get_user_service, get_current_user
from app.schemas.accounts import UserUpdate, UserGet
from app.services.accounts import UserService


router = APIRouter(
    prefix="/user",
    tags=["Accounts"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/current-user", response_model=UserGet)
async def current_user(
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)]
) -> UserGet:
    """
    ## Return current user
    
    """
    return await service.current_user(user_id=user_id)


@router.patch("/current-user", response_model=UserUpdate)
async def update_user(
    data: UserUpdate,
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)]
):
    """
    ## Update current user

    """
    return await service.update_user(user_id=user_id, data=data)


@router.delete("/current-user")
async def delete_user(
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)]
):
    """
    ## Delete current user

    """
    return await service.delete_user(user_id=user_id)


# @router.post("/list", response_model=Sequence[UserGet])
async def get_users(
    data: UserGet,
    service: Annotated[UserService, Depends(get_user_service)]
) -> Sequence[UserGet]:
    """
    ## Return all users

    """
    return await service.get_users(data=data)


# @router.get("/list", response_model=list[UserGet])
# async def get_users(
#         username: str | None = Query(default=None),
#         email: str | None = Query(default=None),
#         phone_number: str | None = Query(default=None),
#         service: Annotated[UserService, Depends(get_user_service)] = None
# ):
#     data = UserGet(
#         username=username,
#         email=email,
#         phone_number=phone_number
#     )
#     return await service.get_users(data=data)





# @router.get("/{user_id}/photo")
# async def get_user_photo(service: Annotated[UserService, Depends(get_current_user)], user_id: int):
#     return service.get_photo_user(user_id)






# @router.put("/update", response_model=UserCreate)
# return service.update(user_id=user.id, operation_id=operation_id, operation_data=operation_data)
# @router.delete("/delete")
#     service.delete(user_id=user.id, operation_id=operation_id)
#     return Response(status_code=status.HTTP_204_NO_CONTENT)    # операция удаления возвращает код 204



