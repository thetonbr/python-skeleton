from typing import Dict, final, Any

from aioddd import EventMapper, Event

from src.libs.account.user.domain.events import UserRegistered, UserPasswordChanged, UserDeleted
from src.libs.account.user.domain.properties import UserEmail
from src.libs.shared.domain.user.properties import UserId


@final
class UserRegisteredEventMapper(EventMapper):
    def belongs_to(self, msg: Event) -> bool:
        return isinstance(msg, UserRegistered)

    def service_name(self) -> str:
        return 'example.account'

    def name(self) -> str:
        return 'user.registered'

    def decode(self, data: Dict[str, Any]) -> Event:
        return UserRegistered(UserId(data['id']), UserEmail(data['id']))

    @staticmethod
    def map_attributes(msg: UserRegistered) -> Dict[str, Any]:
        return {
            'id': msg.id().value(),
            'email': msg.email().value(),
        }


@final
class UserDeletedEventMapper(EventMapper):
    def belongs_to(self, msg: Event) -> bool:
        return isinstance(msg, UserDeleted)

    def service_name(self) -> str:
        return 'example.account'

    def name(self) -> str:
        return 'user.deleted'

    def decode(self, data: Dict[str, Any]) -> Event:
        return UserDeleted(UserId(data['id']), UserEmail(data['email']))

    @staticmethod
    def map_attributes(msg: UserDeleted) -> Dict[str, Any]:
        return {
            'id': msg.id().value(),
            'email': msg.email().value(),
        }


@final
class UserPasswordChangedEventMapper(EventMapper):
    def belongs_to(self, msg: Event) -> bool:
        return isinstance(msg, UserPasswordChanged)

    def service_name(self) -> str:
        return 'example.account'

    def name(self) -> str:
        return 'user.password_changed'

    def decode(self, data: Dict[str, Any]) -> Event:
        return UserPasswordChanged(UserId(data['id']), UserEmail(data['id']))

    @staticmethod
    def map_attributes(msg: UserPasswordChanged) -> Dict[str, Any]:
        return {
            'id': msg.id().value(),
            'email': msg.email().value(),
        }
