from sqladmin import Admin, ModelView

from app.database.models.accounts import User, Role, Contact
from app.database.models.events import Event, EventType, EventImage, SharedEvent
from app.database.session import engine



class UserAdmin(ModelView, model=User):
    # is_async = True
    name_plural = "Accounts"
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True
    # column_formatters = {}
    column_searchable_list = [User.username, User.email]
    # column_filters = []
    form_edit_rules = []
    column_sortable_list = [User.id, User.username]
    column_default_sort = ("id" , True)
    # column_details_list = []
    # column_details_exclude_list = []
    # column_formatters_detail = {}
    # column_export_list = []
    column_list = [User.id, User.username, User.email]
    form_rules = [
        "username",
        "password_hash",
        "email",
        "phone_number",
        "is_phone_verified",
        "photo_url",
        "language",
        "events",
        "roles",
        "contacts",
        "shared_events",
    ]
    # form_edit_rules = []


class RoleAdmin(ModelView, model=Role):
    form_rules = ["name"]
    column_list = [Role.id, Role.name]


class ContactAdmin(ModelView, model=Contact):
    column_list = [Contact.id, Contact.user, Contact.contact_user]


class EventAdmin(ModelView, model=Event):
    column_list = [Event.id, Event.title, Event.active]


class EventTypeAdmin(ModelView, model=EventType):
    column_searchable_list = [EventType.name]
    form_rules = ["name"]
    column_list = [EventType.id, EventType.name]

class SharedEventAdmin(ModelView, model=SharedEvent):
    column_list = [SharedEvent.id, SharedEvent.event, SharedEvent.for_user,
                   SharedEvent.accepted, SharedEvent.active]


class EventImageAdmin(ModelView, model=EventImage):
    column_list = [EventImage.id, EventImage.image_url]


def get_admin(app) -> None:
    admin = Admin(app=app, engine=engine, base_url="/admin", title="Admin", debug=True, authentication_backend=None)
    admin.add_view(UserAdmin)
    admin.add_view(RoleAdmin)
    admin.add_view(ContactAdmin)
    admin.add_view(EventAdmin)
    admin.add_view(EventTypeAdmin)
    admin.add_view(SharedEventAdmin)
    admin.add_view(EventImageAdmin)
