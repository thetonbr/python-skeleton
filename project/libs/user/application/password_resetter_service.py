from typing import final

from project.libs.user.domain.properties import (
    UserEmail,
    UserPassword,
    UserRefreshToken,
)
from project.libs.user.domain.repositories import UserNotifier, UserRepository


@final
class UserPasswordResetterService:
    __slots__ = ('_user_repository', '_user_notifier')

    def __init__(self, user_repository: UserRepository, user_notifier: UserNotifier) -> None:
        self._user_repository = user_repository
        self._user_notifier = user_notifier

    async def __call__(
        self, user_email: UserEmail, user_refresh_token: UserRefreshToken, new_password: UserPassword
    ) -> None:
        user = await self._user_repository.find_email_and_refresh_token(user_email, user_refresh_token)
        user.reset_password(new_password)
        await self._user_repository.save_and_publish(user)
        await self._user_notifier.notify_user_password_resetted(user.id(), user_email)
