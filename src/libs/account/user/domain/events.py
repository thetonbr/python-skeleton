from typing import final

from aioddd import Event

from src.libs.account.user.domain.properties import UserEmail
from src.libs.shared.domain.user.properties import UserId


@final
class UserRegistered(Event):
    def __init__(self, user_id: UserId, email: UserEmail) -> None:
        super().__init__({'id': user_id, 'email': email})

    def id(self) -> UserId:
        return self._attributes['id']

    def email(self) -> UserEmail:
        return self._attributes['email']


@final
class UserDeleted(Event):
    def __init__(self, user_id: UserId, email: UserEmail) -> None:
        super().__init__({'id': user_id, 'email': email})

    def id(self) -> UserId:
        return self._attributes['id']

    def email(self) -> UserEmail:
        return self._attributes['email']


@final
class UserPasswordChanged(Event):
    def __init__(self, user_id: UserId, email: UserEmail) -> None:
        super().__init__({'id': user_id, 'email': email})

    def id(self) -> UserId:
        return self._attributes['id']

    def email(self) -> UserEmail:
        return self._attributes['email']
