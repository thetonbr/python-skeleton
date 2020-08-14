from typing import final, Type, Optional

from aioddd import Query, QueryHandler, Response

from src.libs.account.user.application.token_generator_service import TokenGeneratorService
from src.libs.account.user.domain.properties import UserEmail


@final
class GenerateTokenQuery(Query):
    __slots__ = ('_email', '_password')

    def __init__(self, email: str, password: str) -> None:
        self._email = email
        self._password = password

    def email(self) -> str:
        return self._email

    def password(self) -> str:
        return self._password


@final
class GenerateTokenQueryHandler(QueryHandler):
    __slots__ = '_service'

    def __init__(self, service: TokenGeneratorService) -> None:
        self._service = service

    def subscribed_to(self) -> Type[Query]:
        return GenerateTokenQuery

    async def handle(self, query: GenerateTokenQuery) -> Optional[Response]:
        return await self._service(UserEmail(query.email()), query.password())
