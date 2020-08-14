from abc import ABC, abstractmethod
from typing import Dict, List, Union, Optional, Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from aioddd import Aggregate


class MongoDBBaseMapper(ABC):
    @abstractmethod
    def to_aggregate(self, data: Dict[str, Any]) -> Union[Aggregate, Any]:
        pass

    def to_aggregates(self, data: List[Dict[str, Any]]) -> List[Union[Aggregate, Any]]:
        return [self.to_aggregate(item) for item in data]

    @abstractmethod
    def to_document(self, aggregate: Union[Aggregate, Any]) -> Dict[str, Any]:
        pass

    def to_documents(self, aggregates: List[Union[Aggregate, Any]]) -> List[Dict[str, Any]]:
        return [self.to_document(item) for item in aggregates]


class MongoDBBaseRepository(ABC):
    __slots__ = ('_database', '_mapper')

    def __init__(self, database: Union[AsyncIOMotorDatabase, Database], mapper: MongoDBBaseMapper) -> None:
        self._database = database
        self._mapper = mapper

    async def _find_one(self, collection: str, criteria: Dict[str, Any]) -> Optional[Union[Aggregate, Any]]:
        document = await self._database[collection].find_one(filter=criteria)
        if not document:
            return document
        return self._mapper.to_aggregate(document)

    async def _find(self, collection: str, criteria: Dict[str, Any]) -> List[Union[Aggregate, Any]]:
        return [
            self._mapper.to_aggregate(document)
            async for document in self._database[collection].find(filter=criteria)
        ]

    async def _insert_one(self, collection: str, aggregate: Union[Aggregate, Any]) -> InsertOneResult:
        return await self._database[collection].insert_one(self._mapper.to_document(aggregate))

    async def _update_one(
            self,
            collection: str,
            criteria: Dict[str, Any],
            aggregate: Union[Aggregate, Any]
    ) -> UpdateResult:
        return await self._database[collection].update_one(criteria, {'$set': self._mapper.to_document(aggregate)})

    async def _delete_one(self, collection: str, criteria: Dict[str, Any]) -> DeleteResult:
        return await self._database[collection].delete_one(criteria)
