from asyncio import AbstractEventLoop
from asyncio.events import get_event_loop
from inspect import getmembers
from types import TracebackType
from typing import Optional, Type, Any

from aiohttp.web import Application, run_app
from pyaioapp import AsyncApplication

from src.apps.cnf_http import settings
from src.apps.cnf_http.server import build_server
from src.libs.shared.infrastructure.configurator.container import Builder, Container
from src.libs.shared.infrastructure.debugger import enable_debugger
from src.libs.shared.infrastructure.logger import remove_logger_root_handlers

SETTINGS = dict(getmembers(settings))


class HttpApp(AsyncApplication[Container, Application]):
    async def __aenter__(self) -> Application:
        self._container = await Builder.build(SETTINGS, loop=self.loop)
        self._runner: Application = build_server(self._container)
        self._runner.on_shutdown.append(lambda app: self.__aexit__(None, None, None))
        return self._runner

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> None:
        if self._container:
            await self._container.amqp_connection.close()
            self._container.mongodb_connection.close()

    def __call__(self) -> None:
        run_app(self.__aenter__(), host=SETTINGS['HTTP_HOST'], port=int(SETTINGS['HTTP_PORT']))


def main(loop: AbstractEventLoop) -> Any:
    remove_logger_root_handlers()

    if SETTINGS['DEBUG'] == '1':
        enable_debugger(SETTINGS['DEBUG_HOST'], int(SETTINGS['DEBUG_PORT']))

    if SETTINGS['ENVIRONMENT'] != 'production' and SETTINGS['LIVE_RELOAD'] == '1':
        return HttpApp(loop).__aenter__()

    return HttpApp(loop).__call__()


if __name__ == '__main__':
    main(get_event_loop())
