from datetime import datetime, timedelta
from typing import Any, Callable, Dict, final

from authlib.jose import JsonWebToken
from orjson import dumps, loads

from project.libs.user.domain.properties import UserId
from project.libs.user.domain.repositories import TokenFactory


@final
class JWTTokenFactory(TokenFactory):
    __slots__ = ('_now', '_secret', '_algorithm')

    def __init__(self, now: Callable[[], datetime], secret: str) -> None:
        self._now = now
        self._secret = secret
        self._jwt = JsonWebToken(['HS256'])

    async def generate(self, user_id: UserId, expiration_in_days: int) -> str:
        now = self._now()
        return self._jwt.encode(
            header={'alg': 'HS256'},
            payload={
                'iss': 'Authlib',
                'sub': dumps({'id': user_id.value()}).decode('utf-8'),
                'iat': now,
                'exp': now + timedelta(days=expiration_in_days),
            },
            key=self._secret,
        ).decode('utf-8')

    async def decode(self, token: str) -> Dict[str, Any]:
        token = token.split('Bearer ')[-1]
        claims = self._jwt.decode(s=token, key=self._secret)
        return {
            'iss': claims.get('iss'),
            'sub': claims.get('sub'),
            'iat': claims.get('iat'),
            'exp': claims.get('exp'),
        }

    async def read(self, token: str) -> UserId:
        payload = await self.decode(token)
        data = loads(payload['sub'])
        return UserId(data['id'])
