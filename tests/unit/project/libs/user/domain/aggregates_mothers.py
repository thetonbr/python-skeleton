from typing import Optional, final

from project.libs.user.domain.aggregates import User
from project.libs.user.domain.properties import (
    UserEmail,
    UserId,
    UserPassword,
    UserRefreshToken,
    UserRefreshTokenExpirationIn,
)
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
    UserPasswordMother,
    UserRefreshTokenExpirationInMother,
    UserRefreshTokenMother,
)


@final
class UserMother:
    @staticmethod
    def create(
        user_id: UserId,
        user_email: UserEmail,
        user_password: UserPassword,
        user_refresh_token: Optional[UserRefreshToken],
        user_refresh_token_expiration_in: Optional[UserRefreshTokenExpirationIn],
    ) -> User:
        return User(user_id, user_email, user_password, user_refresh_token, user_refresh_token_expiration_in)

    @classmethod
    def from_password(cls, user_password: UserPassword) -> User:
        return cls.create(UserIdMother.random(), UserEmailMother.random(), user_password, None, None)

    @classmethod
    def from_password_and_forgotten_password(
        cls,
        user_password: UserPassword,
        user_refresh_token: UserRefreshToken,
        user_refresh_token_expiration_in: UserRefreshTokenExpirationIn,
    ) -> User:
        return cls.create(
            UserIdMother.random(),
            UserEmailMother.random(),
            user_password,
            user_refresh_token,
            user_refresh_token_expiration_in,
        )

    @classmethod
    def random_with_forgotten_password(cls) -> User:
        return cls.create(
            UserIdMother.random(),
            UserEmailMother.random(),
            UserPasswordMother.random(),
            UserRefreshTokenMother.random(),
            UserRefreshTokenExpirationInMother.random(),
        )

    @classmethod
    def random(cls) -> User:
        return cls.create(UserIdMother.random(), UserEmailMother.random(), UserPasswordMother.random(), None, None)
