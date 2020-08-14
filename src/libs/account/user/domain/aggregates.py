from typing import final

from aioddd import AggregateRoot

from src.libs.account.user.domain.errors import UserPasswordNotMatchError
from src.libs.account.user.domain.events import UserPasswordChanged, UserRegistered, UserDeleted
from src.libs.account.user.domain.properties import UserEmail, UserPassword
from src.libs.shared.domain.user.properties import UserId


@final
class User(AggregateRoot):
    _id: UserId
    _email: UserEmail
    _password: UserPassword

    def __init__(self, user_id: UserId, email: UserEmail, password: UserPassword) -> None:
        super().__init__()
        self._id = user_id
        self._email = email
        self._password = password

    @classmethod
    def register(cls, user_id: UserId, email: UserEmail, password: UserPassword) -> 'User':
        user = cls(user_id, email, password)
        user.record_aggregate_event(UserRegistered(user_id, email))
        return user

    def delete(self) -> None:
        self.record_aggregate_event(UserDeleted(self._id, self._email))

    def validate_password(self, password: str) -> None:
        if not self._password.check(password):
            raise UserPasswordNotMatchError.create()

    def change_password(self, old_password: str, new_password: UserPassword) -> None:
        self.validate_password(old_password)
        self._password = new_password
        self.record_aggregate_event(UserPasswordChanged(self._id, self._email))

    def id(self) -> UserId:
        return self._id

    def email(self) -> UserEmail:
        return self._email

    def password(self) -> UserPassword:
        return self._password
