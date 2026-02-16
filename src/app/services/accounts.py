from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.database.models.accounts import User
from app.schemas.accounts import UserGet, UserGetBy, UserUpdate
from app.shared.exceptions import UserNotFound


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_user(self, user_id: int, data: UserUpdate) -> UserUpdate:
        user = await User.get_first(self.session, id=user_id)
        if not user:
            raise ValueError("User not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)
        return UserUpdate.model_validate(user)

    async def delete_user(self, user_id: int) -> dict:
        deleted = await User.bulk_delete(session=self.session, id=user_id)
        if deleted == 0:
            raise UserNotFound()
        return {"detail": "User deleted", "id": user_id}

    async def get_users(self, data: UserGet) -> Sequence[UserGet]:
        users = await User.get(session=self.session, **data.model_dump(exclude_unset=True))
        return [UserGet.model_validate(user) for user in users]

    async def get_users_by(self, data: UserGetBy) -> Sequence[User]:
        users = await User.find(session=self.session,
                                order_by=data.order_by,
                                limit=data.limit,
                                **data.model_dump(exclude={"order_by", "limit"}, exclude_unset=True))
        return users

    async def current_user(self, user_id: int) -> UserGet:
        user = await User.get_first(session=self.session, id=user_id)
        return UserGet.model_validate(user)

    async def upload_photo_user(self, user_id: int, file) -> dict:
        filepath = f"{settings.app_dir}/media/users/{user_id}/{file.filename}"
        with open(filepath, "wb") as f:
            f.write(await file.read())

        await User.update(self.session, filters={"user_id": user_id}, defaults={"photo_url": filepath})
        return {"photo_url": filepath}

    # async def get_photo_user(self, user_id: int) -> dict:
    #     user = await User.get_first(session=self.session, user_id=user_id)
    #     if not user or not user.photo_url:
    #         raise HTTPException(status_code=404, detail="Photo not found")
    #
    #     file_path = user.photo_url
    #     if not file_path.exists():
    #         raise HTTPException(status_code=404, detail="Photo file not found")
    #
    #     return FileResponse(file_path)

