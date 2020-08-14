from typing import List, final

from aioddd import EventMapper


@final
class ConfigEventMappers:
    __slots__ = '_mappers'

    def __init__(self, mappers: List[EventMapper]) -> None:
        self._mappers = mappers

    def all(self) -> List[EventMapper]:
        return self._mappers
