from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from typing import Optional, final

from opnieuw import retry

from project.libs.user.domain.properties import UserEmail, UserId, UserRefreshToken
from project.libs.user.domain.repositories import UserNotifier


@dataclass
class EmailConfig:
    host: str
    port: int
    host_user: str
    host_password: str
    use_tls: bool
    from_user: str


@final
class EmailUserNotifier(UserNotifier):
    _config: EmailConfig
    _smtp_client: Optional[SMTP]

    def __init__(self, config: EmailConfig) -> None:
        self._config = config
        self._smtp_client = None

    def __del__(self) -> None:
        if self._smtp_client:
            self._smtp.quit()

    async def notify_user_registered(self, user_id: UserId, email: UserEmail) -> None:
        self._send_mail(
            user_id=user_id.value(),
            to_address=email.value(),
            subject='Welcome to Project',
            mime_text_plain_content=f'Welcome {email.value()}',
        )

    async def notify_user_password_forgotten(
        self, user_id: UserId, email: UserEmail, refresh_token: UserRefreshToken
    ) -> None:
        self._send_mail(
            user_id=user_id.value(),
            to_address=email.value(),
            subject='Project - Here you have your reset password code',
            mime_text_plain_content=f'Here you have your reset password code: {refresh_token.value()}',
        )

    async def notify_user_password_resetted(self, user_id: UserId, email: UserEmail) -> None:
        self._send_mail(
            user_id=user_id.value(),
            to_address=email.value(),
            subject='Project - The password was reset',
            mime_text_plain_content='The password was reset',
        )

    @property
    def _smtp(self) -> SMTP:
        if self._smtp_client is None:
            self._smtp_client = SMTP(self._config.host, self._config.port)
            if self._config.use_tls:
                self._smtp_client.starttls()
            self._smtp_client.login(self._config.host_user, self._config.host_password)
        return self._smtp_client

    @retry(retry_on_exceptions=ConnectionRefusedError, max_calls_total=3, retry_window_after_first_call_in_seconds=1)
    def _send_mail(self, user_id: str, to_address: str, subject: str, mime_text_plain_content: str) -> None:
        msg = MIMEMultipart()

        msg['From'] = self._config.from_user
        msg['To'] = to_address
        msg['Subject'] = subject
        msg['X-UserId'] = user_id

        msg.attach(MIMEText(_text=mime_text_plain_content, _subtype='plain'))

        self._smtp.sendmail(from_addr=msg['From'], to_addrs=msg['To'], msg=msg.as_string())
