from typing import final

from project.libs.user.domain.properties import UserEmail, UserId
from project.libs.user.domain.repositories import UserNotifier, UserRepository


@final
class UserRegisteredNotifierService:
    __slots__ = ('_user_repository', '_user_notifier')

    def __init__(self, user_repository: UserRepository, user_notifier: UserNotifier) -> None:
        self._user_repository = user_repository
        self._user_notifier = user_notifier

    async def __call__(self, user_id: UserId, email: UserEmail) -> None:
        user = await self._user_repository.find_id_and_email(user_id, email)
        user.user_registered_notified()
        await self._user_notifier.notify_user_registered(user_id, email)
        await self._user_repository.save_and_publish(user)
