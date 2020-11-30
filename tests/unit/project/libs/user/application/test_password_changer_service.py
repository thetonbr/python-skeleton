from typing import final
from unittest.mock import Mock

import pytest
from aioddd.testing import mock

from project.libs.user.application.password_changer_service import (
    UserPasswordChangerService,
)
from project.libs.user.domain.repositories import UserRepository
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother
from tests.unit.project.libs.user.domain.properties_mothers import UserPasswordMother


@final
class TestUserPasswordChangerService:
    _mock_user_repository: Mock
    _sut: UserPasswordChangerService

    def setup(self) -> None:
        self._mock_user_repository = mock(UserRepository, ['find', 'save_and_publish'])
        self._sut = UserPasswordChangerService(self._mock_user_repository)

    @pytest.mark.asyncio
    async def test_change_password_successfully(self) -> None:
        old_password = 'secret123456'
        user = UserMother.from_password(UserPasswordMother.create(value=old_password, hashed=False))
        self._mock_user_repository.find.return_value = user
        self._mock_user_repository.save_and_publish.return_value = None

        kwargs = {
            'user_id': user.id(),
            'old_password': old_password,
            'new_password': UserPasswordMother.random(),
        }

        await self._sut(**kwargs)

        self._mock_user_repository.find.assert_called_once_with(kwargs['user_id'])
        self._mock_user_repository.save_and_publish.assert_called_once_with(user)
