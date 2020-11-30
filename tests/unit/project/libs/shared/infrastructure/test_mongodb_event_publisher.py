from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, final

from aioddd import Event, EventMapper, Id

from project.libs.shared.infrastructure.mongodb_event_publisher import (
    MongoDBEventPublisherMapper,
)


@final
class TestMongoDBEventPublisherMapper:
    @staticmethod
    def test_to_document_and_to_aggregate() -> None:
        class _Event(Event):
            @dataclass
            class Attributes:
                foo: str

            attributes: Attributes

        class _EventMapper(EventMapper):
            event_type = _Event
            service_name = '_service_name'
            event_name = '_name'

            def decode(self, data: Dict[str, Any]) -> Event:
                return _Event(_Event.Attributes(foo=data['foo']))

            @staticmethod
            def map_attributes(msg: _Event.Attributes) -> Dict[str, Any]:
                return {'foo': msg.foo}

        evt = _Event(_Event.Attributes(foo=Id.generate().value()))

        sut = MongoDBEventPublisherMapper([_EventMapper()])

        doc = sut.to_document(evt)

        assert Id.validate(doc['id'])
        assert doc['name'] == '_service_name._name'
        assert doc['type'] == 'event'
        assert doc['payload'] == {'foo': evt.attributes.foo}
        assert (datetime.utcnow() - doc['occurred_on']).total_seconds() < 1

        agg: _Event = sut.to_aggregate(doc)

        assert agg.attributes.foo == evt.attributes.foo
