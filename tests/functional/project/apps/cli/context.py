from asyncio import get_event_loop
from os import getenv
from types import TracebackType
from typing import Optional, Type, final

from aiocli.test_utils import TestClient, TestCommander

from project.apps.cli.main import app
from project.apps.settings import container, env
from project.libs.shared.infrastructure.mongodb_connection import MongoDBConnection


@final
class CLIContext:
    _commander: Optional[TestCommander] = None
    client: Optional[TestClient] = None
    exit_code: Optional[int] = None

    async def __aenter__(self) -> 'CLIContext':
        self._commander = TestCommander(app, loop=get_event_loop())
        self.client = TestClient(self._commander)
        await self._commander.start_commander()
        if getenv('DROP_MONGODB_DATABASE', '') == 'BEFORE':
            await self._drop_mongodb_database()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.exit_code = None
        if getenv('DROP_MONGODB_DATABASE', '') == 'AFTER':
            await self._drop_mongodb_database()
        await self._commander.close()
        self._commander = None
        self.client = None

    @staticmethod
    async def _drop_mongodb_database() -> None:
        container().get(key='connections.mongodb', typ=MongoDBConnection).client().drop_database(
            env(key='mongodb_database', typ=str)
        )

    async def i_execute_the_command(
        self,
        args: str,
        timeout_seconds: float = 1,
        timeout_exit_code: int = 1,
    ) -> None:
        self.exit_code = await self.client.handle(
            args.split(' '),
            timeout=float(timeout_seconds),
            timeout_exit_code=timeout_exit_code,
        )

    async def the_exit_status_code_should_be(self, exit_code: int) -> None:
        assert self.exit_code == exit_code, f'"Actual: {self.exit_code}, Expected: {exit_code}'
