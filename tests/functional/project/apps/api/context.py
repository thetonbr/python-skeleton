from os import getenv
from types import TracebackType
from typing import Any, Callable, Optional, Type, final

from aioddd.testing import sanitize_objects
from httpx import AsyncClient, Response
from orjson import dumps, loads

from project.apps.api.main import app
from project.apps.settings import container, env
from project.libs.shared.infrastructure.mongodb_connection import MongoDBConnection


@final
class APIContext:
    client: Optional[AsyncClient] = None
    base_url: str = 'http://functional-tests'
    token: str = ''
    response: Optional[Response] = None

    async def __aenter__(self) -> 'APIContext':
        self.base_url = f'http://{id(self)}'
        self.client = AsyncClient(app=app, base_url=self.base_url)
        if getenv('DROP_MONGODB_DATABASE', '') == 'BEFORE':
            await self._drop_mongodb_database()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.response = None
        if getenv('DROP_MONGODB_DATABASE', '') == 'AFTER':
            await self._drop_mongodb_database()
        await self.client.aclose()
        self.client = None

    @staticmethod
    async def _drop_mongodb_database() -> None:
        container().get(MongoDBConnection).client().drop_database(env(key='mongodb_database', typ=str))

    async def i_send_x_www_form_urlencoded_request(self, method: str, url: str, data: Optional[Any] = None) -> None:
        self.response = await self.client.request(
            method=method,
            url=url,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'Authorization': self.token,
            },
            data=data,
        )

    async def i_send_json_request(
        self,
        method: str,
        url: str,
        data: Optional[Any] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> None:
        self.response = await self.client.request(
            method=method,
            url=url,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': self.token},
            data=dumps(data).decode('utf-8') if isinstance(data, dict) else data,
            params=params,
        )

    async def the_response_status_code_should_be(self, status_code: int) -> None:
        assert (
            self.response.status_code == status_code
        ), f'"Actual: {self.response.status_code}, Expected: {status_code}, Reason: {self.response.text}'

    async def the_response_content_should_be(self, data: Optional[Any] = None) -> None:
        actual = self.response.json()
        expected = loads(data) if isinstance(data, str) else data
        assert actual == expected, f'"Actual: {actual}, Expected: {expected}'

    async def the_response_content_should_be_contains(self, data: Optional[Any] = None) -> None:
        actual = self.response.json()
        expected = loads(data) if isinstance(data, str) else data
        actual = sanitize_objects(expected, actual)
        assert actual == expected, f'"Actual: {actual}, Expected: {expected}'

    async def the_response_content_should(self, callback: Callable[[Any], bool] = None) -> None:
        actual = self.response.json()
        assert callback(actual), f'"Actual: {actual}'
