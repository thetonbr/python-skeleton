from typing import final
from unittest.mock import Mock

import pytest
from aioddd.testing import mock

from project.libs.user.application.register_service import UserRegisterService
from project.libs.user.domain.errors import UserAlreadyExistError
from project.libs.user.domain.repositories import UserRepository
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
    UserPasswordMother,
)


@final
class TestUserRegisterService:
    _mock_user_repository: Mock
    _sut: UserRegisterService

    def setup(self) -> None:
        self._mock_user_repository = mock(UserRepository, ['search', 'save_and_publish'])
        self._sut = UserRegisterService(self._mock_user_repository)

    @pytest.mark.asyncio
    async def test_register_successfully(self) -> None:
        self._mock_user_repository.search.return_value = None
        self._mock_user_repository.save_and_publish.return_value = None

        kwargs = {
            'user_id': UserIdMother.random(),
            'email': UserEmailMother.random(),
            'password': UserPasswordMother.random(),
        }

        await self._sut(**kwargs)

        self._mock_user_repository.search.assert_called_once_with(kwargs['user_id'])
        self._mock_user_repository.save_and_publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_fails_when_user_already_exists(self) -> None:
        user = UserMother.random()
        self._mock_user_repository.search.return_value = user

        kwargs = {
            'user_id': user.id(),
            'email': user.email(),
            'password': user.password(),
        }

        with pytest.raises(UserAlreadyExistError):
            await self._sut(**kwargs)

        self._mock_user_repository.search.assert_called_once_with(kwargs['user_id'])
        self._mock_user_repository.save_and_publish.assert_not_called()
