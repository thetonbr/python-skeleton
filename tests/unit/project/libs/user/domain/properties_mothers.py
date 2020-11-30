from secrets import randbelow
from typing import final

from project.libs.user.domain.properties import (
    UserEmail,
    UserId,
    UserPassword,
    UserRefreshToken,
    UserRefreshTokenExpirationIn,
)
from tests.unit.project.libs.shared.infrastructure.tests.faker import FAKE


class UserIdMother:
    @staticmethod
    def create(value: str) -> UserId:
        return UserId(value)

    @classmethod
    def random(cls) -> UserId:
        return cls.create(UserId.generate().value())


@final
class UserEmailMother:
    @staticmethod
    def create(value: str) -> UserEmail:
        return UserEmail(value)

    @classmethod
    def random(cls) -> UserEmail:
        return cls.create(FAKE.email('project.com'))


@final
class UserPasswordMother:
    @staticmethod
    def create(value: str, hashed: bool = False) -> UserPassword:
        return UserPassword(value, hashed)

    @classmethod
    def random(cls) -> UserPassword:
        return cls.create(FAKE.random_element(['secret123456', '123456secret', 'password123456', '123456password']))


@final
class UserRefreshTokenMother:
    @staticmethod
    def create(value: str) -> UserRefreshToken:
        return UserRefreshToken(value)

    @classmethod
    def random(cls) -> UserRefreshToken:
        return cls.create(''.join([str(randbelow(9)) for _ in range(6)]))


@final
class UserRefreshTokenExpirationInMother:
    @staticmethod
    def create(value: int) -> UserRefreshTokenExpirationIn:
        return UserRefreshTokenExpirationIn(value)

    @classmethod
    def now(cls) -> UserRefreshTokenExpirationIn:
        return cls.create(UserRefreshTokenExpirationIn.now().value())

    @classmethod
    def random(cls) -> UserRefreshTokenExpirationIn:
        return cls.create(int(FAKE.date_time_between('+15m').timestamp()))
