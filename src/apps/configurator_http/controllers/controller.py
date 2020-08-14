from abc import ABC, abstractmethod
from typing import Any

from aiohttp.web import Request, Response as WebResponse, json_response


class Controller(ABC):
    @abstractmethod
    async def __call__(self, request: Request) -> WebResponse:
        pass

    @staticmethod
    def response(status_code: int, data: Any) -> WebResponse:
        return json_response(status=status_code, data=data)
