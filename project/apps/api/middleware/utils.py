from aioddd import CommandBus, EventBus, QueryBus
from aiodi import Container
from fastapi import Depends

from project.apps.settings import container


def get_current_container() -> Container:
    return container()


def get_environment(di: Container = Depends(get_current_container)) -> str:
    return di.get('env.environment', typ=str)


def is_debug(di: Container = Depends(get_current_container)) -> bool:
    return di.get('env.environment', typ=str) != 'production' and di.get('env.debug')


def get_current_dispatcher(di: Container = Depends(get_current_container)) -> CommandBus:
    return di.get(CommandBus)


def get_current_asker(di: Container = Depends(get_current_container)) -> QueryBus:
    return di.get(QueryBus)


def get_current_notifier(di: Container = Depends(get_current_container)) -> EventBus:
    return di.get(EventBus)
