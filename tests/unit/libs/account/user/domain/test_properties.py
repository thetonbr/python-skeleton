from typing import final
from unittest import TestCase

from aioddd import IdInvalidError

from src.libs.account.user.domain.errors import UserEmailNotValidError, UserPasswordNotValidError
from src.libs.account.user.domain.properties import UserEmail, UserPassword
from src.libs.shared.domain.user.properties import UserId
from tests.unit.libs import data_provider


@final
class TestUserProps(TestCase):
    @data_provider(lambda: (
            ('',),
            ('0',),
    ), )
    def test_id_fails(self, value: str) -> None:
        self.assertRaises(IdInvalidError, lambda: UserId(value))

    @data_provider(lambda: (
            ('test',),
            (' @example.com',),
    ), )
    def test_email_fails(self, value: str) -> None:
        self.assertRaises(UserEmailNotValidError, lambda: UserEmail(value))

    @data_provider(lambda: (
            ('secret',),
            ('0' * 101,),
    ), )
    def test_password_fails(self, value: str) -> None:
        self.assertRaises(UserPasswordNotValidError, lambda: UserPassword(value, False))
