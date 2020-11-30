from dataclasses import dataclass
from typing import final

from aioddd import Event

from project.libs.user.domain.properties import (
    UserEmail,
    UserId,
    UserRefreshToken,
    UserRefreshTokenExpirationIn,
)


@final
class UserRegistered(Event):
    @dataclass
    class Attributes:
        id: UserId
        email: UserEmail

    attributes: Attributes


@final
class UserDeleted(Event):
    @dataclass
    class Attributes:
        id: UserId
        email: UserEmail

    attributes: Attributes


@final
class UserPasswordChanged(Event):
    @dataclass
    class Attributes:
        id: UserId
        email: UserEmail

    attributes: Attributes


@final
class UserPasswordForgotten(Event):
    @dataclass
    class Attributes:
        id: UserId
        email: UserEmail
        refresh_token: UserRefreshToken
        refresh_token_expiration_in: UserRefreshTokenExpirationIn

    attributes: Attributes


@final
class UserPasswordResetted(Event):
    @dataclass
    class Attributes:
        id: UserId
        email: UserEmail
        refresh_token: UserRefreshToken
        refresh_token_expiration_in: UserRefreshTokenExpirationIn

    attributes: Attributes


@final
class UserRegisteredNotified(Event):
    @dataclass
    class Attributes:
        id: UserId
        email: UserEmail

    attributes: Attributes
