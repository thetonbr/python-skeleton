from typing import Any, Dict, Union, final

from aioddd import Aggregate, Id

from project.libs.shared.infrastructure.mongodb_utils import MongoDBBaseMapper


@final
class TestMongoDBBaseMapper:
    @staticmethod
    def test_to_documents_and_to_aggregates() -> None:
        class _Aggregate(Aggregate):
            _id: str

            def __init__(self, agg_id: str) -> None:
                self._id = agg_id

            def id(self) -> str:
                return self._id

        class _MongoDBBaseMapper(MongoDBBaseMapper):
            def to_aggregate(self, data: Dict[str, Any]) -> Union[Aggregate, Any]:
                return _Aggregate(data['agg_id'])

            def to_document(self, aggregate: Union[_Aggregate, Any]) -> Dict[str, Any]:
                return {'agg_id': aggregate.id()}

        the_agg = _Aggregate(Id.generate().value())

        sut = _MongoDBBaseMapper()

        docs = sut.to_documents([the_agg])
        aggs = sut.to_aggregates(docs)
        for agg in aggs:
            assert agg.id() == the_agg.id()
