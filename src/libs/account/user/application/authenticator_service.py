from typing import TypedDict, final

from src.libs.account.user.domain.errors import UserUnauthorizedError
from src.libs.account.user.domain.repositories import TokenFactory


class AuthenticatorResponse(TypedDict):
    user_id: str


@final
class AuthenticatorService:
    __slots__ = '_factory'

    def __init__(self, factory: TokenFactory) -> None:
        self._factory = factory

    async def __call__(self, token: str) -> AuthenticatorResponse:
        try:
            user_id = await self._factory.read(token)
            return AuthenticatorResponse(user_id=user_id.value())
        except Exception as err:
            raise UserUnauthorizedError.create(detail={'token': token}).with_exception(err)
