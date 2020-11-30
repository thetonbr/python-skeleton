from asyncio import AbstractEventLoop, get_event_loop
from typing import Optional, Union, final

# noinspection PyProtectedMember
from motor.motor_asyncio import AsyncIOMotorClient as AsyncMongoClient
from motor.motor_asyncio import AsyncIOMotorCollection as AsyncMongoCollection
from motor.motor_asyncio import AsyncIOMotorDatabase as AsyncMongoDatabase
from pymongo import MongoClient as SyncMongoClient
from pymongo.collection import Collection as SyncMongoCollection
from pymongo.database import Database as SyncMongoDatabase


@final
class MongoDBConnection:
    _client: Optional[Union[SyncMongoClient, AsyncMongoClient]]
    _uri_connection: str
    _database_name: str

    def __init__(self, uri_connection: str, database_name: str) -> None:
        self._client = None
        self._uri_connection = uri_connection
        self._database_name = database_name

    def default_database_name(self) -> str:
        return self._database_name

    def client(self, io_loop: Optional[AbstractEventLoop] = None) -> Union[SyncMongoClient, AsyncMongoClient]:
        self.open(io_loop)
        return self._client

    def database(self, database: Optional[str] = None) -> Union[SyncMongoDatabase, AsyncMongoDatabase]:
        return self.client().get_database(self._database_name if not database else database)

    def collection(
        self,
        collection: str,
        database: Optional[str] = None,
    ) -> Union[SyncMongoCollection, AsyncMongoCollection]:
        return self.database(database).get_collection(collection)

    def open(self, io_loop: Optional[AbstractEventLoop] = None) -> 'MongoDBConnection':
        if not self._client:
            self._client = AsyncMongoClient(
                self._uri_connection,
                uuidRepresentation='standard',
                io_loop=io_loop if io_loop else get_event_loop(),
            )
        return self

    def close(self) -> None:
        if self._client:
            self._client.close()

    async def drop_database(self, database: Optional[str] = None) -> None:
        await self.client().drop_database(database or self._database_name)
