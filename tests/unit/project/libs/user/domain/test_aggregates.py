from typing import final

import pytest

from project.libs.user.domain.aggregates import User
from project.libs.user.domain.errors import UserPasswordNotMatchError
from project.libs.user.domain.events import (
    UserDeleted,
    UserPasswordChanged,
    UserPasswordForgotten,
    UserPasswordResetted,
    UserRegistered,
    UserRegisteredNotified,
)
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
    UserPasswordMother,
    UserRefreshTokenExpirationInMother,
    UserRefreshTokenMother,
)


@final
class TestUser:
    @staticmethod
    def test_register() -> None:
        user = User.register(UserIdMother.random(), UserEmailMother.random(), UserPasswordMother.random())
        events = user.pull_aggregate_events()
        assert len(events) == 1
        assert isinstance(events[0], UserRegistered)

    @staticmethod
    def test_deleted() -> None:
        user = UserMother.random()
        user.delete()
        events = user.pull_aggregate_events()
        assert len(events) == 1
        assert isinstance(events[0], UserDeleted)

    @staticmethod
    def test_validate_password() -> None:
        plain_password = 'newSecret123456'
        user = UserMother.from_password(UserPasswordMother.create(plain_password, False))
        user.validate_password(plain_password)

    @staticmethod
    def test_validate_password_fails() -> None:
        user = UserMother.random()
        pytest.raises(UserPasswordNotMatchError, lambda: user.validate_password('fakeSecret123456'))

    @staticmethod
    def test_change_password() -> None:
        old_plain_password = 'oldSecret123456'
        old_password = UserPasswordMother.create(old_plain_password, False)
        user = UserMother.from_password(old_password)
        new_password = UserPasswordMother.random()
        user.change_password(old_plain_password, new_password)
        assert user.password() == new_password
        events = user.pull_aggregate_events()
        assert len(events) == 1
        assert isinstance(events[0], UserPasswordChanged)

    @staticmethod
    def test_forget_password() -> None:
        user = UserMother.from_password(UserPasswordMother.create(value='secret123456', hashed=False))
        assert user.refresh_token() is None
        assert user.refresh_token_expiration_in() is None
        user.forget_password()
        assert user.refresh_token() is not None
        assert user.refresh_token_expiration_in() is not None
        events = user.pull_aggregate_events()
        assert len(events) == 1
        assert isinstance(events[0], UserPasswordForgotten)

    @staticmethod
    def test_reset_password() -> None:
        user = UserMother.from_password_and_forgotten_password(
            UserPasswordMother.create(value='secret123456', hashed=False),
            UserRefreshTokenMother.random(),
            UserRefreshTokenExpirationInMother.random(),
        )
        new_password = UserPasswordMother.random()
        user.reset_password(new_password)
        assert user.password() == new_password
        events = user.pull_aggregate_events()
        assert len(events) == 1
        assert isinstance(events[0], UserPasswordResetted)

    @staticmethod
    def test_user_registered_notified() -> None:
        user = UserMother.random()
        user.user_registered_notified()
        events = user.pull_aggregate_events()
        assert len(events) == 1
        assert isinstance(events[0], UserRegisteredNotified)
