from typing import final, Dict, Any

from aioddd import EventMapper, Event


@final
class InternalUserDeletedEvent(Event):
    def __init__(self, user_id: str) -> None:
        super().__init__({'id': user_id})

    def id(self) -> str:
        return self._attributes['id']


@final
class InternalUserDeletedEventMapper(EventMapper):
    def belongs_to(self, msg: Event) -> bool:
        return isinstance(msg, InternalUserDeletedEvent)

    def service_name(self) -> str:
        return 'example.account'

    def name(self) -> str:
        return 'user.deleted'

    def decode(self, data: Dict[str, Any]) -> Event:
        return InternalUserDeletedEvent(data['id'])

    @staticmethod
    def map_attributes(msg: InternalUserDeletedEvent) -> Dict[str, Any]:
        return {'id': msg.id()}
