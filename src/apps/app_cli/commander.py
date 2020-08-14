from typing import List, Tuple, Dict, Any

from aiocli.commander import Application, Command

from src.libs.shared.infrastructure.container import Container

_optionals: List[Tuple[str, Dict[str, Any]]] = [
    ('--times', {'default': 0}),
    ('--retries', {'default': None}),
    ('--stop', {'action': 'store_true'})
]
_positionals: List[Tuple[str, Dict[str, Any]]] = []


def build_commander(container: Container) -> Application:
    return Application([
        Command(
            name='skeleton:account:consumer-on-internal-user-deleted',
            handler=container.cli_app_consumer_on_internal_user_deleted_controller,
            optionals=_optionals,
            positionals=_positionals
        )
    ])
