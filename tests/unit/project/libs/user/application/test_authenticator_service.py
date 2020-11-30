from typing import final
from unittest.mock import Mock

import pytest
from aioddd.testing import mock

from project.libs.user.application.authenticator_service import AuthenticatorService
from project.libs.user.domain.errors import UserUnauthorizedError
from project.libs.user.domain.repositories import TokenFactory
from tests.unit.project.libs.user.domain.properties_mothers import UserIdMother


@final
class TestAuthenticatorService:
    _mock_token_factory: Mock
    _sut: AuthenticatorService

    def setup(self) -> None:
        self._mock_token_factory = mock(TokenFactory, ['read'])
        self._sut = AuthenticatorService(self._mock_token_factory)

    @pytest.mark.asyncio
    async def test_authenticate_successfully(self) -> None:
        user_id = UserIdMother.random()
        self._mock_token_factory.read.return_value = user_id

        kwargs = {
            'token': 'token',
        }

        res = await self._sut(**kwargs)

        self._mock_token_factory.read.assert_called_once_with(kwargs['token'])
        assert res.user_id == user_id.value()

    @pytest.mark.asyncio
    async def test_authenticate_fails_because_is_unauthorized(self) -> None:
        self._mock_token_factory.read.side_effect = Exception()

        kwargs = {
            'token': 'token',
        }

        with pytest.raises(UserUnauthorizedError):
            await self._sut(**kwargs)

        self._mock_token_factory.read.assert_called_once_with(kwargs['token'])
