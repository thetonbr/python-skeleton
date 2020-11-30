from typing import Optional, Type, final

from aioddd import Query, QueryHandler, Response
from pydantic import BaseModel

from project.libs.user.application.token_generator_service import TokenGeneratorService
from project.libs.user.domain.properties import UserEmail


@final
class GenerateTokenQuery(Query, BaseModel):
    email: str
    password: str


@final
class GenerateTokenQueryHandler(QueryHandler):
    __slots__ = '_service'

    def __init__(self, service: TokenGeneratorService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Query]:
        return GenerateTokenQuery

    async def handle(self, query: GenerateTokenQuery) -> Optional[Response]:
        return await self._service(UserEmail(query.email), query.password)
