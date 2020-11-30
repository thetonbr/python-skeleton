from typing import final
from unittest.mock import Mock

import pytest
from aioddd.testing import mock

from project.libs.user.application.finder_service import (
    UserFinderService,
    UserFullFinderService,
)
from project.libs.user.domain.repositories import UserRepository
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother


@final
class TestUserFinderService:
    _mock_user_repository: Mock
    _sut: UserFinderService

    def setup(self) -> None:
        self._mock_user_repository = mock(UserRepository, ['find'])
        self._sut = UserFinderService(self._mock_user_repository)

    @pytest.mark.asyncio
    async def test_find_successfully(self) -> None:
        user = UserMother.random()
        self._mock_user_repository.find.return_value = user

        kwargs = {'user_id': user.id()}

        res = await self._sut(**kwargs)

        self._mock_user_repository.find.assert_called_once_with(kwargs['user_id'])
        assert res.id == user.id().value()
        assert res.email == user.email().value()


@final
class TestUserFullFinderService:
    _mock_user_repository: Mock
    _sut: UserFullFinderService

    def setup(self) -> None:
        self._mock_user_repository = mock(UserRepository, ['find'])
        self._sut = UserFullFinderService(self._mock_user_repository)

    @pytest.mark.asyncio
    async def test_find_successfully(self) -> None:
        user = UserMother.random_with_forgotten_password()
        self._mock_user_repository.find.return_value = user

        kwargs = {'user_id': user.id()}

        res = await self._sut(**kwargs)

        self._mock_user_repository.find.assert_called_once_with(kwargs['user_id'])
        assert res.id == user.id().value()
        assert res.email == user.email().value()
        assert res.refresh_token == user.refresh_token().value()
        assert res.refresh_token_expiration_in == user.refresh_token_expiration_in().value()
