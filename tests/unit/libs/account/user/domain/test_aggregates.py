from typing import final
from unittest import TestCase

from src.libs.account.user.domain.aggregates import User
from src.libs.account.user.domain.errors import UserPasswordNotMatchError
from src.libs.account.user.domain.events import UserRegistered, UserDeleted, UserPasswordChanged
from tests.unit.libs.account.user.domain.aggregates_mothers import UserMother
from tests.unit.libs.account.user.domain.properties_mothers import UserIdMother, UserEmailMother, UserPasswordMother


@final
class TestUser(TestCase):
    def test_register(self) -> None:
        user = User.register(UserIdMother.random(), UserEmailMother.random(), UserPasswordMother.random())
        events = user.pull_aggregate_events()
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], UserRegistered)

    def test_deleted(self) -> None:
        user = UserMother.random()
        user.delete()
        events = user.pull_aggregate_events()
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], UserDeleted)

    def test_validate_password(self) -> None:
        plain_password = 'secret123456'
        user = UserMother.from_password(UserPasswordMother.create(plain_password, False))
        user.validate_password(plain_password)

    def test_validate_password_fails(self) -> None:
        user = UserMother.random()
        self.assertRaises(UserPasswordNotMatchError, lambda: user.validate_password('secret123456'))

    def test_change_password(self) -> None:
        old_plain_password = 'secret123456'
        old_password = UserPasswordMother.create(old_plain_password, False)
        user = UserMother.from_password(old_password)
        new_password = UserPasswordMother.random()
        user.change_password(old_plain_password, new_password)
        self.assertEqual(user.password(), new_password)
        events = user.pull_aggregate_events()
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], UserPasswordChanged)
