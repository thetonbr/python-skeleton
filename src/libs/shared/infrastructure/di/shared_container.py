from asyncio import AbstractEventLoop
from logging import Logger
from typing import Dict, Any, Union

from aio_pika import Connection, connect_robust
from aioddd import SimpleEventBus, SimpleCommandBus, SimpleQueryBus
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from src.apps.app_http.controllers.controller import HTTPValidator
from src.apps.app_http.controllers.root_get_controller import RootGetController
from src.apps.app_http.middleware.http_auth_middleware import HttpAuthMiddleware
from src.apps.app_http.middleware.http_error_middleware import HttpErrorMiddleware
from src.apps.app_http.middleware.http_logger_middleware import HttpLoggerMiddleware
from src.libs.shared.infrastructure.amqp_event_publisher import AMQPEventPublisher
from src.libs.shared.infrastructure.event_mappers import ConfigEventMappers
from src.libs.shared.infrastructure.event_publisher import EventPublisherDecorator
from src.libs.shared.infrastructure.logger import create_logger
from src.libs.shared.infrastructure.mongodb_event_publisher import MongoDBEventPublisher, MongoDBEventPublisherMapper


class SharedContainer:
    # _global_provider
    loop: AbstractEventLoop
    logger: Logger
    mongodb_connection: Union[AsyncIOMotorClient, MongoClient]
    amqp_connection: Connection
    event_publisher: EventPublisherDecorator
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
        container.event_publisher = EventPublisherDecorator([])
        cls._cqrs_provider(container, settings)
        cls._http_middleware_provider(container, settings)
        cls._http_controller_provider(container, settings)
        return container

    @classmethod
    async def _global_provider(cls, container: 'SharedContainer', settings: Dict[str, Any]) -> None:
        container.loop = settings['loop']
        container.logger = create_logger('app', 'INFO')
        container.amqp_connection = await cls._open_amqp_connection(settings)
        container.mongodb_connection = await cls._open_mongodb_connection(settings)

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
        container.amqp_event_publisher = AMQPEventPublisher(
            container.amqp_connection,
            container.config_event_mappers.all(),
            settings['RABBITMQ_EXCHANGE'],
        )
        container.amqp_graveyard_event_publisher = AMQPEventPublisher(
            container.amqp_connection,
            container.config_event_mappers.all(),
            f'graveyard.{settings["RABBITMQ_EXCHANGE"]}',
        )
        container.mongodb_event_publisher = MongoDBEventPublisher(
            container.mongodb_connection.get_database(settings['MONGODB_DATABASE']),
            MongoDBEventPublisherMapper(container.config_event_mappers.all())
        )

    @staticmethod
    def _cqrs_provider(container: 'SharedContainer', _: Dict[str, Any]) -> None:
        container.event_bus = SimpleEventBus([])
        container.command_bus = SimpleCommandBus([])
        container.query_bus = SimpleQueryBus([])

    @staticmethod
    def _http_middleware_provider(container: 'SharedContainer', setting: Dict[str, Any]) -> None:
        container.http_app_logger_middleware = HttpLoggerMiddleware(container.logger)
        container.http_app_error_middleware = HttpErrorMiddleware(container.logger, setting['DEBUG'] == '1')

    @staticmethod
    def _http_controller_provider(container: 'SharedContainer', _: Dict[str, Any]) -> None:
        validator = HTTPValidator()
        container.http_app_root_get_controller = RootGetController(
            container.command_bus,
            container.query_bus,
            validator,
        )
