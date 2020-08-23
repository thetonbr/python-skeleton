from typing import List, final

from aioddd import EventMapper


@final
class ConfigEventMappers:
    _mappers: List[EventMapper]

    def __init__(self, mappers: List[EventMapper]) -> None:
        self._mappers = mappers

    def add(self, mappers: List[EventMapper]) -> None:
        for mapper in mappers:
            self._mappers.append(mapper)

    def all(self) -> List[EventMapper]:
        return self._mappers
