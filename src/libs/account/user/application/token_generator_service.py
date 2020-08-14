from typing import TypedDict, final

from src.libs.account.user.domain.errors import UserPasswordNotMatchError, UserNotFoundError, UserUnauthorizedError
from src.libs.account.user.domain.properties import UserEmail
from src.libs.account.user.domain.repositories import AuthRepository, TokenFactory


class TokenGeneratorResponse(TypedDict):
    user_id: str
    token: str


@final
class TokenGeneratorService:
    __slots__ = ('_repository', '_factory', '_expiration_days')

    def __init__(self, repository: AuthRepository, factory: TokenFactory, expiration_days: int) -> None:
        self._repository = repository
        self._factory = factory
        self._expiration_days = expiration_days

    async def __call__(self, email: UserEmail, password: str) -> TokenGeneratorResponse:
        try:
            user = await self._repository.find(email)
            user.validate_password(password)
        except (UserNotFoundError, UserPasswordNotMatchError) as err:
            raise UserUnauthorizedError.create(detail={'email': email.value()}).with_exception(err)
        token = await self._factory.generate(user.id(), self._expiration_days)
        return TokenGeneratorResponse(user_id=user.id().value(), token=token)
