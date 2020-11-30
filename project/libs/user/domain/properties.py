from datetime import datetime, timedelta
from functools import lru_cache
from secrets import randbelow
from time import time
from typing import final

from aioddd import Id, Timestamp
from bcrypt import checkpw, gensalt, hashpw
from validators import ValidationFailure, email

from project.libs.user.domain.errors import (
    UserEmailNotValidError,
    UserPasswordNotValidError,
    UserRefreshTokenExpirationInNotValidError,
    UserRefreshTokenNotValidError,
)


class UserId(Id):
    pass


@final
class UserEmail:
    __slots__ = '_value'

    def __init__(self, value: str) -> None:
        if isinstance((err := email(value)), ValidationFailure):
            raise UserEmailNotValidError.create(detail={'email': value}).with_exception(err)
        self._value = value

    def value(self) -> str:
        return self._value


@final
class UserPassword:
    __slots__ = '_value'

    def __init__(self, value: str, hashed: bool = False) -> None:
        if hashed:
            self._value = value.encode('utf8')
        else:
            length = len(value)
            if length < 8 or length > 100:
                raise UserPasswordNotValidError.create(detail={'min': 8, 'max': 100, 'val': value})
            try:
                self._value = hashpw(bytes(value, encoding='utf8'), self._salt())
            except Exception as err:  # pragma: no cover
                raise UserPasswordNotValidError.create().with_exception(err)  # pragma: no cover

    @staticmethod
    @lru_cache
    def _salt() -> bytes:
        return gensalt(10)

    def value(self) -> str:
        return self._value.decode('utf-8')

    def check(self, plain: str) -> bool:
        try:
            return bool(checkpw(plain.encode('utf8'), self._value))
        except Exception as err:  # pragma: no cover
            raise UserPasswordNotValidError.create().with_exception(err)  # pragma: no cover


@final
class UserRefreshToken:
    __slots__ = '_value'

    def __init__(self, value: str) -> None:
        if not value.isdigit() or len(value) != 6:
            raise UserRefreshTokenNotValidError.create(detail={'refresh_token': value})
        self._value = value

    @classmethod
    def generate(cls) -> 'UserRefreshToken':
        return cls(''.join([str(randbelow(9)) for _ in range(6)]))

    def value(self) -> str:
        return self._value


@final
class UserRefreshTokenExpirationIn(Timestamp):
    _minutes = 15

    def __init__(self, value: int) -> None:
        try:
            super().__init__(value)
        except Exception as err:
            raise UserRefreshTokenExpirationInNotValidError.create(
                detail={'refresh_token_expiration_in': value}
            ).with_exception(err)

    @classmethod
    def minutes(cls) -> int:
        return cls._minutes

    @classmethod
    def generate(cls) -> 'UserRefreshTokenExpirationIn':
        return cls(int((datetime.now() + timedelta(minutes=cls.minutes())).timestamp()))

    def has_fifteen_minutes_passed(self) -> bool:
        return (self.diff(Timestamp.now()).total_seconds() / 900) >= 1

    @classmethod
    def now(cls) -> 'UserRefreshTokenExpirationIn':
        return cls(int(time()))

    def value(self) -> int:
        return self._value
