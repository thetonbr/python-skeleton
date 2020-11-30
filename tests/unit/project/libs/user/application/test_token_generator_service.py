from typing import final
from unittest.mock import Mock

import pytest
from aioddd.testing import mock

from project.libs.user.application.token_generator_service import TokenGeneratorService
from project.libs.user.domain.errors import (
    UserNotFoundError,
    UserPasswordNotMatchError,
    UserUnauthorizedError,
)
from project.libs.user.domain.repositories import AuthRepository, TokenFactory
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserPasswordMother,
)


@final
class TestTokenGeneratorService:
    _mock_auth_repository: Mock
    _mock_token_factory: Mock
    _expiration_days: int
    _token_type: str
    _sut: TokenGeneratorService

    def setup(self) -> None:
        self._mock_auth_repository = mock(AuthRepository, ['find'])
        self._mock_token_factory = mock(TokenFactory, ['generate'])
        self._expiration_days = 14
        self._token_type = 'Bearer'
        self._sut = TokenGeneratorService(
            self._mock_auth_repository,
            self._mock_token_factory,
            self._expiration_days,
            self._token_type,
        )

    @pytest.mark.asyncio
    async def test_generate_token_successfully(self) -> None:
        password = 'secret123456'
        user = UserMother.from_password(UserPasswordMother.create(value=password, hashed=False))
        access_token = 'token'
        self._mock_auth_repository.find.return_value = user
        self._mock_token_factory.generate.return_value = access_token

        kwargs = {
            'email': user.email(),
            'password': password,
        }

        res = await self._sut(**kwargs)

        self._mock_auth_repository.find.assert_called_once_with(kwargs['email'])
        self._mock_token_factory.generate.assert_called_once_with(user.id(), self._expiration_days)
        assert res.user_id == user.id().value()
        assert res.access_token == access_token
        assert res.token_type == self._token_type

    @pytest.mark.asyncio
    async def test_generate_token_fails_when_user_not_found(self) -> None:
        self._mock_auth_repository.find.side_effect = UserNotFoundError.create()

        kwargs = {
            'email': UserEmailMother.random(),
            'password': 'secret123456',
        }

        with pytest.raises(UserUnauthorizedError):
            await self._sut(**kwargs)

        self._mock_auth_repository.find.assert_called_once_with(kwargs['email'])
        self._mock_token_factory.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_token_fails_when_user_password_not_match(self) -> None:
        self._mock_auth_repository.find.side_effect = UserPasswordNotMatchError.create()

        kwargs = {
            'email': UserEmailMother.random(),
            'password': 'secret123456',
        }

        with pytest.raises(UserUnauthorizedError):
            await self._sut(**kwargs)

        self._mock_auth_repository.find.assert_called_once_with(kwargs['email'])
        self._mock_token_factory.generate.assert_not_called()
