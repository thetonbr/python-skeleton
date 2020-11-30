from unittest.mock import Mock

import pytest
from aioddd import InternalEventPublisher, SimpleEventBus
from aioddd.errors import raise_

from project.libs.shared.infrastructure.mongodb_connection import MongoDBConnection
from project.libs.user.domain.errors import (
    UserNotDeletedError,
    UserNotFoundError,
    UserNotSavedError,
)
from project.libs.user.infrastructure.mongodb_user_repository import (
    MongoDBUserMapper,
    MongoDBUserRepository,
)
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserRefreshTokenMother,
)


@pytest.mark.asyncio
async def test_mongodb_user_repository(mongodb_disposable_connection: MongoDBConnection) -> None:
    sut = MongoDBUserRepository(
        mongodb_disposable_connection,
        MongoDBUserMapper(),
        InternalEventPublisher(SimpleEventBus([])),
    )

    user = UserMother.random()
    user_id = user.id()

    assert await sut.search(user_id) is None

    await sut.save_and_publish(user)

    user = await sut.find(user_id)
    assert user.id().value() == user_id.value()

    await sut.save_and_publish(user)

    user = await sut.find_email(user.email())
    assert user.id().value() == user_id.value()

    user = await sut.find_id_and_email(user_id, user.email())
    assert user.id().value() == user_id.value()

    await sut.delete_and_publish(user)

    with pytest.raises(UserNotFoundError):
        await sut.find(user_id)

    with pytest.raises(UserNotFoundError):
        await sut.find_email(UserEmailMother.random())

    with pytest.raises(UserNotFoundError):
        await sut.find_id_and_email(user_id, UserEmailMother.random())

    with pytest.raises(UserNotFoundError):
        await sut.find_email_and_refresh_token(UserEmailMother.random(), UserRefreshTokenMother.random())

    user_mock = Mock()
    user_mock.id.side_effect = [lambda: raise_(Exception()), user_id]

    with pytest.raises(UserNotSavedError):
        await sut.save_and_publish(user_mock)

    user_mock = Mock()
    user_mock.id.side_effect = [lambda: raise_(Exception()), user_id]

    with pytest.raises(UserNotDeletedError):
        await sut.delete_and_publish(user_mock)

    user = UserMother.random_with_forgotten_password()
    await sut.save_and_publish(user)
    user_response = await sut.find_email_and_refresh_token(user.email(), user.refresh_token())
    assert user.id().value() == user_response.id().value()
    assert user.refresh_token().value() == user_response.refresh_token().value()
    assert user.refresh_token_expiration_in().value() == user_response.refresh_token_expiration_in().value()
    await sut.delete_and_publish(user_response)
