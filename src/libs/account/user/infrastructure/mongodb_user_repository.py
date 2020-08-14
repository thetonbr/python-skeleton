from typing import final, Dict, Union, Any, Optional

from aioddd import EventPublisher
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.database import Database

from src.libs.account.user.domain.aggregates import User
from src.libs.account.user.domain.errors import UserNotFoundError, UserNotCreatedError, UserNotUpdatedError, \
    UserNotDeletedError
from src.libs.account.user.domain.properties import UserEmail, UserPassword
from src.libs.account.user.domain.repositories import UserRepository
from src.libs.shared.domain.user.properties import UserId
from src.libs.shared.infrastructure.mongodb_utils import MongoDBBaseRepository, MongoDBBaseMapper


@final
class MongoDBUserMapper(MongoDBBaseMapper):
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
class MongoDBUserRepository(UserRepository, MongoDBBaseRepository):
    __slots__ = ('_collection', '_publisher')

    def __init__(
            self,
            database: Union[AsyncIOMotorDatabase, Database],
            mapper: MongoDBUserMapper,
            publisher: EventPublisher
    ) -> None:
        super().__init__(database, mapper)
        self._collection = 'users'
        self._publisher = publisher

    async def find(self, user_id: UserId) -> User:
        user: Optional[User] = await self._find_one(self._collection, {'id': user_id.value()})
        if not user:
            raise UserNotFoundError.create(detail={'id': user_id.value()})
        return user

    async def search(self, user_id: UserId) -> Optional[User]:
        return await self._find_one(self._collection, {'id': user_id.value()})

    async def save_and_publish(self, user: User) -> None:
        if not await self.search(user.id()):
            try:
                await self._insert_one(self._collection, user)
            except Exception as err:
                raise UserNotCreatedError.create(detail={'id': user.id().value()}).with_exception(err)
        else:
            try:
                await self._update_one(self._collection, {'id': user.id().value()}, user)
            except Exception as err:
                raise UserNotUpdatedError.create(detail={'id': user.id().value()}).with_exception(err)
        await self._publisher.publish(user.pull_aggregate_events())

    async def delete_and_publish(self, user: User) -> None:
        try:
            await self._delete_one(self._collection, {'id': user.id().value()})
        except Exception as err:
            raise UserNotDeletedError.create(detail={'id': user.id().value()}).with_exception(err)
        await self._publisher.publish(user.pull_aggregate_events())
