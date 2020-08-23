from typing import Dict, Any

from src.apps.app_cli.controllers.user.consumer_on_internal_user_deleted_controller import \
    ConsumerOnInternalUserDeletedController
from src.apps.app_cli.requests.account.internal_user import InternalUserDeletedEventMapper
from src.apps.app_http.controllers.controller import HTTPValidator
from src.apps.app_http.controllers.user.change_user_password_post_controller import \
    UserPasswordChangerPostController
from src.apps.app_http.controllers.user.delete_user_delete_controller import UserDeleterDeleteController
from src.apps.app_http.controllers.user.find_user_get_controller import UserFinderGetController
from src.apps.app_http.controllers.user.register_user_put_controller import UserRegisterPutController
from src.apps.app_http.controllers.user.user_auth_get_controller import UserAuthGetController
from src.apps.app_http.controllers.user.user_auth_post_controller import UserAuthPostController
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
    # _http_controller_provider
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
        cls._event_mappers_provider(shared)
        cls._amqp_provider(container, settings, shared)
        cls._mongodb_provider(container, settings, shared)
        cls._user_aggregate_provider(container, settings, shared)
        cls._cqrs_provider(container, settings, shared)
        cls._http_middleware_provider(container, settings, shared)
        cls._http_controller_provider(container, settings, shared)
        cls._cli_controller_provider(container, settings, shared)
        return container

    @staticmethod
    def _event_mappers_provider(shared: SharedContainer) -> None:
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
        container.amqp_event_publisher = AMQPEventPublisher(
            shared.amqp_connection,
            shared.config_event_mappers.all(),
            settings['RABBITMQ_EXCHANGE_ACCOUNT'],
        )
        container.amqp_graveyard_event_publisher = AMQPEventPublisher(
            shared.amqp_connection,
            shared.config_event_mappers.all(),
            f'graveyard.{settings["RABBITMQ_EXCHANGE_ACCOUNT"]}',
        )
        shared.event_publisher.add_publisher(container.amqp_event_publisher)

    @staticmethod
    def _mongodb_provider(container: 'AccountContainer', settings: Dict[str, Any], shared: SharedContainer) -> None:
        database = shared.mongodb_connection.get_database(settings['MONGODB_DATABASE_ACCOUNT'])
        shared.event_publisher.add_publisher(MongoDBEventPublisher(
            database,
            MongoDBEventPublisherMapper(shared.config_event_mappers.all())
        ))
        container.mongodb_user_repository = MongoDBUserRepository(
            database,
            MongoDBUserMapper(),
            shared.event_publisher
        )
        container.mongodb_auth_repository = MongoDBAuthRepository(
            database,
            MongoDBAuthMapper()
        )

    @staticmethod
    def _user_aggregate_provider(container: 'AccountContainer', settings: Dict[str, Any], _: SharedContainer) -> None:
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
    def _cqrs_provider(container: 'AccountContainer', _: Dict[str, Any], shared: SharedContainer) -> None:
        # for handler in []:
        #     shared.event_bus.add_handler(handler)
        for handler in [
            # User
            RegisterUserCommandHandler(container.user_register_service),
            DeleteUserCommandHandler(container.user_deleter_service),
            ChangeUserPasswordCommandHandler(container.user_password_changer_service),
        ]:
            shared.command_bus.add_handler(handler)
        for handler in [
            # User
            GenerateTokenQueryHandler(container.token_generator_service),
            ReadUserAuthQueryHandler(container.jwt_token_factory),
            FindUserQueryHandler(container.user_finder_service),
        ]:
            shared.query_bus.add_handler(handler)

    @staticmethod
    def _http_middleware_provider(container: 'AccountContainer', _: Dict[str, Any], shared: SharedContainer) -> None:
        shared.http_app_auth_middleware = HttpAuthMiddleware(shared.logger, container.authenticator_service)

    @staticmethod
    def _http_controller_provider(container: 'AccountContainer', _: Dict[str, Any], shared: SharedContainer) -> None:
        validator = HTTPValidator()
        container.http_app_user_finder_get_controller = UserFinderGetController(
            shared.command_bus,
            shared.query_bus,
            validator,
        )
        container.http_app_user_register_put_controller = UserRegisterPutController(
            shared.command_bus,
            shared.query_bus,
            validator,
        )
        container.http_app_user_deleter_delete_controller = UserDeleterDeleteController(
            shared.command_bus,
            shared.query_bus,
            validator,
        )
        container.http_app_user_password_changer_post_controller = UserPasswordChangerPostController(
            shared.command_bus,
            shared.query_bus,
            validator,
        )
        container.http_app_user_auth_post_controller = UserAuthPostController(
            shared.command_bus,
            shared.query_bus,
            validator,
        )
        container.http_app_user_auth_get_controller = UserAuthGetController(
            shared.command_bus,
            shared.query_bus,
            validator,
        )

    @staticmethod
    def _cli_controller_provider(container: 'AccountContainer', _: Dict[str, Any], shared: SharedContainer) -> None:
        amqp_consumer = AMQPEventConsumer(
            shared.amqp_connection,
            shared.config_event_mappers.all(),
            container.amqp_graveyard_event_publisher
        )

        container.cli_app_consumer_on_internal_user_deleted_controller = ConsumerOnInternalUserDeletedController(
            InternalUserDeletedEventMapper(),
            shared.logger,
            amqp_consumer,
            shared.command_bus,
            shared.amqp_default_retries,
        )
