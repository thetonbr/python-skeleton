from typing import final

from project.libs.user.infrastructure.mongodb_auth_repository import MongoDBAuthMapper
from tests.unit.project.libs.user.domain.aggregates_mothers import UserMother


@final
class TestMongoDBAuthMapper:
    @staticmethod
    def test_to_document_and_to_aggregate() -> None:
        user = UserMother.random()

        sut = MongoDBAuthMapper()

        doc = sut.to_document(user)
        agg = sut.to_aggregate(doc)

        assert agg.id().value() == user.id().value()
        assert agg.email().value() == user.email().value()
        assert agg.password().value() == user.password().value()
