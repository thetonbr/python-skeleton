from typing import final
from unittest.mock import Mock

import pytest
from aioddd.testing import mock

from project.libs.user.application.deleter_service import UserDeleterService
from project.libs.user.domain.repositories import UserRepository
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother


@final
class TestUserDeleterService:
    _mock_user_repository: Mock
    _sut: UserDeleterService

    def setup(self) -> None:
        self._mock_user_repository = mock(UserRepository, ['find', 'delete_and_publish'])
        self._sut = UserDeleterService(self._mock_user_repository)

    @pytest.mark.asyncio
    async def test_delete_successfully(self) -> None:
        user = UserMother.random()
        self._mock_user_repository.find.return_value = user

        kwargs = {
            'user_id': user.id(),
        }

        await self._sut(**kwargs)

        self._mock_user_repository.find.assert_called_once_with(kwargs['user_id'])
        self._mock_user_repository.delete_and_publish.assert_called_once_with(user)
