from aiodi import Container

from project.apps.settings import container


def get_current_container() -> Container:
    return container()
