from datetime import datetime, timedelta
from typing import final

import pytest
from aioddd import IdInvalidError, Timestamp

from project.libs.user.domain.errors import (
    UserEmailNotValidError,
    UserPasswordNotValidError,
    UserRefreshTokenExpirationInNotValidError,
    UserRefreshTokenNotValidError,
)
from project.libs.user.domain.properties import (
    UserEmail,
    UserId,
    UserPassword,
    UserRefreshToken,
    UserRefreshTokenExpirationIn,
)
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserRefreshTokenExpirationInMother,
)


@final
class TestUserProps:
    @staticmethod
    @pytest.mark.parametrize('value', ['', '0'])
    def test_id_fails(value: str) -> None:
        pytest.raises(IdInvalidError, lambda: UserId(value))

    @staticmethod
    @pytest.mark.parametrize('value', ['test', '@project.com'])
    def test_email_fails(value: str) -> None:
        pytest.raises(UserEmailNotValidError, lambda: UserEmail(value))

    @staticmethod
    @pytest.mark.parametrize('value', ['secret', '0' * 101])
    def test_password_fails(value: str) -> None:
        pytest.raises(UserPasswordNotValidError, lambda: UserPassword(value, False))

    @staticmethod
    @pytest.mark.parametrize('value', ['', 'A' * 6, 'a' * 6, '0' * 7])
    def test_refresh_token_fails(value: str) -> None:
        pytest.raises(UserRefreshTokenNotValidError, lambda: UserRefreshToken(value))

    @staticmethod
    @pytest.mark.test
    def test_refresh_token_successfully() -> None:
        assert isinstance(UserRefreshToken('0' * 6), UserRefreshToken)

    @staticmethod
    @pytest.mark.parametrize('value', [1606006344])
    def test_refresh_token_expiration_successfully(value: int) -> None:
        assert isinstance(UserRefreshTokenExpirationIn(value), UserRefreshTokenExpirationIn)

    @staticmethod
    @pytest.mark.parametrize('value', [1523443804214])
    def test_refresh_token_expiration_in_fails(value: int) -> None:
        pytest.raises(UserRefreshTokenExpirationInNotValidError, lambda: UserRefreshTokenExpirationIn(value))

    @staticmethod
    @pytest.mark.test
    def test_refresh_token_expiration_in_has_fifteen_minutes_passed() -> None:
        timestamp_obj = Timestamp(int((datetime.now() - timedelta(minutes=15, seconds=1)).timestamp()))
        assert True is UserRefreshTokenExpirationInMother.create(timestamp_obj.value()).has_fifteen_minutes_passed()

    @staticmethod
    @pytest.mark.test
    def test_refresh_token_expiration_in_has_fifteen_minutes_not_passed() -> None:
        timestamp_obj = Timestamp(int((datetime.now() + timedelta(minutes=15, seconds=1)).timestamp()))
        assert False is UserRefreshTokenExpirationInMother.create(timestamp_obj.value()).has_fifteen_minutes_passed()
