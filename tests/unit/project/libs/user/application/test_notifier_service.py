from typing import final
from unittest.mock import Mock

import pytest
from aioddd.testing import mock

from project.libs.user.application.notifier_service import UserRegisteredNotifierService
from project.libs.user.domain.repositories import UserNotifier, UserRepository
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother


@final
class TestUserRegisteredNotifierService:
    _mock_user_repository: Mock
    _mock_user_notifier: Mock
    _sut: UserRegisteredNotifierService

    def setup(self) -> None:
        self._mock_user_repository = mock(UserRepository, ['find_id_and_email', 'save_and_publish'])
        self._mock_user_notifier = mock(UserNotifier, ['notify_user_registered'])
        self._sut = UserRegisteredNotifierService(self._mock_user_repository, self._mock_user_notifier)

    @pytest.mark.asyncio
    async def test_notifier_successfully(self) -> None:
        user = UserMother.random()
        self._mock_user_repository.find_id_and_email.return_value = user
        self._mock_user_notifier.notify_user_registered.return_value = None
        self._mock_user_repository.save_and_publish.return_value = None

        kwargs = {
            'user_id': user.id(),
            'email': user.email(),
        }

        await self._sut(**kwargs)

        self._mock_user_repository.find_id_and_email.assert_called_once_with(kwargs['user_id'], kwargs['email'])
        self._mock_user_notifier.notify_user_registered.assert_called_once_with(kwargs['user_id'], kwargs['email'])
        self._mock_user_repository.save_and_publish.assert_called_once()
