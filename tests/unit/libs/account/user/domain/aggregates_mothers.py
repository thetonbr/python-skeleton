from typing import final

from src.libs.account.user.domain.aggregates import User
from src.libs.account.user.domain.properties import UserEmail, UserPassword
from src.libs.shared.domain.user.properties import UserId
from tests.unit.libs.account.user.domain.properties_mothers import UserIdMother, UserEmailMother, UserPasswordMother


@final
class UserMother:
    @staticmethod
    def create(user_id: UserId, user_email: UserEmail, user_password: UserPassword) -> User:
        return User(user_id, user_email, user_password)

    @classmethod
    def from_password(cls, user_password: UserPassword) -> User:
        return cls.create(UserIdMother.random(), UserEmailMother.random(), user_password)

    @classmethod
    def random(cls) -> User:
        return cls.create(UserIdMother.random(), UserEmailMother.random(), UserPasswordMother.random())
