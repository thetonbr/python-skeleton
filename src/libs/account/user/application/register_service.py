from typing import final

from src.libs.account.user.domain.aggregates import User
from src.libs.account.user.domain.errors import UserAlreadyExistError
from src.libs.account.user.domain.properties import UserEmail, UserPassword
from src.libs.account.user.domain.repositories import UserRepository
from src.libs.shared.domain.user.properties import UserId


@final
class UserRegisterService:
    __slots__ = '_repository'

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def __call__(self, user_id: UserId, email: UserEmail, password: UserPassword) -> None:
        if await self._repository.search(user_id):
            raise UserAlreadyExistError.create(detail={'id': user_id.value()})
        user = User.register(user_id, email, password)
        await self._repository.save_and_publish(user)
