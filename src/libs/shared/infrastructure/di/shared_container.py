from asyncio import AbstractEventLoop
from logging import Logger
from typing import Dict, Any, Union

from aio_pika import Connection, connect_robust
from aioddd import SimpleEventBus, SimpleCommandBus, SimpleQueryBus
from aioddd.events import EventPublishers, ConfigEventMappers
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from src.apps.app_http.controllers.controller import HTTPValidator
from src.apps.app_http.controllers.root_get_controller import RootGetController
from src.apps.app_http.middleware.http_auth_middleware import HttpAuthMiddleware
from src.apps.app_http.middleware.http_error_middleware import HttpErrorMiddleware
from src.apps.app_http.middleware.http_logger_middleware import HttpLoggerMiddleware
from src.libs.shared.infrastructure.amqp_event_publisher import AMQPEventPublisher
from src.libs.shared.infrastructure.internal_event_publisher import InternalEventPublisher
from src.libs.shared.infrastructure.logger import create_logger
from src.libs.shared.infrastructure.mongodb_event_publisher import MongoDBEventPublisher, MongoDBEventPublisherMapper


class SharedContainer:
    # _global_provider
    loop: AbstractEventLoop
    logger: Logger
    mongodb_connection: Union[AsyncIOMotorClient, MongoClient]
    amqp_connection: Connection
    event_publisher: EventPublishers
    # _event_mappers_provider
    config_event_mappers: ConfigEventMappers
    # _amqp_provider
    amqp_default_retries: int
    amqp_event_publisher: AMQPEventPublisher
    amqp_graveyard_event_publisher: AMQPEventPublisher
    # _mongodb_provider
    mongodb_event_publisher: MongoDBEventPublisher
    # _cqrs_provider
    event_bus: SimpleEventBus
    command_bus: SimpleCommandBus
    query_bus: SimpleQueryBus
    # _http_middleware_provider
    http_app_logger_middleware: HttpLoggerMiddleware
    http_app_auth_middleware: HttpAuthMiddleware
    http_app_error_middleware: HttpErrorMiddleware
    # _http_controller_provider
    http_app_root_get_controller: RootGetController

    @classmethod
    async def build(cls, settings: Dict[str, Any]) -> 'SharedContainer':
        container = cls()
        await cls._global_provider(container, settings)
        cls._event_mappers_provider(container, settings)
        cls._amqp_provider(container, settings)
        container.event_publisher = EventPublishers([])
        cls._cqrs_provider(container, settings)
        cls._es_provider(container, settings)
        cls._http_middleware_provider(container, settings)
        cls._http_controller_provider(container, settings)
        return container

    @classmethod
    async def _global_provider(cls, container: 'SharedContainer', settings: Dict[str, Any]) -> None:
        container.loop = settings['loop']
        container.logger = create_logger(name='app', level='INFO')
        container.amqp_connection = await cls._open_amqp_connection(settings=settings)
        container.mongodb_connection = await cls._open_mongodb_connection(settings=settings)

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
    def _event_mappers_provider(container: 'SharedContainer', _: Dict[str, Any]) -> None:
        container.config_event_mappers = ConfigEventMappers(mappers=[])

    @staticmethod
    def _amqp_provider(container: 'SharedContainer', settings: Dict[str, Any]) -> None:
        container.amqp_default_retries = 3
        mappers = container.config_event_mappers.all()
        container.amqp_event_publisher = AMQPEventPublisher(
            connection=container.amqp_connection,
            mappers=mappers,
            exchange=settings['RABBITMQ_EXCHANGE'],
        )
        container.amqp_graveyard_event_publisher = AMQPEventPublisher(
            connection=container.amqp_connection,
            mappers=mappers,
            exchange=f'graveyard.{settings["RABBITMQ_EXCHANGE"]}',
        )
        container.mongodb_event_publisher = MongoDBEventPublisher(
            database=container.mongodb_connection.get_database(name=settings['MONGODB_DATABASE']),
            mapper=MongoDBEventPublisherMapper(mappers=mappers)
        )

    @staticmethod
    def _cqrs_provider(container: 'SharedContainer', _: Dict[str, Any]) -> None:
        container.command_bus = SimpleCommandBus(handlers=[])
        container.query_bus = SimpleQueryBus(handlers=[])

    @staticmethod
    def _es_provider(container: 'SharedContainer', _: Dict[str, Any]) -> None:
        container.event_bus = SimpleEventBus(handlers=[])
        container.event_publisher.add(publishers=InternalEventPublisher(event_bus=container.event_bus))

    @staticmethod
    def _http_middleware_provider(container: 'SharedContainer', setting: Dict[str, Any]) -> None:
        container.http_app_logger_middleware = HttpLoggerMiddleware(logger=container.logger)
        container.http_app_error_middleware = HttpErrorMiddleware(
            logger=container.logger,
            debug=setting['DEBUG'] == '1'
        )

    @staticmethod
    def _http_controller_provider(container: 'SharedContainer', _: Dict[str, Any]) -> None:
        validator = HTTPValidator()
        container.http_app_root_get_controller = RootGetController(
            command_bus=container.command_bus,
            query_bus=container.query_bus,
            validator=validator,
        )
