from typing import final

from project.libs.user.infrastructure.mongodb_user_repository import MongoDBUserMapper
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother


@final
class TestMongoDBUserMapper:
    @staticmethod
    def test_to_document_and_to_aggregate() -> None:
        user = UserMother.random()

        sut = MongoDBUserMapper()

        doc = sut.to_document(user)
        agg = sut.to_aggregate(doc)

        assert agg.id().value() == user.id().value()
        assert agg.email().value() == user.email().value()
        assert agg.password().value() == user.password().value()
