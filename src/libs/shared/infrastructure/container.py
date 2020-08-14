from asyncio import AbstractEventLoop, get_event_loop
from logging import Logger
from typing import Dict, Any, List, Union, Optional

from aio_pika import Connection, connect_robust
from aioddd import EventPublisher, EventBus, CommandBus, QueryBus, QueryHandler, \
    CommandHandler, EventHandler, SimpleEventBus, SimpleCommandBus, SimpleQueryBus
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from src.apps.app_cli.controllers.user.consumer_on_internal_user_deleted_controller import \
    ConsumerOnInternalUserDeletedController
from src.apps.app_cli.requests.account.internal_user import InternalUserDeletedEventMapper
from src.apps.app_http.controllers.controller import HTTPValidator
from src.apps.app_http.controllers.root_get_controller import RootGetController
from src.apps.app_http.controllers.user.change_user_password_post_controller import \
    UserPasswordChangerPostController
from src.apps.app_http.controllers.user.delete_user_delete_controller import UserDeleterDeleteController
from src.apps.app_http.controllers.user.find_user_get_controller import UserFinderGetController
from src.apps.app_http.controllers.user.register_user_put_controller import UserRegisterPutController
from src.apps.app_http.controllers.user.user_auth_get_controller import UserAuthGetController
from src.apps.app_http.controllers.user.user_auth_post_controller import UserAuthPostController
from src.apps.app_http.middleware.http_auth_middleware import HttpAuthMiddleware
from src.apps.app_http.middleware.http_error_middleware import HttpErrorMiddleware
from src.apps.app_http.middleware.http_logger_middleware import HttpLoggerMiddleware
from src.libs.account.user.application.authenticator_service import AuthenticatorService
from src.libs.account.user.application.deleter_service import UserDeleterService
from src.libs.account.user.application.finder_service import UserFinderService
from src.libs.account.user.application.password_changer_service import UserPasswordChangerService
from src.libs.account.user.application.register_service import UserRegisterService
from src.libs.account.user.application.token_generator_service import TokenGeneratorService
from src.libs.account.user.infrastructure.cqrs.change_user_password_command_handler import \
    ChangeUserPasswordCommandHandler
from src.libs.account.user.infrastructure.cqrs.delete_user_command_handler import DeleteUserCommandHandler
from src.libs.account.user.infrastructure.cqrs.find_user_query_handler import FindUserQueryHandler
from src.libs.account.user.infrastructure.cqrs.generate_token_query_handler import GenerateTokenQueryHandler
from src.libs.account.user.infrastructure.cqrs.read_user_auth_query_handler import ReadUserAuthQueryHandler
from src.libs.account.user.infrastructure.cqrs.register_user_command_handler import RegisterUserCommandHandler
from src.libs.account.user.infrastructure.event_mappers import UserRegisteredEventMapper, UserDeletedEventMapper, \
    UserPasswordChangedEventMapper
from src.libs.account.user.infrastructure.jwt_token_factory import JWTTokenFactory
from src.libs.account.user.infrastructure.mongodb_auth_repository import MongoDBAuthRepository, MongoDBAuthMapper
from src.libs.account.user.infrastructure.mongodb_user_repository import MongoDBUserRepository, MongoDBUserMapper
from src.libs.shared.infrastructure.amqp_event_consumer import AMQPEventConsumer
from src.libs.shared.infrastructure.amqp_event_publisher import AMQPEventPublisher
from src.libs.shared.infrastructure.event_mappers import ConfigEventMappers
from src.libs.shared.infrastructure.event_publisher import EventPublisherDecorator
from src.libs.shared.infrastructure.logger import create_logger
# pylint: disable=R0915
from src.libs.shared.infrastructure.mongodb_event_publisher import MongoDBEventPublisher, MongoDBEventPublisherMapper


class Container:
    # _global_provider
    loop: AbstractEventLoop
    logger: Logger
    mongodb_connection: Union[AsyncIOMotorClient, MongoClient]
    amqp_connection: Connection
    event_publisher: EventPublisher
    # _event_mappers_provider
    config_event_mappers: ConfigEventMappers
    # _amqp_provider
    amqp_default_retries: int
    amqp_event_publisher: AMQPEventPublisher
    amqp_graveyard_event_publisher: AMQPEventPublisher
    # _mongodb_provider
    mongodb_event_publisher: MongoDBEventPublisher
    mongodb_user_repository: MongoDBUserRepository
    mongodb_auth_repository: MongoDBAuthRepository
    # _user_provider
    token_expiration_days: int
    jwt_token_factory: JWTTokenFactory
    token_generator_service: TokenGeneratorService
    authenticator_service: AuthenticatorService
    user_finder_service: UserFinderService
    user_register_service: UserRegisterService
    user_deleter_service: UserDeleterService
    user_password_changer_service: UserPasswordChangerService
    # _cqrs_provider
    event_bus: EventBus
    event_handlers: List[EventHandler]
    command_bus: CommandBus
    command_handlers: List[CommandHandler]
    query_bus: QueryBus
    query_handlers: List[QueryHandler]
    # _http_middleware_provider
    http_app_logger_middleware: HttpLoggerMiddleware
    http_app_auth_middleware: HttpAuthMiddleware
    http_app_error_middleware: HttpErrorMiddleware
    # _http_controller_provider
    http_app_root_get_controller: RootGetController
    http_app_user_finder_get_controller: UserFinderGetController
    http_app_user_register_put_controller: UserRegisterPutController
    http_app_user_deleter_delete_controller: UserDeleterDeleteController
    http_app_user_password_changer_post_controller: UserPasswordChangerPostController
    http_app_user_auth_post_controller: UserAuthPostController
    http_app_user_auth_get_controller: UserAuthGetController
    # _cli_controller_provider
    cli_app_consumer_on_internal_user_deleted_controller: ConsumerOnInternalUserDeletedController


class Builder:
    @staticmethod
    async def build(settings: Dict[str, Any], *, loop: Optional[AbstractEventLoop] = None) -> Container:
        container = Container()
        settings['loop'] = loop or get_event_loop()
        await Builder._global_provider(container, settings)
        Builder._event_mappers_provider(container, settings)
        Builder._amqp_provider(container, settings)
        container.event_publisher = EventPublisherDecorator(
            container.amqp_event_publisher,
            container.mongodb_event_publisher,
        )
        Builder._mongodb_provider(container, settings)
        Builder._user_aggregate_provider(container, settings)
        Builder._cqrs_provider(container, settings)
        Builder._http_middleware_provider(container, settings)
        Builder._http_controller_provider(container, settings)
        Builder._cli_controller_provider(container, settings)
        return container

    @staticmethod
    async def _global_provider(container: Container, settings: Dict[str, Any]) -> None:
        container.loop = settings['loop']
        container.logger = create_logger('app', 'INFO')
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
    def _event_mappers_provider(container: Container, _: Dict[str, Any]) -> None:
        container.config_event_mappers = ConfigEventMappers(mappers=[
            # Account.User
            UserRegisteredEventMapper(),
            UserDeletedEventMapper(),
            UserPasswordChangedEventMapper(),
            # internal Account.User
            InternalUserDeletedEventMapper(),
        ])

    @staticmethod
    def _amqp_provider(container: Container, settings: Dict[str, Any]) -> None:
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
    def _mongodb_provider(container: Container, settings: Dict[str, Any]) -> None:
        database = container.mongodb_connection.get_database(settings['MONGODB_DATABASE'])
        container.mongodb_user_repository = MongoDBUserRepository(
            database,
            MongoDBUserMapper(),
            container.event_publisher
        )
        container.mongodb_auth_repository = MongoDBAuthRepository(
            database,
            MongoDBAuthMapper()
        )

    @staticmethod
    def _user_aggregate_provider(container: Container, settings: Dict[str, Any]) -> None:
        container.token_expiration_days = int(settings['OAUTH_EXPIRATION_DAYS'])
        container.jwt_token_factory = JWTTokenFactory(settings['OAUTH_SECRET'])
        container.token_generator_service = TokenGeneratorService(
            container.mongodb_auth_repository,
            container.jwt_token_factory,
            container.token_expiration_days
        )
        container.authenticator_service = AuthenticatorService(container.jwt_token_factory)
        container.user_finder_service = UserFinderService(container.mongodb_user_repository)
        container.user_register_service = UserRegisterService(container.mongodb_user_repository)
        container.user_deleter_service = UserDeleterService(container.mongodb_user_repository)
        container.user_password_changer_service = UserPasswordChangerService(container.mongodb_user_repository)

    @staticmethod
    def _cqrs_provider(container: Container, _: Dict[str, Any]) -> None:
        container.event_handlers = []
        container.event_bus = SimpleEventBus(container.event_handlers)

        container.command_handlers = [
            # Account.User
            RegisterUserCommandHandler(container.user_register_service),
            DeleteUserCommandHandler(container.user_deleter_service),
            ChangeUserPasswordCommandHandler(container.user_password_changer_service),
        ]
        container.command_bus = SimpleCommandBus(container.command_handlers)

        container.query_handlers = [
            # Account.User
            GenerateTokenQueryHandler(container.token_generator_service),
            ReadUserAuthQueryHandler(container.jwt_token_factory),
            FindUserQueryHandler(container.user_finder_service),
        ]
        container.query_bus = SimpleQueryBus(container.query_handlers)

    @staticmethod
    def _http_middleware_provider(container: Container, setting: Dict[str, Any]) -> None:
        container.http_app_logger_middleware = HttpLoggerMiddleware(container.logger)
        container.http_app_auth_middleware = HttpAuthMiddleware(container.logger, container.authenticator_service)
        container.http_app_error_middleware = HttpErrorMiddleware(container.logger, setting['DEBUG'] == '1')

    @staticmethod
    def _http_controller_provider(container: Container, _: Dict[str, Any]) -> None:
        validator = HTTPValidator()
        container.http_app_root_get_controller = RootGetController(
            container.command_bus,
            container.query_bus,
            validator,
        )
        container.http_app_user_finder_get_controller = UserFinderGetController(
            container.command_bus,
            container.query_bus,
            validator,
        )
        container.http_app_user_register_put_controller = UserRegisterPutController(
            container.command_bus,
            container.query_bus,
            validator,
        )
        container.http_app_user_deleter_delete_controller = UserDeleterDeleteController(
            container.command_bus,
            container.query_bus,
            validator,
        )
        container.http_app_user_password_changer_post_controller = UserPasswordChangerPostController(
            container.command_bus,
            container.query_bus,
            validator,
        )
        container.http_app_user_auth_post_controller = UserAuthPostController(
            container.command_bus,
            container.query_bus,
            validator,
        )
        container.http_app_user_auth_get_controller = UserAuthGetController(
            container.command_bus,
            container.query_bus,
            validator,
        )

    @staticmethod
    def _cli_controller_provider(container: Container, _: Dict[str, Any]) -> None:
        amqp_consumer = AMQPEventConsumer(
            container.amqp_connection,
            container.config_event_mappers.all(),
            container.amqp_graveyard_event_publisher
        )

        container.cli_app_consumer_on_internal_user_deleted_controller = ConsumerOnInternalUserDeletedController(
            InternalUserDeletedEventMapper(),
            container.logger,
            amqp_consumer,
            container.command_bus,
            container.amqp_default_retries,
        )
