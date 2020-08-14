from logging import Logger
from typing import List, final, Union, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import CollectionInvalid
from pymongo.mongo_client import MongoClient

from src.libs.configurator.mongodb.config import MongoDBServiceConfigData


@final
class MongoDBConfigurerService:
    __slots__ = ('_connection', '_configs', '_logger')

    def __init__(
            self,
            connection: Union[MongoClient, AsyncIOMotorClient],
            configs: List[MongoDBServiceConfigData],
            logger: Logger
    ):
        self._connection = connection
        self._configs = configs
        self._logger = logger

    async def setup(self, only_database: Optional[str] = None, db_suffix: Optional[str] = None) -> None:
        self._logger.info({'message': 'Setting MongoDB…'})
        configs = self._prepare_configs(only_database, db_suffix)
        for config in configs:
            database = self._connection.get_database(config.database.name)
            for col in config.collections:
                try:
                    await database.create_collection(name=col.name)
                except CollectionInvalid:
                    pass
        self._logger.info({'message': 'Finished!'})

    async def clean(self, only_database: Optional[str], db_suffix: Optional[str] = None) -> None:
        self._logger.info({'message': 'Cleaning MongoDB…'})
        configs = self._prepare_configs(only_database, db_suffix)
        _ = [await self._connection.drop_database(config.database.name) for config in configs]
        self._logger.info({'message': 'Cleaned!'})

    def _prepare_configs(
            self,
            only_database: Optional[str],
            db_suffix: Optional[str]
    ) -> List[MongoDBServiceConfigData]:
        configs = self._configs if not only_database else \
            [config for config in self._configs if config.database.name == only_database]
        for i, config in enumerate(configs):
            if db_suffix:
                config.database.name = f'{config.database.name}{db_suffix}'  # type: ignore
                configs[i] = config
        return configs
