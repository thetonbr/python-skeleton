from typing import Optional, Type, final

from aioddd import Query, QueryHandler, Response
from pydantic import BaseModel

from project.libs.user.application.finder_service import (
    UserFinderService,
    UserFullFinderService,
)
from project.libs.user.domain.properties import UserId


@final
class FindUserQuery(Query, BaseModel):
    user_id: str


@final
class FindUserQueryHandler(QueryHandler):
    __slots__ = '_service'

    def __init__(self, service: UserFinderService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Query]:
        return FindUserQuery

    async def handle(self, query: FindUserQuery) -> Optional[Response]:
        return await self._service(UserId(query.user_id))


@final
class FindFullUserQuery(Query, BaseModel):
    user_id: str


@final
class FindFullUserQueryHandler(QueryHandler):
    __slots__ = '_service'

    def __init__(self, service: UserFullFinderService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Query]:
        return FindFullUserQuery

    async def handle(self, query: FindFullUserQuery) -> Optional[Response]:
        return await self._service(UserId(query.user_id))
