from typing import Any, Dict, Optional, final

import pytest

from project.apps.settings import env
from project.libs.user.infrastructure.email_user_notifier import (
    EmailConfig,
    EmailUserNotifier,
)
from tests.integration.project.libs.user.infrastructure.context import MailContext
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
    UserRefreshTokenMother,
)


@final
class TestEmailUserNotifier:
    _cnf: EmailConfig
    _email_ui_port: int
    _sut: EmailUserNotifier

    def setup(self) -> None:
        self._cnf = EmailConfig(
            host=env('email_host', typ=str),
            port=env('email_port', typ=int),
            host_user=env('email_host_user', typ=str),
            host_password=env('email_host_password', typ=str),
            use_tls=env('email_use_tls', typ=bool),
            from_user=env('email_from', typ=str),
        )
        self._email_ui_port = env('email_ui_port', typ=int)
        self._sut = EmailUserNotifier(config=self._cnf)

    @pytest.mark.asyncio
    async def test_notify_user_registered_successfully(self) -> None:
        async with MailContext(user=self._cnf.host_user, ui_host=self._cnf.host, ui_port=self._email_ui_port) as ctx:
            user_id = UserIdMother.random()
            user_email = UserEmailMother.random()
            await self._sut.notify_user_registered(user_id, user_email)

            await ctx.i_send_get_request(user_email=user_email.value())

            def assert_response(headers: Dict[str, Any], body: Optional[str]) -> bool:
                assert headers['X-UserId'][0] == user_id.value()
                assert headers['From'][0] == self._cnf.from_user
                assert headers['Subject'][0] == 'Welcome to Project'
                assert headers['To'][0] == user_email.value()
                assert body == f'Welcome {user_email.value()}'
                return True

            await ctx.the_response_content_should(callback=assert_response)

    @pytest.mark.asyncio
    async def test_user_password_forgotten_successfully(self) -> None:
        async with MailContext(user=self._cnf.host_user, ui_host=self._cnf.host, ui_port=self._email_ui_port) as ctx:
            user_id = UserIdMother.random()
            user_email = UserEmailMother.random()
            refresh_token = UserRefreshTokenMother.random()
            await self._sut.notify_user_password_forgotten(user_id, user_email, refresh_token)

            await ctx.i_send_get_request(user_email=user_email.value())

            def assert_response(headers: Dict[str, Any], body: Optional[str]) -> bool:
                assert headers['X-UserId'][0] == user_id.value()
                assert headers['From'][0] == self._cnf.from_user
                assert headers['Subject'][0] == 'Project - Here you have your reset password code'
                assert headers['To'][0] == user_email.value()
                assert body == f'Here you have your reset password code: {refresh_token.value()}'
                return True

            await ctx.the_response_content_should(callback=assert_response)

    @pytest.mark.asyncio
    async def test_notify_user_password_resetted_successfully(self) -> None:
        async with MailContext(user=self._cnf.host_user, ui_host=self._cnf.host, ui_port=self._email_ui_port) as ctx:
            user_id = UserIdMother.random()
            user_email = UserEmailMother.random()
            await self._sut.notify_user_password_resetted(user_id, user_email)

            await ctx.i_send_get_request(user_email=user_email.value())

            def assert_response(headers: Dict[str, Any], body: Optional[str]) -> bool:
                assert headers['X-UserId'][0] == user_id.value()
                assert headers['From'][0] == self._cnf.from_user
                assert headers['Subject'][0] == 'Project - The password was reset'
                assert headers['To'][0] == user_email.value()
                assert body == 'The password was reset'
                return True

            await ctx.the_response_content_should(callback=assert_response)
