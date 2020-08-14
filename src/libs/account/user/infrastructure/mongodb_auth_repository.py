from typing import final, Dict, Union, Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.database import Database

from src.libs.account.user.domain.aggregates import User
from src.libs.account.user.domain.errors import UserNotFoundError
from src.libs.account.user.domain.properties import UserEmail, UserPassword
from src.libs.account.user.domain.repositories import AuthRepository
from src.libs.shared.domain.user.properties import UserId
from src.libs.shared.infrastructure.mongodb_utils import MongoDBBaseRepository, MongoDBBaseMapper


@final
class MongoDBAuthMapper(MongoDBBaseMapper):
    def to_aggregate(self, data: Dict[str, Any]) -> User:
        return User(
            UserId(data['id']),
            UserEmail(data['email']),
            UserPassword(data['password'], True)
        )

    def to_document(self, aggregate: Union[User, Any]) -> Dict[str, Any]:
        return {
            'id': aggregate.id().value(),
            'email': aggregate.email().value(),
            'password': aggregate.password().value(),
        }


@final
class MongoDBAuthRepository(AuthRepository, MongoDBBaseRepository):
    __slots__ = '_collection'

    def __init__(
            self,
            database: Union[AsyncIOMotorDatabase, Database],
            mapper: MongoDBAuthMapper,
    ) -> None:
        super().__init__(database, mapper)
        self._collection = 'users'

    async def find(self, email: UserEmail) -> User:
        user: Optional[User] = await self._find_one(self._collection, {'email': email.value()})
        if not user:
            raise UserNotFoundError.create(detail={'email': email.value()})
        return user
