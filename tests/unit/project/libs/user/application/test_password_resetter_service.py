from typing import final
from unittest.mock import Mock

import pytest
from aioddd.testing import mock

from project.libs.user.application.password_resetter_service import (
    UserPasswordResetterService,
)
from project.libs.user.domain.repositories import UserNotifier, UserRepository
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserPasswordMother,
    UserRefreshTokenExpirationInMother,
    UserRefreshTokenMother,
)


@final
class TestUserPasswordResetterService:
    _mock_user_repository: Mock
    _sut: UserPasswordResetterService

    def setup(self) -> None:
        self._mock_user_repository = mock(UserRepository, ['find_email_and_refresh_token', 'save_and_publish'])
        self._mock_user_notifier = mock(UserNotifier, ['notify_user_password_resetted'])
        self._sut = UserPasswordResetterService(self._mock_user_repository, self._mock_user_notifier)

    @pytest.mark.asyncio
    async def test_reset_password_successfully(self) -> None:
        user = UserMother.from_password_and_forgotten_password(
            UserPasswordMother.create(value='secret123456', hashed=False),
            UserRefreshTokenMother.random(),
            UserRefreshTokenExpirationInMother.random(),
        )
        self._mock_user_repository.find_email_and_refresh_token.return_value = user
        self._mock_user_notifier.notify_user_password_resetted.return_value = None
        self._mock_user_repository.save_and_publish.return_value = None

        kwargs = {
            'user_email': user.email(),
            'user_refresh_token': user.refresh_token(),
            'new_password': UserPasswordMother.random(),
        }

        await self._sut(**kwargs)

        self._mock_user_repository.find_email_and_refresh_token.assert_called_once_with(
            kwargs['user_email'], kwargs['user_refresh_token']
        )
        self._mock_user_notifier.notify_user_password_resetted.assert_called_once()
        self._mock_user_repository.save_and_publish.assert_called_once_with(user)
