from typing import final

from src.libs.account.user.domain.properties import UserPassword
from src.libs.account.user.domain.repositories import UserRepository
from src.libs.shared.domain.user.properties import UserId


@final
class UserPasswordChangerService:
    __slots__ = '_repository'

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def __call__(self, user_id: UserId, old_password: str, new_password: UserPassword) -> None:
        user = await self._repository.find(user_id)
        user.change_password(old_password, new_password)
        await self._repository.save_and_publish(user)
