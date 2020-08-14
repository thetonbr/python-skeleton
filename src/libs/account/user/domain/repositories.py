from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from src.libs.account.user.domain.aggregates import User
from src.libs.account.user.domain.properties import UserEmail
from src.libs.shared.domain.user.properties import UserId


class UserRepository(ABC):
    @abstractmethod
    async def find(self, user_id: UserId) -> User:
        pass

    @abstractmethod
    async def search(self, user_id: UserId) -> Optional[User]:
        pass

    @abstractmethod
    async def save_and_publish(self, user: User) -> None:
        pass

    @abstractmethod
    async def delete_and_publish(self, user: User) -> None:
        pass


class AuthRepository(ABC):
    @abstractmethod
    async def find(self, email: UserEmail) -> User:
        pass


class TokenFactory(ABC):
    @abstractmethod
    async def generate(self, user_id: UserId, expiration_in_days: int) -> str:
        pass

    @abstractmethod
    async def decode(self, token: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def read(self, token: str) -> UserId:
        pass
