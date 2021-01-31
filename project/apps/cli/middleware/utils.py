from aioddd import Container

from apps.settings import container


def get_current_container() -> Container:
    return container()
