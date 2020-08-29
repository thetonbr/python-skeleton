from typing import Dict, Any

from src.apps.app_cli.controllers.account.consumer_on_internal_user_deleted_controller import \
    ConsumerOnInternalUserDeletedController
from src.apps.app_cli.requests.account.internal_user import InternalUserDeletedEventMapper
from src.apps.app_http.controllers.account.user.change_user_password_post_controller import \
    UserPasswordChangerPostController
from src.apps.app_http.controllers.account.user.delete_user_delete_controller import UserDeleterDeleteController
from src.apps.app_http.controllers.account.user.find_user_get_controller import UserFinderGetController
from src.apps.app_http.controllers.account.user.register_user_put_controller import UserRegisterPutController
from src.apps.app_http.controllers.account.user.user_auth_get_controller import UserAuthGetController
from src.apps.app_http.controllers.account.user.user_auth_post_controller import UserAuthPostController
from src.apps.app_http.controllers.controller import HTTPValidator
from src.apps.app_http.middleware.http_auth_middleware import HttpAuthMiddleware
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
from src.libs.shared.infrastructure.di.shared_container import SharedContainer
from src.libs.shared.infrastructure.mongodb_event_publisher import MongoDBEventPublisher, MongoDBEventPublisherMapper


class AccountContainer:
    # _amqp_provider
    amqp_default_retries: int
    amqp_event_publisher: AMQPEventPublisher
    amqp_graveyard_event_publisher: AMQPEventPublisher
    # _mongodb_provider
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
    # _http_controller_provider_of_user
    http_app_user_finder_get_controller: UserFinderGetController
    http_app_user_register_put_controller: UserRegisterPutController
    http_app_user_deleter_delete_controller: UserDeleterDeleteController
    http_app_user_password_changer_post_controller: UserPasswordChangerPostController
    http_app_user_auth_post_controller: UserAuthPostController
    http_app_user_auth_get_controller: UserAuthGetController
    # _cli_controller_provider
    cli_app_consumer_on_internal_user_deleted_controller: ConsumerOnInternalUserDeletedController

    @classmethod
    async def build(cls, settings: Dict[str, Any], shared: SharedContainer) -> 'AccountContainer':
        container = cls()
        cls._event_mappers_provider(container, settings, shared)
        cls._amqp_provider(container, settings, shared)
        cls._mongodb_provider(container, settings, shared)
        cls._user_aggregate_provider(container, settings, shared)
        cls._cqrs_provider(container, settings, shared)
        cls._es_provider(container, settings, shared)
        cls._http_middleware_provider(container, settings, shared)
        cls._http_controller_provider_of_user(container, settings, shared)
        cls._cli_controller_provider(container, settings, shared)
        return container

    @staticmethod
    def _event_mappers_provider(_: 'AccountContainer', __: Dict[str, Any], shared: SharedContainer) -> None:
        shared.config_event_mappers.add(mappers=[
            # User
            UserRegisteredEventMapper(),
            UserDeletedEventMapper(),
            UserPasswordChangedEventMapper(),
            # internal User
            InternalUserDeletedEventMapper(),
        ])

    @staticmethod
    def _amqp_provider(container: 'AccountContainer', settings: Dict[str, Any], shared: SharedContainer) -> None:
        container.amqp_default_retries = 3
        mappers = shared.config_event_mappers.all()
        container.amqp_event_publisher = AMQPEventPublisher(
            connection=shared.amqp_connection,
            mappers=mappers,
            exchange=settings['RABBITMQ_EXCHANGE_ACCOUNT'],
        )
        container.amqp_graveyard_event_publisher = AMQPEventPublisher(
            connection=shared.amqp_connection,
            mappers=mappers,
            exchange=f'graveyard.{settings["RABBITMQ_EXCHANGE_ACCOUNT"]}',
        )
        shared.event_publisher.add(publishers=container.amqp_event_publisher)

    @staticmethod
    def _mongodb_provider(container: 'AccountContainer', settings: Dict[str, Any], shared: SharedContainer) -> None:
        database = shared.mongodb_connection.get_database(name=settings['MONGODB_DATABASE_ACCOUNT'])
        shared.event_publisher.add(publishers=MongoDBEventPublisher(
            database=database,
            mapper=MongoDBEventPublisherMapper(mappers=shared.config_event_mappers.all())
        ))
        container.mongodb_user_repository = MongoDBUserRepository(
            database=database,
            mapper=MongoDBUserMapper(),
            publisher=shared.event_publisher
        )
        container.mongodb_auth_repository = MongoDBAuthRepository(
            database=database,
            mapper=MongoDBAuthMapper()
        )

    @staticmethod
    def _user_aggregate_provider(container: 'AccountContainer', settings: Dict[str, Any], _: SharedContainer) -> None:
        container.token_expiration_days = int(settings['OAUTH_EXPIRATION_DAYS'])
        container.jwt_token_factory = JWTTokenFactory(secret=settings['OAUTH_SECRET'])
        container.token_generator_service = TokenGeneratorService(
            repository=container.mongodb_auth_repository,
            factory=container.jwt_token_factory,
            expiration_days=container.token_expiration_days
        )
        container.authenticator_service = AuthenticatorService(factory=container.jwt_token_factory)
        container.user_finder_service = UserFinderService(repository=container.mongodb_user_repository)
        container.user_register_service = UserRegisterService(repository=container.mongodb_user_repository)
        container.user_deleter_service = UserDeleterService(repository=container.mongodb_user_repository)
        container.user_password_changer_service = UserPasswordChangerService(
            repository=container.mongodb_user_repository
        )

    @staticmethod
    def _cqrs_provider(container: 'AccountContainer', _: Dict[str, Any], shared: SharedContainer) -> None:
        for handler in [
            # User
            RegisterUserCommandHandler(service=container.user_register_service),
            DeleteUserCommandHandler(service=container.user_deleter_service),
            ChangeUserPasswordCommandHandler(service=container.user_password_changer_service),
        ]:
            shared.command_bus.add_handler(handler=handler)
        for handler in [
            # User
            GenerateTokenQueryHandler(service=container.token_generator_service),
            ReadUserAuthQueryHandler(service=container.jwt_token_factory),
            FindUserQueryHandler(service=container.user_finder_service),
        ]:
            shared.query_bus.add_handler(handler=handler)

    @staticmethod
    def _es_provider(_: 'AccountContainer', settings: Dict[str, Any], shared: SharedContainer) -> None:
        if settings['ENABLE_EVENT_HANDLERS'] == "0":
            return
        for handler in [
        ]:
            shared.event_bus.add_handler(handler=handler)

    @staticmethod
    def _http_middleware_provider(container: 'AccountContainer', _: Dict[str, Any], shared: SharedContainer) -> None:
        shared.http_app_auth_middleware = HttpAuthMiddleware(
            logger=shared.logger,
            service=container.authenticator_service,
        )

    @staticmethod
    def _http_controller_provider_of_user(
            container: 'AccountContainer',
            _: Dict[str, Any],
            shared: SharedContainer
    ) -> None:
        validator = HTTPValidator()
        container.http_app_user_finder_get_controller = UserFinderGetController(
            command_bus=shared.command_bus,
            query_bus=shared.query_bus,
            validator=validator,
        )
        container.http_app_user_register_put_controller = UserRegisterPutController(
            command_bus=shared.command_bus,
            query_bus=shared.query_bus,
            validator=validator,
        )
        container.http_app_user_deleter_delete_controller = UserDeleterDeleteController(
            command_bus=shared.command_bus,
            query_bus=shared.query_bus,
            validator=validator,
        )
        container.http_app_user_password_changer_post_controller = UserPasswordChangerPostController(
            command_bus=shared.command_bus,
            query_bus=shared.query_bus,
            validator=validator,
        )
        container.http_app_user_auth_post_controller = UserAuthPostController(
            command_bus=shared.command_bus,
            query_bus=shared.query_bus,
            validator=validator,
        )
        container.http_app_user_auth_get_controller = UserAuthGetController(
            command_bus=shared.command_bus,
            query_bus=shared.query_bus,
            validator=validator,
        )

    @staticmethod
    def _cli_controller_provider(container: 'AccountContainer', _: Dict[str, Any], shared: SharedContainer) -> None:
        amqp_consumer = AMQPEventConsumer(
            connection=shared.amqp_connection,
            mappers=shared.config_event_mappers.all(),
            dead_publisher=container.amqp_graveyard_event_publisher
        )

        container.cli_app_consumer_on_internal_user_deleted_controller = ConsumerOnInternalUserDeletedController(
            event_mapper=InternalUserDeletedEventMapper(),
            logger=shared.logger,
            consumer=amqp_consumer,
            command_bus=shared.command_bus,
            retries=shared.amqp_default_retries,
        )
