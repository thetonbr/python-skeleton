from asyncio import AbstractEventLoop, get_event_loop
from typing import Dict, Any, Optional

from src.libs.shared.infrastructure.di.account_container import AccountContainer
from src.libs.shared.infrastructure.di.shared_container import SharedContainer


class Container:
    shared: SharedContainer
    account: AccountContainer


class Builder:
    @staticmethod
    async def build(settings: Dict[str, Any], *, loop: Optional[AbstractEventLoop] = None) -> Container:
        container = Container()
        settings['loop'] = loop or get_event_loop()
        container.shared = await SharedContainer.build(settings=settings)
        container.account = await AccountContainer.build(settings=settings, shared=container.shared)
        return container
