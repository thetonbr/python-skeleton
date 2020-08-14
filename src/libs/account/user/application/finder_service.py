from typing import final

from aioddd import Response

from src.libs.account.user.domain.repositories import UserRepository
from src.libs.shared.domain.user.properties import UserId


class UserFinderResponse(Response):
    id: str
    email: str


@final
class UserFinderService:
    __slots__ = '_repository'

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def __call__(self, user_id: UserId) -> UserFinderResponse:
        user = await self._repository.find(user_id)
        return UserFinderResponse(id=user.id().value(), email=user.email().value())
