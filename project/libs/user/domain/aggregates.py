from typing import Optional, final

from aioddd import AggregateRoot

from project.libs.user.domain.errors import (
    UserPasswordNotMatchError,
    UserRefreshTokenExpirationInExpiredError,
)
from project.libs.user.domain.events import (
    UserDeleted,
    UserPasswordChanged,
    UserPasswordForgotten,
    UserPasswordResetted,
    UserRegistered,
    UserRegisteredNotified,
)
from project.libs.user.domain.properties import (
    UserEmail,
    UserId,
    UserPassword,
    UserRefreshToken,
    UserRefreshTokenExpirationIn,
)


@final
class User(AggregateRoot):
    _id: UserId
    _email: UserEmail
    _password: UserPassword
    _refresh_token: Optional[UserRefreshToken]
    _refresh_token_expiration_in: Optional[UserRefreshTokenExpirationIn]

    def __init__(
        self,
        user_id: UserId,
        email: UserEmail,
        password: UserPassword,
        refresh_token: Optional[UserRefreshToken],
        refresh_token_expiration_in: Optional[UserRefreshTokenExpirationIn],
    ) -> None:
        super().__init__()
        self._id = user_id
        self._email = email
        self._password = password
        self._refresh_token = refresh_token
        self._refresh_token_expiration_in = refresh_token_expiration_in

    @classmethod
    def register(cls, user_id: UserId, email: UserEmail, password: UserPassword) -> 'User':
        user = cls(user_id, email, password, None, None)
        user.record_aggregate_event(UserRegistered(UserRegistered.Attributes(user_id, email)))
        return user

    def user_registered_notified(self) -> None:
        self.record_aggregate_event(UserRegisteredNotified(UserRegisteredNotified.Attributes(self._id, self._email)))

    def delete(self) -> None:
        self.record_aggregate_event(UserDeleted(UserDeleted.Attributes(self._id, self._email)))

    def validate_password(self, password: str) -> None:
        if not self._password.check(password):
            raise UserPasswordNotMatchError.create(detail={'email': self._email.value()})

    def change_password(self, old_password: str, new_password: UserPassword) -> None:
        self.validate_password(old_password)
        self._password = new_password
        self.record_aggregate_event(UserPasswordChanged(UserPasswordChanged.Attributes(self._id, self._email)))

    def forget_password(self) -> None:
        self._refresh_token = UserRefreshToken.generate()
        self._refresh_token_expiration_in = UserRefreshTokenExpirationIn.generate()
        self.record_aggregate_event(
            UserPasswordForgotten(
                UserPasswordForgotten.Attributes(
                    self._id, self._email, self._refresh_token, self._refresh_token_expiration_in
                )
            )
        )

    def reset_password(self, new_password: UserPassword) -> None:
        if not self._refresh_token or not self._refresh_token_expiration_in:
            return

        if self._refresh_token_expiration_in.has_fifteen_minutes_passed():
            raise UserRefreshTokenExpirationInExpiredError.create(
                detail={
                    'refresh_token_expiration_in': self._refresh_token_expiration_in.value(),
                    'limit_expiration_in': UserRefreshTokenExpirationIn.minutes(),
                    'unit_expiration_in': 'minutes',
                }
            )
        self._password = new_password
        self.record_aggregate_event(
            UserPasswordResetted(
                UserPasswordResetted.Attributes(
                    self._id, self._email, self._refresh_token, self._refresh_token_expiration_in
                )
            )
        )
        self._refresh_token = None
        self._refresh_token_expiration_in = None

    def id(self) -> UserId:
        return self._id

    def email(self) -> UserEmail:
        return self._email

    def password(self) -> UserPassword:
        return self._password

    def refresh_token(self) -> Optional[UserRefreshToken]:
        return self._refresh_token

    def refresh_token_expiration_in(self) -> Optional[UserRefreshTokenExpirationIn]:
        return self._refresh_token_expiration_in
