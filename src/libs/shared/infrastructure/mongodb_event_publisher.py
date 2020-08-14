from datetime import datetime
from typing import List, final, Union, Dict, Any

from aioddd import EventPublisher, Event, EventMapper, find_event_mapper_by_type, find_event_mapper_by_name
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.database import Database

from src.libs.shared.infrastructure.mongodb_utils import MongoDBBaseRepository, MongoDBBaseMapper


@final
class MongoDBEventPublisherMapper(MongoDBBaseMapper):
    __slots__ = '_mappers'

    def __init__(self, mappers: List[EventMapper]):
        self._mappers = mappers

    def to_aggregate(self, data: Dict[str, Any]) -> Event:
        return find_event_mapper_by_name(data['name'], self._mappers).decode(data['payload'])

    def to_document(self, aggregate: Union[Event, Any]) -> Dict[str, Any]:
        mapper = find_event_mapper_by_type(aggregate, self._mappers)
        meta = aggregate.get_meta()
        return {
            'id': meta['id'],
            'name': f'{mapper.service_name()}.{mapper.name()}',
            'type': meta['type'],
            'payload': mapper.encode(aggregate)['attributes'],
            'occurredOn': datetime.utcfromtimestamp(meta['occurredOn']),
        }


@final
class MongoDBEventPublisher(EventPublisher, MongoDBBaseRepository):
    __slots__ = '_collection'

    def __init__(
            self,
            database: Union[AsyncIOMotorDatabase, Database],
            mapper: MongoDBEventPublisherMapper
    ) -> None:
        super().__init__(database, mapper)
        self._collection = 'domain_events'

    async def publish(self, events: List[Event]) -> None:
        _ = [await self._publish(event) for event in events]

    async def _publish(self, event: Event) -> None:
        await self._insert_one(self._collection, event)
