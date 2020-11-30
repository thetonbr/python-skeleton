from typing import Any, Dict

from aiocli.commander import Application

from project.apps.settings import container

example_router = Application()


@example_router.command(name='print-envs')
async def print_envs_command_handler(_: Dict[str, Any]) -> int:
    print(container().get('env'))
    return 0
