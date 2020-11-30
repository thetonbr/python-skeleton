from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from aioddd import Aggregate

# noinspection PyProtectedMember
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

from project.libs.shared.infrastructure.mongodb_connection import MongoDBConnection


class MongoDBBaseMapper(ABC):
    @abstractmethod
    def to_aggregate(self, data: Dict[str, Any]) -> Union[Aggregate, Any]:
        pass  # pragma: no cover

    def to_aggregates(self, data: List[Dict[str, Any]]) -> List[Union[Aggregate, Any]]:
        return [self.to_aggregate(item) for item in data]

    @abstractmethod
    def to_document(self, aggregate: Union[Aggregate, Any]) -> Dict[str, Any]:
        pass  # pragma: no cover

    def to_documents(self, aggregates: List[Union[Aggregate, Any]]) -> List[Dict[str, Any]]:
        return [self.to_document(item) for item in aggregates]


class MongoDBBaseRepository(ABC):
    __slots__ = ('_connection', '_mapper')

    def __init__(self, connection: MongoDBConnection, mapper: MongoDBBaseMapper) -> None:
        self._connection = connection
        self._mapper = mapper

    async def _create_index(self, collection: str, keys: Union[str, List[Tuple[str, str]]], **kwargs: Any) -> None:
        await self._connection.collection(collection).create_index(keys, **kwargs)

    async def _find_one(self, collection: str, criteria: Dict[str, Any]) -> Optional[Union[Aggregate, Any]]:
        document = await self._connection.collection(collection).find_one(
            filter=criteria,
        )
        if not document:
            return document
        return self._mapper.to_aggregate(document)

    async def _find(
        self,
        collection: str,
        criteria: Dict[str, Any],
        limit: int = 0,
        **kwargs: Any,
    ) -> List[Union[Aggregate, Any]]:
        return [
            self._mapper.to_aggregate(document)
            async for document in self._connection.collection(collection).find(
                filter=criteria,
                limit=limit,
                **kwargs,
            )
        ]

    async def _insert_one(self, collection: str, aggregate: Union[Aggregate, Any]) -> InsertOneResult:
        return await self._connection.collection(collection).insert_one(
            self._mapper.to_document(aggregate),
        )

    async def _update_one(
        self, collection: str, criteria: Dict[str, Any], aggregate: Union[Aggregate, Any]
    ) -> UpdateResult:
        return await self._connection.collection(collection).update_one(
            criteria,
            {
                '$set': self._mapper.to_document(aggregate),
            },
        )

    async def _delete_one(self, collection: str, criteria: Dict[str, Any]) -> DeleteResult:
        return await self._connection.collection(collection).delete_one(
            criteria,
        )

    async def _delete_collection(self, collection: str) -> None:
        return await self._connection.database().drop_collection(name_or_collection=collection)
