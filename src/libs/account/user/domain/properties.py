from typing import final

from bcrypt import hashpw, checkpw, gensalt
from validators import email, ValidationFailure

from src.libs.account.user.domain.errors import UserEmailNotValidError, UserPasswordNotValidError


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
                self._value = hashpw(bytes(value, encoding='utf8'), gensalt(self._salt()))
            except Exception as err:
                raise UserPasswordNotValidError.create().with_exception(err)

    @staticmethod
    def _salt() -> int:
        return 13

    def value(self) -> str:
        return self._value.decode('utf-8')

    def check(self, plain: str) -> bool:
        try:
            return bool(checkpw(plain.encode('utf8'), self._value))
        except Exception as err:
            raise UserPasswordNotValidError.create().with_exception(err)
