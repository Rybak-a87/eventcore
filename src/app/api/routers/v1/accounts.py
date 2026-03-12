from typing import Annotated, Sequence

from fastapi import APIRouter, Depends

from app.api.dependencies import get_user_service, get_current_user
from app.schemas.accounts import UserUpdate, UserReadDetail
from app.services.accounts import UserService


router = APIRouter(
    prefix="/user",
    tags=["Accounts"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/current-user", response_model=UserReadDetail)
async def current_user(
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)]
) -> UserReadDetail:
    """
    ## Return current user
    
    """
    return await service.current_user(user_id=user_id)


@router.patch("/current-user", response_model=UserReadDetail)
async def update_user(
    data: UserUpdate,
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)]
) -> UserReadDetail:
    """
    ## Update current user

    """
    return await service.update_user(user_id=user_id, data=data)


@router.delete("/current-user")
async def delete_user(
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)]
) -> dict:
    """
    ## Delete current user

    """
    return await service.delete_user(user_id=user_id)


# @router.post("/list", response_model=Sequence[UserReadDetail])
async def get_users(
    data: UserReadDetail,
    service: Annotated[UserService, Depends(get_user_service)]
) -> Sequence[UserReadDetail]:
    """
    ## Return all users

    """
    return await service.get_users(data=data)


# @router.get("/list", response_model=list[UserReadDetail])
# async def get_users(
#         username: str | None = Query(default=None),
#         email: str | None = Query(default=None),
#         phone_number: str | None = Query(default=None),
#         service: Annotated[UserService, Depends(get_user_service)] = None
# ):
#     data = UserReadDetail(
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



