import os
import uuid
from pathlib import Path
from typing import Sequence, List, Any
from datetime import datetime, timezone

from fastapi import UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from app.core.settings import settings
from app.database.models.accounts import User
from app.database.models.events import Event, EventType, EventImage
from app.schemas.events import EventUpdate, EventCreate, EventImageRead, EventRead, EventTypeRead, EventReadDetail
from app.shared.exceptions import EventNotFound
from app.tasks.email_tasks import send_event_email


class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_event(self, user_id: int, event_id: int, data: EventUpdate) -> EventReadDetail:
        data_dict = data.model_dump(exclude_unset=True, exclude={"type"})
        event = await Event.find_with_related_first(session=self.session, related=[EventType, EventImage],
                                                    self_filters={"user_id": user_id, "id": event_id},
                                                    strategy="prefetch")
        if data.type_name:
            event_type = await (EventType
                                .find_first(session=self.session, name=data.type_name, user_id__in=[user_id, None]))
            if not event_type:
                event_type = await EventType.create(session=self.session, user_id=user_id, name=data.type_name)

            data_dict["type_id"] = event_type.id

        for field, value in data_dict.items():
            setattr(event, field, value)
        await self.session.commit()
        await self.session.refresh(event)
        if data.type_name: setattr(event, "type_name", event_type.name)
        return EventReadDetail.model_validate(event)

    async def delete_event(self, user_id: int, event_id: int) -> dict[str, int]:
        deleted = await Event.delete(session=self.session, user_id=user_id, id=event_id)
        if deleted == 0:
            raise EventNotFound()
        return {"event_id": event_id, "deleted": deleted}

    async def get_user_event(self, user_id: int, event_id: int) -> EventReadDetail:
        event = await Event.find_with_related_first(session=self.session, related=[EventType, EventImage],
                                                    self_filters={"user_id": user_id, "id": event_id},
                                                    strategy="prefetch")
        if event is None:
            raise EventNotFound()
        setattr(event, "type_name", event.type.name)
        return EventReadDetail.model_validate(event)

    async def get_user_events(self, user_id: int) -> List[EventRead]:
        events = await Event.find_with_related(session=self.session, related=[EventType, EventImage],
                                               self_filters={"user_id": user_id}, strategy="prefetch")
        for event in events:
            setattr(event, "type_name", event.type.name)
        return [EventRead.model_validate(event) for event in events]

    async def create_event(self, user_id: int, data: EventCreate) -> EventRead:
        data_dict = data.model_dump(exclude_unset=True, exclude={"type_name"})
        event_type = await EventType.find_first(session=self.session, user_id__in=[user_id, None], name=data.type_name)
        if not event_type:
            event_type = await EventType.create(session=self.session, user_id=user_id, name=data.type_name)
        data_dict["type_id"] = event_type.id
        event, _ = await Event.update_or_create(session=self.session, user_id=user_id, **data_dict)
        setattr(event, "type_name", event_type.name)
        # if files:
        #     await self.__upload_images(user_id=user_id, event=event, files=files)

        # send_event_email.delay(
        #     to=event.user.email,
        #     subject=f"Напоминание: {event.title}",
        #     body=f"Событие на {event.event_datetime}: {event.description or ''}"
        # )
        return EventRead.model_validate(event)
    
    async def get_types(self, user_id) -> List[EventTypeRead]:
        types = await EventType.find(session=self.session, user_id__in=[user_id, None])
        return [EventTypeRead.model_validate(t) for t in types]

    async def __upload_images(self, user_id: int, event: Event, files: Sequence[UploadFile]) -> list:
        MAX_PHOTOS_PER_EVENT = 5
        if len(files) > MAX_PHOTOS_PER_EVENT:
            raise HTTPException(status_code=400,
                                detail=f"Cannot upload more than {MAX_PHOTOS_PER_EVENT} photos at once")
        # existing_count = len(event.images)
        # if existing_count + len(files) > MAX_PHOTOS_PER_EVENT:
        #     raise HTTPException(400, f"You can upload at most {MAX_PHOTOS_PER_EVENT - existing_count} more photos")

        saved_images = []
        path_work_dir = os.path.join(settings.media_dir, "users", str(user_id), "events", str(event.id))
        os.makedirs(path_work_dir, exist_ok=True)
        for file in files:
            ext = os.path.splitext(file.filename)[-1]
            filename = f"{uuid.uuid4()}{ext}"
            path = os.path.join(path_work_dir, filename)
            with open(path, "wb") as f:
                content = await file.read()
                f.write(content)

            image = await EventImage.create(
                session=self.session,
                event_id=event.id,
                image_url=f"{user_id}/events/{event.id}/{filename}"
            )
            saved_images.append(image)

        return saved_images

    async def upload_images(self, user_id: int, event_id: int, files: list[UploadFile]) -> List[EventImageRead]:
        event = await Event.get_first(session=self.session, id=event_id, user_id=user_id)
        if not event:
            raise EventNotFound()
        images = await self.__upload_images(user_id=user_id, event=event, files=files)
        return [EventImageRead.model_validate(image) for image in images]

    # @staticmethod
    # async def get_image(current_user_id: int, user_id: str, event_id: str, filename: str) -> FileResponse:
    #     file_path = os.path.join(settings.media_dir, "users", user_id, "events", event_id, filename)
    #     if current_user_id != int(user_id) and not os.path.exists(file_path):
    #         raise HTTPException(status_code=404, detail="File not found")
    #     return FileResponse(file_path)

    async def get_images(self, user_id: int, event_id: int) -> List[EventImageRead]:
        event_images = await EventImage.find_join(session=self.session, related=Event,
                                                  self_filters={"event_id": event_id},
                                                  related_filters={"user_id": user_id})
        return [EventImageRead.model_validate(image) for image in event_images]
    #
    # async def delete_event_photo(self, user_id: int, photo_id: int):
    #     photo = await EventImage.get(session=self.session, id=photo_id)
    #     if not photo:
    #         raise HTTPException(404, "Photo not found")
    #
    #     # Проверяем, что ивент принадлежит пользователю
    #     event = await Event.get(session=self.session, id=photo.event_id, user_id=user_id)
    #     if not event:
    #         raise HTTPException(403, "You don't have permission to delete this photo")
    #
    #     # Удаляем файл с диска
    #     file_path = photo.image_url.lstrip("/")  # если хранится как /media/...
    #     if os.path.exists(file_path):
    #         os.remove(file_path)
    #
    #     # Удаляем запись из БД
    #     await self.session.delete(photo)
    #     await self.session.commit()
    #
    #     return {"detail": "Photo deleted successfully"}
