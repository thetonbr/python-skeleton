from typing import final

import pytest
from aioddd import get_env
from requests import delete, get
from requests.auth import HTTPBasicAuth

from project.apps.settings import env
from project.libs.user.infrastructure.email_user_notifier import (
    EmailConfig,
    EmailUserNotifier,
)
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
    UserRefreshTokenMother,
)


@final
class TestEmailUserNotifier:
    _config: EmailConfig
    _email_ui_port: int
    _sut: EmailUserNotifier

    def setup(self) -> None:
        self._config = EmailConfig(
            host=env('email_host', typ=str),
            port=env('email_port', typ=int),
            host_user=env('email_host_user', typ=str),
            host_password=env('email_host_password', typ=str),
            use_tls=env('email_use_tls', typ=bool),
            from_user=env('email_from', typ=str),
        )
        self._email_ui_port = env('email_ui_port', typ=int)
        self._sut = EmailUserNotifier(self._config)

    @pytest.mark.asyncio
    async def test_notify_user_registered_successfully(self) -> None:
        user_id = UserIdMother.random()
        user_email = UserEmailMother.random()
        await self._sut.notify_user_registered(user_id, user_email)

        url_base_api = f'http://{self._config.host}:{self._email_ui_port}/api/'
        auth = HTTPBasicAuth(self._config.host_user, get_env(key='EMAIL_HOST_PASSWORD_DECODED', default='secret'))

        res = get(url=f'{url_base_api}v2/search?kind=to&query={user_email.value()}&limit=1', auth=auth)
        response = res.json()
        assert response['count'] == 1
        content = response['items'][0]['Content']
        assert content['Headers']['X-UserId'][0] == user_id.value()
        assert content['Headers']['From'][0] == self._config.from_user
        assert content['Headers']['Subject'][0] == 'Welcome to project'
        assert content['Headers']['To'][0] == user_email.value()
        assert response['items'][0]['MIME']['Parts'][0]['Body'] == f'Welcome {user_email.value()}'
        self._delete_messages(url_base_api, auth)

    @pytest.mark.asyncio
    async def test_user_password_forgotten_successfully(self) -> None:
        user_id = UserIdMother.random()
        user_email = UserEmailMother.random()
        refresh_token = UserRefreshTokenMother.random()
        await self._sut.notify_user_password_forgotten(user_id, user_email, refresh_token)

        url_base_api = f'http://{self._config.host}:{self._email_ui_port}/api/'
        auth = HTTPBasicAuth(self._config.host_user, get_env(key='EMAIL_HOST_PASSWORD_DECODED', default='secret'))

        res = get(url=f'{url_base_api}v2/search?kind=to&query={user_email.value()}&limit=1', auth=auth)
        response = res.json()
        assert response['count'] == 1
        content = response['items'][0]['Content']
        assert content['Headers']['X-UserId'][0] == user_id.value()
        assert content['Headers']['From'][0] == self._config.from_user
        assert content['Headers']['Subject'][0] == 'project - Here you have your reset password code'
        assert content['Headers']['To'][0] == user_email.value()
        assert (
            response['items'][0]['MIME']['Parts'][0]['Body']
            == f'Here you have your reset password code: {refresh_token.value()}'
        )
        self._delete_messages(url_base_api, auth)

    @pytest.mark.asyncio
    async def test_notify_user_password_resetted_successfully(self) -> None:
        user_id = UserIdMother.random()
        user_email = UserEmailMother.random()
        await self._sut.notify_user_password_resetted(user_id, user_email)

        url_base_api = f'http://{self._config.host}:{self._email_ui_port}/api/'
        auth = HTTPBasicAuth(self._config.host_user, get_env(key='EMAIL_HOST_PASSWORD_DECODED', default='secret'))

        res = get(url=f'{url_base_api}v2/search?kind=to&query={user_email.value()}&limit=1', auth=auth)
        response = res.json()
        assert response['count'] == 1
        content = response['items'][0]['Content']
        assert content['Headers']['X-UserId'][0] == user_id.value()
        assert content['Headers']['From'][0] == self._config.from_user
        assert content['Headers']['Subject'][0] == 'project - The password was reset'
        assert content['Headers']['To'][0] == user_email.value()
        assert response['items'][0]['MIME']['Parts'][0]['Body'] == 'The password was reset'
        self._delete_messages(url_base_api, auth)

    @staticmethod
    def _delete_messages(url_base_api: str, auth: HTTPBasicAuth) -> None:
        res = delete(url=f'{url_base_api}v1/messages', auth=auth)
        assert res.status_code == 200
