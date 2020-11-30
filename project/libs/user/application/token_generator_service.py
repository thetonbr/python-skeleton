from typing import final

from pydantic import BaseModel

from project.libs.user.domain.errors import (
    UserNotFoundError,
    UserPasswordNotMatchError,
    UserUnauthorizedError,
)
from project.libs.user.domain.properties import UserEmail
from project.libs.user.domain.repositories import AuthRepository, TokenFactory


class TokenGeneratorResponse(BaseModel):
    user_id: str
    token_type: str
    access_token: str


@final
class TokenGeneratorService:
    __slots__ = ('_repository', '_factory', '_expiration_days', '_token_type')

    def __init__(
        self,
        repository: AuthRepository,
        factory: TokenFactory,
        expiration_days: int,
        token_type: str,
    ) -> None:
        self._repository = repository
        self._factory = factory
        self._expiration_days = expiration_days
        self._token_type = token_type

    async def __call__(self, email: UserEmail, password: str) -> TokenGeneratorResponse:
        try:
            user = await self._repository.find(email)
            user.validate_password(password)
        except (UserNotFoundError, UserPasswordNotMatchError) as err:
            raise UserUnauthorizedError.create(detail={'email': email.value()}).with_exception(err)
        token = await self._factory.generate(user.id(), self._expiration_days)
        return TokenGeneratorResponse(user_id=user.id().value(), access_token=token, token_type=self._token_type)
