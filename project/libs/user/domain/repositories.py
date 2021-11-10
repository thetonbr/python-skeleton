from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from project.libs.user.domain.aggregates import User
from project.libs.user.domain.properties import UserEmail, UserId, UserRefreshToken


class UserRepository(ABC):
    @abstractmethod
    async def find(self, user_id: UserId) -> User:
        pass  # pragma: no cover

    @abstractmethod
    async def find_all(self) -> list[User]:
        pass  # pragma: no cover

    @abstractmethod
    async def find_id_and_email(self, user_id: UserId, email: UserEmail) -> User:
        pass  # pragma: no cover

    @abstractmethod
    async def find_email(self, email: UserEmail) -> User:
        pass  # pragma: no cover

    @abstractmethod
    async def find_email_and_refresh_token(self, email: UserEmail, refresh_token: UserRefreshToken) -> User:
        pass  # pragma: no cover

    @abstractmethod
    async def search(self, user_id: UserId) -> Optional[User]:
        pass  # pragma: no cover

    @abstractmethod
    async def save_and_publish(self, user: User) -> None:
        pass  # pragma: no cover

    @abstractmethod
    async def delete_and_publish(self, user: User) -> None:
        pass  # pragma: no cover


class AuthRepository(ABC):
    @abstractmethod
    async def find(self, email: UserEmail) -> User:
        pass  # pragma: no cover


class TokenFactory(ABC):
    @abstractmethod
    async def generate(self, user_id: UserId, expiration_in_days: int) -> str:
        pass  # pragma: no cover

    @abstractmethod
    async def decode(self, token: str) -> Dict[str, Any]:
        pass  # pragma: no cover

    @abstractmethod
    async def read(self, token: str) -> UserId:
        pass  # pragma: no cover


class UserNotifier(ABC):
    @abstractmethod
    async def notify_user_registered(self, user_id: UserId, email: UserEmail) -> None:
        pass  # pragma: no cover

    @abstractmethod
    async def notify_user_password_forgotten(
        self, user_id: UserId, email: UserEmail, refresh_token: UserRefreshToken
    ) -> None:
        pass  # pragma: no cover

    @abstractmethod
    async def notify_user_password_resetted(self, user_id: UserId, email: UserEmail) -> None:
        pass  # pragma: no cover
