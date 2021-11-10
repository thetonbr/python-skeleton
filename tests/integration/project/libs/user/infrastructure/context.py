from types import TracebackType
from typing import Any, Callable, Dict, Optional, Tuple, Type, final

from aioddd import get_env
from httpx import AsyncClient, Response


@final
class MailContext:
    base_url: str
    base_auth: Tuple[str, str]
    delete_messages: bool
    client: Optional[AsyncClient]
    response: Optional[Response] = None

    def __init__(self, user: str, ui_host: str, ui_port: int, delete_messages: bool = True) -> None:
        self.base_url = f'http://{ui_host}:{ui_port}'
        self.base_auth = (user, get_env(key='EMAIL_HOST_PASSWORD_DECODED', default='secret'))
        self.delete_messages = delete_messages
        self.client = AsyncClient(auth=self.base_auth, base_url=self.base_url)

    async def __aenter__(self) -> 'MailContext':
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.response = None
        if self.delete_messages:
            await self.client.delete(url=f'{self.base_url}/api/v1/messages')
        await self.client.aclose()
        self.client = None

    async def i_send_get_request(self, user_email: str) -> None:
        self.response = await self.client.get(url=f'{self.base_url}/api/v2/search?kind=to&query={user_email}&limit=1')

    async def the_response_content_should(
        self, callback: Callable[[Dict[str, Any], Optional[str]], bool] = None
    ) -> None:
        assert self.response
        actual = self.response.json()
        assert actual['count'] == 1
        headers = actual['items'][0]['Content']['Headers']
        body = actual['items'][0]['MIME']['Parts'][0]['Body']
        assert callback(headers, body), f'"Actual: {actual}'
