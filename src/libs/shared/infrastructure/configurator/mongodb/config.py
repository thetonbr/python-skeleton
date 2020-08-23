from typing import NamedTuple, List


class Database(NamedTuple):
    name: str


class Collection(NamedTuple):
    name: str


class MongoDBServiceConfigData(NamedTuple):
    database: Database
    collections: List[Collection]
