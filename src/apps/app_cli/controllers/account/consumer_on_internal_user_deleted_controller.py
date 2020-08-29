from typing import final, Optional

from aioddd import Event

from src.apps.app_cli.controllers.controller import BaseConsumerController
from src.apps.app_cli.requests.account.internal_user import InternalUserDeletedEvent
from src.libs.account.user.domain.errors import UserNotFoundError
from src.libs.shared.infrastructure.amqp_event_consumer import AMQPResponder


@final
class ConsumerOnInternalUserDeletedController(BaseConsumerController):
    async def _on_event(self, event: InternalUserDeletedEvent) -> None:
        # Do something
        pass

    async def _on_error(self, err: Exception, event: Event, responder: AMQPResponder) -> Optional[Exception]:
        if isinstance(err, UserNotFoundError):
            return None
        return err
