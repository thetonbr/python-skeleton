from typing import final, Type, Optional

from aioddd import Query, QueryHandler, Response

from src.libs.account.user.application.finder_service import UserFinderService
from src.libs.shared.domain.user.properties import UserId


@final
class FindUserQuery(Query):
    __slots__ = '_user_id'

    def __init__(self, user_id: str) -> None:
        self._user_id = user_id

    def user_id(self) -> str:
        return self._user_id


@final
class FindUserQueryHandler(QueryHandler):
    __slots__ = '_service'

    def __init__(self, service: UserFinderService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Query]:
        return FindUserQuery

    async def handle(self, command: FindUserQuery) -> Optional[Response]:
        return await self._service(UserId(command.user_id()))
