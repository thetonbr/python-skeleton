from typing import final
from unittest.mock import Mock

import pytest
from aioddd.testing import mock

from project.libs.user.application.password_forget_service import (
    UserPasswordForgetService,
)
from project.libs.user.domain.repositories import UserNotifier, UserRepository
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother
from tests.unit.project.libs.user.domain.properties_mothers import UserPasswordMother


@final
class TestUserPasswordForgetService:
    _mock_user_repository: Mock
    _sut: UserPasswordForgetService

    def setup(self) -> None:
        self._mock_user_repository = mock(UserRepository, ['find_email', 'save_and_publish'])
        self._mock_user_notifier = mock(UserNotifier, ['notify_user_password_forgotten'])
        self._sut = UserPasswordForgetService(self._mock_user_repository, self._mock_user_notifier)

    @pytest.mark.asyncio
    async def test_reset_password_successfully(self) -> None:
        user = UserMother.from_password(
            UserPasswordMother.create(value='secret123456', hashed=False),
        )
        self._mock_user_repository.find_email.return_value = user
        self._mock_user_notifier.notify_user_password_forgotten.return_value = None
        self._mock_user_repository.save_and_publish.return_value = None

        kwargs = {
            'user_email': user.email(),
        }

        await self._sut(**kwargs)

        self._mock_user_repository.find_email.assert_called_once_with(kwargs['user_email'])
        self._mock_user_notifier.notify_user_password_forgotten.assert_called_once()
        self._mock_user_repository.save_and_publish.assert_called_once_with(user)
