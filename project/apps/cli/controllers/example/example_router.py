from aiocli.commander import Application
from aiocli.commander_app import Depends
from aioddd import Container

from project.apps.cli.middleware.utils import get_current_container

example_router = Application()


@example_router.command(name='print-envs')
async def print_envs_command_handler(container: Container = Depends(get_current_container)) -> int:
    print(container.get('env'))
    return 0
