from typing import Any, Dict, Optional, Union, final

from aioddd import EventPublisher

from project.libs.shared.infrastructure.mongodb_connection import MongoDBConnection
from project.libs.shared.infrastructure.mongodb_utils import (
    MongoDBBaseMapper,
    MongoDBBaseRepository,
)
from project.libs.user.domain.aggregates import User
from project.libs.user.domain.errors import (
    UserNotDeletedError,
    UserNotFoundError,
    UserNotSavedError,
)
from project.libs.user.domain.properties import (
    UserEmail,
    UserId,
    UserPassword,
    UserRefreshToken,
    UserRefreshTokenExpirationIn,
)
from project.libs.user.domain.repositories import UserRepository


class MongoDBUserMapper(MongoDBBaseMapper):
    def to_aggregate(self, data: Dict[str, Any]) -> User:
        return User(
            UserId(data['id']),
            UserEmail(data['email']),
            UserPassword(data['password'], True),
            None if data['refresh_token'] is None else UserRefreshToken(data['refresh_token']),
            None
            if data['refresh_token_expiration_in'] is None
            else UserRefreshTokenExpirationIn(data['refresh_token_expiration_in']),
        )

    def to_document(self, aggregate: Union[User, Any]) -> Dict[str, Any]:
        refresh_token = None
        refresh_token_expiration_in = None
        if refresh_token_ := aggregate.refresh_token():
            refresh_token = refresh_token_.value()
        if refresh_token_expiration_in_ := aggregate.refresh_token_expiration_in():
            refresh_token_expiration_in = refresh_token_expiration_in_.value()
        return {
            'id': aggregate.id().value(),
            'email': aggregate.email().value(),
            'password': aggregate.password().value(),
            'refresh_token': refresh_token,
            'refresh_token_expiration_in': refresh_token_expiration_in,
        }


@final
class MongoDBUserRepository(UserRepository, MongoDBBaseRepository):
    __slots__ = ('_collection', '_publisher')

    def __init__(self, connection: MongoDBConnection, mapper: MongoDBUserMapper, publisher: EventPublisher) -> None:
        super().__init__(connection, mapper)
        self._collection = 'users'
        self._publisher = publisher

    async def find(self, user_id: UserId) -> User:
        await self._ensure_indexes()
        user: Optional[User] = await self._find_one(self._collection, {'id': user_id.value()})
        if not user:
            raise UserNotFoundError.create(detail={'id': user_id.value()})
        return user

    async def find_all(self) -> list[User]:
        await self._ensure_indexes()
        return await self._find(self._collection)

    async def find_email(self, email: UserEmail) -> User:
        await self._ensure_indexes()
        user: Optional[User] = await self._find_one(self._collection, {'email': email.value()})
        if not user:
            raise UserNotFoundError.create(detail={'email': email.value()})
        return user

    async def find_id_and_email(self, user_id: UserId, email: UserEmail) -> User:
        await self._ensure_indexes()
        user: Optional[User] = await self._find_one(self._collection, {'id': user_id.value(), 'email': email.value()})
        if not user:
            raise UserNotFoundError.create(detail={'id': user_id.value(), 'email': email.value()})
        return user

    async def find_email_and_refresh_token(self, email: UserEmail, refresh_token: UserRefreshToken) -> User:
        await self._ensure_indexes()
        user: Optional[User] = await self._find_one(
            self._collection, {'email': email.value(), 'refresh_token': refresh_token.value()}
        )
        if not user:
            raise UserNotFoundError.create(detail={'email': email.value(), 'refresh_token': refresh_token.value()})
        return user

    async def search(self, user_id: UserId) -> Optional[User]:
        await self._ensure_indexes()
        return await self._find_one(self._collection, {'id': user_id.value()})

    async def save_and_publish(self, user: User) -> None:
        try:
            await self._ensure_indexes()
            await self._connection.collection(self._collection).update_one(
                {'id': user.id().value()},
                {'$set': self._mapper.to_document(user)},
                upsert=True,
            )
        except Exception as err:
            raise UserNotSavedError.create(detail={'id': user.id().value()}).with_exception(err)
        await self._publisher.publish(user.pull_aggregate_events())

    async def delete_and_publish(self, user: User) -> None:
        try:
            await self._ensure_indexes()
            await self._delete_one(self._collection, {'id': user.id().value()})
        except Exception as err:
            raise UserNotDeletedError.create(detail={'id': user.id().value()}).with_exception(err)
        await self._publisher.publish(user.pull_aggregate_events())

    async def _ensure_indexes(self) -> None:
        await self._create_index(self._collection, 'id', unique=True)
        await self._create_index(self._collection, 'email')
