from typing import List

from aiocli.commander import Application, Command

from src.libs.configurator.shared.infrastructure.container import Container


def build_commander(container: Container) -> Application:
    return Application([
        *_amqp_commands(container),
        *_mongodb_commands(container),
    ])


def _amqp_commands(container: Container) -> List[Command]:
    return [
        Command(
            name='example:service-configurator:amqp-setup',
            handler=container.cli_app_setup_amqp_controller,
            optionals=[],
            positionals=[]
        ),
        Command(
            name='example:service-configurator:amqp-clean',
            handler=container.cli_app_clean_amqp_controller,
            optionals=[],
            positionals=[]
        ),
    ]


def _mongodb_commands(container: Container) -> List[Command]:
    return [
        Command(
            name='example:service-configurator:mongodb-setup',
            handler=container.cli_app_setup_mongodb_controller,
            optionals=[],
            positionals=[]
        ),
        Command(
            name='example:service-configurator:mongodb-clean',
            handler=container.cli_app_clean_mongodb_controller,
            optionals=[],
            positionals=[]
        ),
    ]
