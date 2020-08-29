from asyncio import AbstractEventLoop, get_event_loop
from logging import Logger
from typing import Dict, final, Union, Any, Optional

from aio_pika import Connection, connect_robust
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from src.apps.cnf_cli.controllers.amqp.clean_amqp_controller import CleanAMQPController
from src.apps.cnf_cli.controllers.amqp.setup_amqp_controller import SetupAMQPController
from src.apps.cnf_cli.controllers.mongodb.clean_mongodb_controller import CleanMongoDBController
from src.apps.cnf_cli.controllers.mongodb.setup_mongodb_controller import SetupMongoDBController
from src.apps.cnf_http.controllers.amqp.clean_amqp_get_controller import CleanAMQPGetController
from src.apps.cnf_http.controllers.amqp.setup_amqp_get_controller import SetupAMQPGetController
from src.apps.cnf_http.controllers.mongodb.clean_mongodb_get_controller import CleanMongoDBGetController
from src.apps.cnf_http.controllers.mongodb.setup_mongodb_get_controller import SetupMongoDBGetController
from src.apps.cnf_http.controllers.root_get_controller import RootGetController
from src.libs.shared.infrastructure.configurator.amqp.configurer import AMQPConfigurerService
from src.libs.shared.infrastructure.configurator.amqp.services import RootAMQPServiceConfig
from src.libs.shared.infrastructure.configurator.amqp.services.account import AccountAMQPServiceConfig
from src.libs.shared.infrastructure.configurator.mongodb.configurer import MongoDBConfigurerService
from src.libs.shared.infrastructure.configurator.mongodb.services import RootMongoDBServiceConfigData
from src.libs.shared.infrastructure.configurator.mongodb.services.account import AccountMongoDBServiceConfigData
from src.libs.shared.infrastructure.logger import create_logger


@final
class Container:
    # _global_provider
    loop: AbstractEventLoop
    logger: Logger
    mongodb_connection: Union[AsyncIOMotorClient, MongoClient]
    amqp_connection: Connection
    # _amqp_provider
    amqp_configurer_service: AMQPConfigurerService
    # _mongodb_provider
    mongodb_configurer_service: MongoDBConfigurerService
    # _http_controller_provider
    http_app_root_get_controller: RootGetController
    http_app_setup_amqp_get_controller: SetupAMQPGetController
    http_app_clean_amqp_get_controller: CleanAMQPGetController
    http_app_setup_mongodb_get_controller: SetupMongoDBGetController
    http_app_clean_mongodb_get_controller: CleanMongoDBGetController
    # _cli_controller_provider
    cli_app_setup_amqp_controller: SetupAMQPController
    cli_app_clean_amqp_controller: CleanAMQPController
    cli_app_setup_mongodb_controller: SetupMongoDBController
    cli_app_clean_mongodb_controller: CleanMongoDBController


class Builder:
    @staticmethod
    async def build(settings: Dict[str, Any], *, loop: Optional[AbstractEventLoop] = None) -> Container:
        container = Container()
        settings['loop'] = loop or get_event_loop()
        await Builder._global_provider(container, settings)
        Builder._amqp_provider(container, settings)
        Builder._mongodb_provider(container, settings)
        Builder._http_controller_provider(container, settings)
        Builder._cli_controller_provider(container, settings)
        return container

    @staticmethod
    async def _global_provider(container: Container, settings: Dict[str, Any]) -> None:
        container.loop = settings['loop']
        container.logger = create_logger('service-configurator', 'INFO')
        container.amqp_connection = await Builder._open_amqp_connection(settings)
        container.mongodb_connection = await Builder._open_mongodb_connection(settings)

    @staticmethod
    async def _open_amqp_connection(settings: Dict[str, Any]) -> Connection:
        return await connect_robust(
            login=settings['RABBITMQ_USER'],
            password=settings['RABBITMQ_PASSWORD'],
            host=settings['RABBITMQ_HOST'],
            port=settings['RABBITMQ_PORT'],
            virtualhost=settings['RABBITMQ_VHOST'],
            loop=settings['loop'],
        )

    @staticmethod
    async def _open_mongodb_connection(settings: Dict[str, Any]) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(
            'mongodb://'
            f'{settings["MONGODB_USERNAME"]}:{settings["MONGODB_PASSWORD"]}@'
            f'{settings["MONGODB_HOST"]}:{settings["MONGODB_PORT"]}/'
            f'{settings["MONGODB_ROOT_DATABASE"]}',
            io_loop=settings['loop'],
        )

    @staticmethod
    def _amqp_provider(container: Container, _: Dict[str, Any]) -> None:
        container.amqp_configurer_service = AMQPConfigurerService(
            container.amqp_connection,
            [
                RootAMQPServiceConfig,
                AccountAMQPServiceConfig,
            ],
            container.logger
        )

    @staticmethod
    def _mongodb_provider(container: Container, _: Dict[str, Any]) -> None:
        container.mongodb_configurer_service = MongoDBConfigurerService(
            container.mongodb_connection,
            [
                *RootMongoDBServiceConfigData,
                *AccountMongoDBServiceConfigData,
            ],
            container.logger
        )

    @staticmethod
    def _http_controller_provider(container: Container, _: Dict[str, Any]) -> None:
        container.http_app_root_get_controller = RootGetController()
        container.http_app_setup_amqp_get_controller = SetupAMQPGetController(
            container.amqp_configurer_service
        )
        container.http_app_clean_amqp_get_controller = CleanAMQPGetController(
            container.amqp_configurer_service
        )
        container.http_app_setup_mongodb_get_controller = SetupMongoDBGetController(
            container.mongodb_configurer_service
        )
        container.http_app_clean_mongodb_get_controller = CleanMongoDBGetController(
            container.mongodb_configurer_service
        )

    @staticmethod
    def _cli_controller_provider(container: Container, _: Dict[str, Any]) -> None:
        container.cli_app_setup_amqp_controller = SetupAMQPController(
            container.amqp_configurer_service
        )
        container.cli_app_clean_amqp_controller = CleanAMQPController(
            container.amqp_configurer_service
        )
        container.cli_app_setup_mongodb_controller = SetupMongoDBController(
            container.mongodb_configurer_service
        )
        container.cli_app_clean_mongodb_controller = CleanMongoDBController(
            container.mongodb_configurer_service
        )
