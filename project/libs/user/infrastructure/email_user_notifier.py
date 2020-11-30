import smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import final

from retry import retry

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
    __slots__ = '_config'

    def __init__(self, config: EmailConfig) -> None:
        self._config = config

    @retry(ConnectionRefusedError, tries=3, delay=1)
    async def notify_user_registered(self, user_id: UserId, email: UserEmail) -> None:
        server = smtplib.SMTP(self._config.host, self._config.port)

        if self._config.use_tls:
            server.starttls()

        msg = MIMEMultipart()
        msg['From'] = self._config.from_user
        msg['To'] = email.value()
        msg['Subject'] = 'Welcome to project'
        msg['X-UserId'] = user_id.value()
        msg.attach(MIMEText(f'Welcome {email.value()}', 'plain'))

        server.login(self._config.host_user, self._config.host_password)

        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()

    @retry(ConnectionRefusedError, tries=3, delay=1)
    async def notify_user_password_forgotten(
        self, user_id: UserId, email: UserEmail, refresh_token: UserRefreshToken
    ) -> None:
        server = smtplib.SMTP(self._config.host, self._config.port)

        if self._config.use_tls:
            server.starttls()

        msg = MIMEMultipart()
        msg['From'] = self._config.from_user
        msg['To'] = email.value()
        msg['Subject'] = 'project - Here you have your reset password code'
        msg['X-UserId'] = user_id.value()
        msg.attach(MIMEText(f'Here you have your reset password code: {refresh_token.value()}', 'plain'))

        server.login(self._config.host_user, self._config.host_password)

        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()

    @retry(ConnectionRefusedError, tries=3, delay=1)
    async def notify_user_password_resetted(self, user_id: UserId, email: UserEmail) -> None:
        server = smtplib.SMTP(self._config.host, self._config.port)

        if self._config.use_tls:
            server.starttls()

        msg = MIMEMultipart()
        msg['From'] = self._config.from_user
        msg['To'] = email.value()
        msg['Subject'] = 'project - The password was reset'
        msg['X-UserId'] = user_id.value()
        msg.attach(MIMEText('The password was reset', 'plain'))

        server.login(self._config.host_user, self._config.host_password)

        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
