from asyncio import get_event_loop
from inspect import getmembers
from types import TracebackType
from typing import Optional, Type

from aiocli.commander import Application, run_app
from pyaioapp import AsyncApplication

from src.apps.app_cli import settings
from src.apps.app_cli.commander import build_commander
from src.libs.shared.infrastructure.container import Builder, Container
from src.libs.shared.infrastructure.debugger import enable_debugger
from src.libs.shared.infrastructure.logger import remove_logger_root_handlers

SETTINGS = dict(getmembers(settings))


class CliApp(AsyncApplication[Container, Application]):
    async def __aenter__(self) -> Application:
        self._container = await Builder.build(SETTINGS, loop=self.loop)
        self._runner = build_commander(self._container)
        self._runner.on_shutdown.append(lambda app: self.__aexit__(None, None, None))
        return self._runner

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> None:
        if self._container:
            await self._container.shared.amqp_connection.close()
            self._container.shared.mongodb_connection.close()

    def __call__(self) -> None:
        run_app(self.__aenter__(), loop=self.loop)


if __name__ == '__main__':
    remove_logger_root_handlers()

    if SETTINGS['DEBUG'] == '1':
        enable_debugger(SETTINGS['DEBUG_HOST'], int(SETTINGS['DEBUG_PORT']))

    CliApp(get_event_loop()).__call__()
