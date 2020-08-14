from typing import final, Type, Optional, Dict, Any

from aioddd import Query, QueryHandler, Response

from src.libs.account.user.domain.repositories import TokenFactory


@final
class ReadUserAuthQuery(Query):
    __slots__ = '_token'

    def __init__(self, token: str) -> None:
        self._token = token

    def token(self) -> str:
        return self._token


class ReadUserAuthQueryResponse(Response):
    jwt: Dict[str, Any]
    user_id: str


@final
class ReadUserAuthQueryHandler(QueryHandler):
    __slots__ = '_service'

    def __init__(self, service: TokenFactory) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Query]:
        return ReadUserAuthQuery

    async def handle(self, query: ReadUserAuthQuery) -> Optional[Response]:
        return ReadUserAuthQueryResponse(
            jwt=await self._service.decode(query.token()),
            user_id=(await self._service.read(query.token())).value()
        )
