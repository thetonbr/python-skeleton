from datetime import datetime, timedelta
from json import dumps, loads
from typing import Dict, Any

from jwt import encode, decode

from src.libs.account.user.domain.repositories import TokenFactory
from src.libs.shared.domain.user.properties import UserId


class JWTTokenFactory(TokenFactory):
    __slots__ = ('_secret', '_algorithm')

    def __init__(self, secret: str) -> None:
        self._secret = secret
        self._algorithm = 'HS256'

    async def generate(self, user_id: UserId, expiration_in_days: int) -> str:
        now = datetime.utcnow()
        return str(encode({
            'sub': dumps({'id': user_id.value()}),
            'iat': now,
            'exp': now + timedelta(days=expiration_in_days),
        }, self._secret, algorithm=self._algorithm), 'utf8')

    async def decode(self, token: str) -> Dict[str, Any]:
        return decode(token, key=self._secret, verify=True, algorithms=[self._algorithm])

    async def read(self, token: str) -> UserId:
        return UserId(loads((await self.decode(token))['sub'])['id'])
