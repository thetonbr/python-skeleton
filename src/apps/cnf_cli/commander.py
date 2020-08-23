from typing import List

from aiocli.commander import Application, Command

from src.libs.shared.infrastructure.configurator.container import Container


def build_commander(container: Container) -> Application:
    return Application([
        *_amqp_commands(container),
        *_mongodb_commands(container),
    ])


def _amqp_commands(container: Container) -> List[Command]:
    return [
        Command(
            name='example:cnf:amqp-setup',
            handler=container.cli_app_setup_amqp_controller,
            optionals=[],
            positionals=[]
        ),
        Command(
            name='example:cnf:amqp-clean',
            handler=container.cli_app_clean_amqp_controller,
            optionals=[],
            positionals=[]
        ),
    ]


def _mongodb_commands(container: Container) -> List[Command]:
    return [
        Command(
            name='example:cnf:mongodb-setup',
            handler=container.cli_app_setup_mongodb_controller,
            optionals=[],
            positionals=[]
        ),
        Command(
            name='example:cnf:mongodb-clean',
            handler=container.cli_app_clean_mongodb_controller,
            optionals=[],
            positionals=[]
        ),
    ]
