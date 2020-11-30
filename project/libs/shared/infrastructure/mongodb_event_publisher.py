from datetime import datetime
from typing import Any, Dict, List, Union, final

from aioddd import (
    Event,
    EventMapper,
    EventPublisher,
    find_event_mapper_by_name,
    find_event_mapper_by_type,
)

from project.libs.shared.infrastructure.mongodb_connection import MongoDBConnection
from project.libs.shared.infrastructure.mongodb_utils import (
    MongoDBBaseMapper,
    MongoDBBaseRepository,
)


@final
class MongoDBEventPublisherMapper(MongoDBBaseMapper):
    __slots__ = '_mappers'

    def __init__(self, mappers: List[EventMapper]) -> None:
        self._mappers = mappers

    def to_aggregate(self, data: Dict[str, Any]) -> Event:
        return find_event_mapper_by_name(data['name'], self._mappers).decode(data['payload'])

    def to_document(self, evt: Union[Event, Any]) -> Dict[str, Any]:
        mapper = find_event_mapper_by_type(evt, self._mappers)
        data = mapper.encode(evt)
        return {
            'id': data['id'],
            'name': data['meta']['message'],
            'type': data['type'],
            'payload': data['attributes'],
            'occurred_on': datetime.utcfromtimestamp(data['occurred_on']),
        }


@final
class MongoDBEventPublisher(EventPublisher, MongoDBBaseRepository):
    __slots__ = '_collection'

    def __init__(self, connection: MongoDBConnection, mapper: MongoDBEventPublisherMapper) -> None:
        super().__init__(connection, mapper)
        self._collection = 'domain_events'

    async def publish(self, events: List[Event]) -> None:
        _ = [await self._publish(event) for event in events]

    async def _publish(self, event: Event) -> None:
        await self._insert_one(self._collection, event)
