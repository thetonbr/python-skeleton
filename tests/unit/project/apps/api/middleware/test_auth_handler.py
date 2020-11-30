import pytest

from project.apps.api.middleware.auth_handler import UserAuth, auth_guard
from project.libs.user.domain.errors import UserUnauthorizedError
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
)


@pytest.mark.test
def test_auth_guard_fails_when_user_unauthorized() -> None:
    with pytest.raises(UserUnauthorizedError):
        auth_guard(
            UserIdMother.random().value(),
            UserAuth(**{'id': UserIdMother.random().value(), 'email': UserEmailMother.random().value()}),
        )
