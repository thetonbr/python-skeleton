from asyncio.events import get_event_loop, AbstractEventLoop
from typing import final

from aioddd import Id
from aiounittest import AsyncTestCase

from src.libs.account.user.infrastructure.jwt_token_factory import JWTTokenFactory
from tests.unit.libs.account.user.domain.properties_mothers import UserIdMother


@final
class TestJWTTokenFactory(AsyncTestCase):
    _loop: AbstractEventLoop = get_event_loop()

    def get_event_loop(self) -> AbstractEventLoop:
        return self._loop

    async def test_generate_and_read(self) -> None:
        user_id = UserIdMother.random()
        secret = Id.generate().value()
        sut = JWTTokenFactory(secret)
        token = await sut.generate(user_id, 1)
        user_id = await sut.read(token)
        self.assertEqual(user_id.value(), user_id.value())
