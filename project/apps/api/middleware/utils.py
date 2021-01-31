from aioddd import Container, CommandBus, QueryBus, EventBus
from fastapi import Depends

from project.apps.settings import container


def get_current_container() -> Container:
    return container()


def get_current_dispatcher(di: Container = Depends(get_current_container)) -> CommandBus:
    return di.get(CommandBus)


def get_current_asker(di: Container = Depends(get_current_container)) -> QueryBus:
    return di.get(QueryBus)


def get_current_notifier(di: Container = Depends(get_current_container)) -> EventBus:
    return di.get(EventBus)
