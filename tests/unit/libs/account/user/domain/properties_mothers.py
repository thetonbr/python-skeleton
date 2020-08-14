from typing import final, Union

from faker import Faker
from faker.providers import internet, misc
from faker.providers.internet import Provider as InternetProvider
from faker.providers.misc import Provider as MiscProvider

from src.libs.account.user.domain.properties import UserEmail, UserPassword
from src.libs.shared.domain.user.properties import UserId

FAKE = Faker()  # type: Union[Faker, InternetProvider, MiscProvider]
FAKE.add_provider(internet)
FAKE.add_provider(misc)


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
        return cls.create(FAKE.free_email())


@final
class UserPasswordMother:
    @staticmethod
    def create(value: str, hashed: bool = False) -> UserPassword:
        return UserPassword(value, hashed)

    @classmethod
    def random(cls) -> UserPassword:
        return cls.create(FAKE.password())
