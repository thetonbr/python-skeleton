from typing import final

from src.libs.shared.domain.user.properties import UserId


@final
class UserIdMother:
    @staticmethod
    def create(value: str) -> UserId:
        return UserId(value)

    @classmethod
    def random(cls) -> UserId:
        return cls.create(UserId.generate().value())
