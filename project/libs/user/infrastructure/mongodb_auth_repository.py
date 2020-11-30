from typing import Optional, final

from project.libs.shared.infrastructure.mongodb_connection import MongoDBConnection
from project.libs.shared.infrastructure.mongodb_utils import MongoDBBaseRepository
from project.libs.user.domain.aggregates import User
from project.libs.user.domain.errors import UserNotFoundError
from project.libs.user.domain.properties import UserEmail
from project.libs.user.domain.repositories import AuthRepository
from project.libs.user.infrastructure.mongodb_user_repository import MongoDBUserMapper


@final
class MongoDBAuthMapper(MongoDBUserMapper):
    pass


@final
class MongoDBAuthRepository(AuthRepository, MongoDBBaseRepository):
    __slots__ = '_collection'

    def __init__(self, connection: MongoDBConnection, mapper: MongoDBAuthMapper) -> None:
        super().__init__(connection, mapper)
        self._collection = 'users'

    async def find(self, email: UserEmail) -> User:
        user: Optional[User] = await self._find_one(self._collection, {'email': email.value()})
        if not user:
            raise UserNotFoundError.create(detail={'email': email.value()})  # pragma: no cover
        return user
