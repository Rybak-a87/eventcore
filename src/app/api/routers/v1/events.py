from typing import Annotated, List, Any

from fastapi import APIRouter, Depends, Form, UploadFile, File
from starlette.responses import FileResponse

# from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_event_service, get_current_user
from app.core.settings import settings
from app.schemas.events import EventCreate, EventRead, EventUpdate, EventImageRead, \
    EventTypeRead, EventReadDetail
from app.services.events import EventService


router = APIRouter(
    prefix="/event",
    tags=["Events"],
    # dependencies=[Depends(get_current_user)]
)


@router.get("/list", status_code=201, response_model=List[EventRead])
async def get_events(
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[EventService, Depends(get_event_service)],
) -> List[EventRead]:
    """
    ## Get Events

    """
    return await service.get_user_events(user_id=user_id)

@router.get("/types", status_code=201, response_model=List[EventTypeRead])
async def get_types(
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[EventService, Depends(get_event_service)]
) -> List[EventTypeRead]:
    """
    ## Get Types

    """
    return await service.get_types(user_id=user_id)


@router.get("/{event_id}", status_code=201, response_model=EventReadDetail)
async def get_event(
    event_id: int,
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[EventService, Depends(get_event_service)]
) -> EventReadDetail:
    """
    ## Get Event

    """
    return await service.get_user_event(user_id=user_id, event_id=event_id)


@router.post("/", status_code=201, response_model=EventRead)
async def create_event(
    data: EventCreate,
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[EventService, Depends(get_event_service)],
) -> EventRead:
    """
    ## Create Event

    """
    return await service.create_event(user_id=user_id, data=data)


@router.post("/{event_id}/upload-images", status_code=201, response_model=List[EventImageRead])
async def upload_event_images(
    event_id: int,
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[EventService, Depends(get_event_service)],
    images: List[UploadFile] = File(...),
) -> List[EventImageRead]:
    """
    ## Upload Event Images

    """
    return await service.upload_images(user_id=user_id, event_id=event_id, files=images)


@router.patch("/{event_id}", response_model=EventReadDetail)
async def update_event(
    event_id: int,
    data: EventUpdate,
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[EventService, Depends(get_event_service)]
) -> EventReadDetail:
    """
    ## Update Event

    """
    return await service.update_event(user_id=user_id, event_id=event_id, data=data)


@router.delete("/{event_id}", response_model=dict[str, int])
async def delete_event(
    event_id: int,
    user_id: Annotated[int, Depends(get_current_user)],
    service: Annotated[EventService, Depends(get_event_service)],
)-> dict[str, int]:
    """
    ## Delete Event

    """
    return await service.delete_event(user_id=user_id, event_id=event_id)





# # @router.delete("/list")
# async def delete_event(
#     data: EventsDelete,
#     user_id: Annotated[int, Depends(get_current_user)],
#     service: Annotated[EventService, Depends(get_event_service)]
# ):
#     """
#     ## Delete Events
#
#     """
#     return service.delete_events(user_id=user_id, **data.model_dump())



#
#
# @router.delete("/photos/{photo_id}")
# async def delete_event_photo(
#     photo_id: int,
#     user_id: Annotated[int, Depends(get_current_user)],
#     service: Annotated[EventService, Depends(get_event_service)]
# ):
#     """
#     ## Remote Event Images
#     """
#     return await service.delete_event_photo(user_id=user_id, photo_id=photo_id)




#
# @router.get("/media/{user_id}/events/{event_id}/{filename}")
# async def get_media_file(
#     user_id: str,
#     event_id: str,
#     filename: str,
#     current_user_id: Annotated[int, Depends(get_current_user)],
#     service: Annotated[EventService, Depends(get_event_service)]
# ) -> FileResponse:
#
#     return await service.get_image(current_user_id=current_user_id, user_id=user_id, event_id=event_id, filename=filename)



