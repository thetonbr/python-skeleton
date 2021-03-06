from typing import Optional, final

from pydantic import BaseModel

from project.libs.user.domain.aggregates import User
from project.libs.user.domain.properties import UserId
from project.libs.user.domain.repositories import UserRepository


class UserFinderResponse(BaseModel):
    id: str
    email: str

    @classmethod
    def create(cls, user: User) -> 'UserFinderResponse':
        return cls(id=user.id().value(), email=user.email().value())


@final
class UserFinderService:
    __slots__ = '_repository'

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def __call__(self, user_id: UserId) -> UserFinderResponse:
        return UserFinderResponse.create(user=await self._repository.find(user_id))


class UserFullFinderResponse(BaseModel):
    id: str
    email: str
    refresh_token: Optional[str]
    refresh_token_expiration_in: Optional[int]


@final
class UserFullFinderService:
    __slots__ = '_repository'

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def __call__(self, user_id: UserId) -> UserFullFinderResponse:
        user = await self._repository.find(user_id)
        refresh_token = None
        refresh_token_expiration_in = None
        if refresh_token_ := user.refresh_token():
            refresh_token = refresh_token_.value()
        if refresh_token_expiration_in_ := user.refresh_token_expiration_in():
            refresh_token_expiration_in = refresh_token_expiration_in_.value()
        return UserFullFinderResponse(
            id=user.id().value(),
            email=user.email().value(),
            refresh_token=refresh_token,
            refresh_token_expiration_in=refresh_token_expiration_in,
        )


@final
class UsersFinderService:
    __slots__ = '_repository'

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def __call__(self) -> list[UserFinderResponse]:
        return list(map(UserFinderResponse.create, await self._repository.find_all()))
