from datetime import datetime
from typing import final

import pytest
from aioddd import Id

from project.libs.user.infrastructure.jwt_token_factory import JWTTokenFactory
from tests.unit.project.libs.user.domain.properties_mothers import UserIdMother


@final
class TestJWTTokenFactory:
    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_and_read() -> None:
        user_id = UserIdMother.random()
        secret = Id.generate().value()

        sut = JWTTokenFactory(lambda: datetime.utcnow(), secret)

        token = await sut.generate(user_id, 1)
        auth_user_id = await sut.read(token)

        assert user_id.value() == auth_user_id.value()
