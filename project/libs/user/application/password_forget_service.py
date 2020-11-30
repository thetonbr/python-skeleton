from typing import final

from project.libs.user.domain.properties import UserEmail
from project.libs.user.domain.repositories import UserNotifier, UserRepository


@final
class UserPasswordForgetService:
    __slots__ = ('_user_repository', '_user_notifier')

    def __init__(self, user_repository: UserRepository, user_notifier: UserNotifier) -> None:
        self._user_repository = user_repository
        self._user_notifier = user_notifier

    async def __call__(self, user_email: UserEmail) -> None:
        user = await self._user_repository.find_email(user_email)
        user.forget_password()
        await self._user_repository.save_and_publish(user)
        await self._user_notifier.notify_user_password_forgotten(
            user.id(), user_email, user.refresh_token()  # type: ignore
        )
