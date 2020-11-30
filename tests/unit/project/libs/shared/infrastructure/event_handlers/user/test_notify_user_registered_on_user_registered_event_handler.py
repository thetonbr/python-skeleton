from typing import Dict, List, final
from unittest.mock import Mock

import pytest
from aioddd import CommandBus
from aioddd.testing import mock

from project.libs.shared.infrastructure.event_handlers.user.notify_user_registered_on_user_registered_event_handler import (
    NotifyUserRegisteredOnUserRegisteredEventHandler,
)
from project.libs.user.domain.errors import UserNotFoundError
from project.libs.user.domain.events import UserRegistered
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
)


@final
class TestNotifyUserRegisteredOnUserRegisteredEventHandler:
    _mock_command_bus: Mock
    _sut: NotifyUserRegisteredOnUserRegisteredEventHandler
    _kwargs: Dict[str, List[UserRegistered]]

    def setup(self) -> None:
        self._mock_command_bus = mock(CommandBus, ['dispatch'])
        self._sut = NotifyUserRegisteredOnUserRegisteredEventHandler(self._mock_command_bus)
        self._kwargs = {
            'events': [
                UserRegistered(
                    UserRegistered.Attributes(
                        UserIdMother.random(),
                        UserEmailMother.random(),
                    )
                ),
            ],
        }

    @pytest.mark.asyncio
    async def test_handle_successfully(self) -> None:
        self._mock_command_bus.dispatch.return_value = None

        assert self._sut.subscribed_to() == [UserRegistered]
        await self._sut.handle(**self._kwargs)

        self._mock_command_bus.dispatch.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_successfully_even_if_user_not_found(self) -> None:
        self._mock_command_bus.dispatch.side_effect = UserNotFoundError.create()

        assert self._sut.subscribed_to() == [UserRegistered]
        await self._sut.handle(**self._kwargs)

        self._mock_command_bus.dispatch.assert_called_once()
