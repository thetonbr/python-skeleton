# pylint: skip-file
from datetime import datetime
from functools import lru_cache
from logging import Logger
from typing import Dict, Optional, Type, TypeVar, Union, cast

from aioddd import (
    CommandBus,
    CommandHandler,
    EventBus,
    EventHandler,
    EventMapper,
    EventPublisher,
    EventPublishers,
    InternalEventPublisher,
    QueryBus,
    QueryHandler,
    SimpleCommandBus,
    SimpleEventBus,
    SimpleQueryBus,
    get_env,
    get_simple_logger,
)
from aiodi import Container

from project.libs.shared.infrastructure.event_handlers.user.notify_user_registered_on_user_registered_event_handler import (
    NotifyUserRegisteredOnUserRegisteredEventHandler,
)
from project.libs.shared.infrastructure.mongodb_connection import MongoDBConnection
from project.libs.shared.infrastructure.mongodb_event_publisher import (
    MongoDBEventPublisher,
    MongoDBEventPublisherMapper,
)
from project.libs.user.application.authenticator_service import AuthenticatorService
from project.libs.user.application.deleter_service import UserDeleterService
from project.libs.user.application.finder_service import (
    UserFinderService,
    UserFullFinderService,
)
from project.libs.user.application.notifier_service import UserRegisteredNotifierService
from project.libs.user.application.password_changer_service import (
    UserPasswordChangerService,
)
from project.libs.user.application.password_forget_service import (
    UserPasswordForgetService,
)
from project.libs.user.application.password_resetter_service import (
    UserPasswordResetterService,
)
from project.libs.user.application.register_service import UserRegisterService
from project.libs.user.application.token_generator_service import TokenGeneratorService
from project.libs.user.domain.repositories import (
    AuthRepository,
    TokenFactory,
    UserNotifier,
    UserRepository,
)
from project.libs.user.infrastructure.cqrs.change_user_password_command_handler import (
    ChangeUserPasswordCommandHandler,
)
from project.libs.user.infrastructure.cqrs.delete_user_command_handler import (
    DeleteUserCommandHandler,
)
from project.libs.user.infrastructure.cqrs.find_user_query_handler import (
    FindFullUserQueryHandler,
    FindUserQueryHandler,
)
from project.libs.user.infrastructure.cqrs.forget_user_password_command_handler import (
    ForgetUserPasswordCommandHandler,
)
from project.libs.user.infrastructure.cqrs.generate_token_query_handler import (
    GenerateTokenQueryHandler,
)
from project.libs.user.infrastructure.cqrs.notify_user_registered_command_handler import (
    NotifyUserRegisteredCommandHandler,
)
from project.libs.user.infrastructure.cqrs.register_user_command_handler import (
    RegisterUserCommandHandler,
)
from project.libs.user.infrastructure.cqrs.reset_user_password_command_handler import (
    ResetUserPasswordCommandHandler,
)
from project.libs.user.infrastructure.email_user_notifier import (
    EmailConfig,
    EmailUserNotifier,
)
from project.libs.user.infrastructure.event_mappers import (
    UserDeletedEventMapper,
    UserPasswordChangedEventMapper,
    UserPasswordForgottenEventMapper,
    UserPasswordResettedEventMapper,
    UserRegisteredEventMapper,
    UserRegisteredNotifiedEventMapper,
)
from project.libs.user.infrastructure.jwt_token_factory import JWTTokenFactory
from project.libs.user.infrastructure.mongodb_auth_repository import (
    MongoDBAuthRepository,
)
from project.libs.user.infrastructure.mongodb_user_repository import (
    MongoDBUserRepository,
)

_T = TypeVar('_T')
_ENV: Optional[Dict[str, Union[str, int, bool]]] = None
_CONTAINER: Optional[Container] = None


@lru_cache()
def env(key: Optional[str] = None, typ: Optional[Type[_T]] = None) -> _T:
    global _ENV
    if not _ENV:
        _ENV = {
            'name': 'project',
            'debug': bool(int(get_env(key='DEBUG', default='0'))),
            'environment': get_env(key='ENVIRONMENT', default='production'),
            'version': get_env(key='VERSION', default='latest'),
            'tz': get_env(key='TZ', default='UTC'),
            'log_level': get_env(key='LOG_LEVEL', default='INFO'),
            'oauth_secret': get_env(key='OAUTH_SECRET', default='secret'),
            'oauth_expiration_days': int(get_env(key='OAUTH_EXPIRATION_DAYS', default='14')),
            'http_host': get_env(key='HTTP_HOST', default='0.0.0.0'),
            'http_port': int(get_env(key='HTTP_PORT', default='8000')),
            'mongodb_protocol': get_env(key='MONGODB_PROTOCOL', default='mongodb'),
            'mongodb_root_database': get_env(key='MONGODB_ROOT_DATABASE', default='admin'),
            'mongodb_username': get_env(key='MONGODB_USERNAME', default='admin'),
            'mongodb_password': get_env(key='MONGODB_PASSWORD', default='secret'),
            'mongodb_database': get_env(key='MONGODB_DATABASE', default='project'),
            'mongodb_host': get_env(key='MONGODB_HOST', default='mongodb'),
            'mongodb_port': int(get_env(key='MONGODB_PORT', default='27017')),
            'email_host': get_env(key='EMAIL_HOST', default='mailhog'),
            'email_port': int(get_env(key='EMAIL_PORT', default='2525')),
            'email_host_user': get_env(key='EMAIL_HOST_USER', default=''),
            'email_host_password': get_env(key='EMAIL_HOST_PASSWORD', default=''),
            'email_use_tls': bool(int(get_env(key='EMAIL_USE_TLS', default='0'))),
            'email_from': get_env(key='EMAIL_FROM', default='local@project.com'),
            'email_ui_port': int(get_env(key='EMAIL_UI_PORT', default='8025')),
            'openapi_url': get_env(key='OPENAPI_URL', default='/openapi.json'),
            'openapi_prefix': get_env(key='OPENAPI_PREFIX', default=''),
        }
    if not key:
        return _ENV  # type: ignore
    if key not in _ENV:  # pragma: no cover
        raise KeyError(f'<{key}{f": {typ.__name__}" if typ else ""}> does not exist as environment variable')
    val = _ENV[key]
    if typ and not isinstance(val, (typ,)):  # pragma: no cover
        raise TypeError(f'<{key}{f": {typ.__name__}" if typ else ""}> does not exist as environment variable')
    return val  # type: ignore


def container(reset: bool = False) -> Container:
    global _CONTAINER
    if _CONTAINER and not reset:
        return _CONTAINER
    di = Container({'env': env(key=None, typ=dict)})
    di.resolve(
        [
            (
                Logger,
                get_simple_logger,
                {
                    'name': di.resolve_parameter(
                        lambda di_: f"{di_.get('env.name', typ=str)}:{di_.get('env.version', typ=str)}"
                    ),
                    'level': di.resolve_parameter(lambda di_: di_.get('env.log_level', typ=str)),
                },
            ),
            (
                MongoDBConnection,
                MongoDBConnection,
                {
                    'uri_connection': di.resolve_parameter(
                        lambda di_: "{}://{}:{}@{}{}/{}".format(
                            di_.get("env.mongodb_protocol", typ=str),
                            di_.get("env.mongodb_username", typ=str),
                            di_.get("env.mongodb_password", typ=str),
                            di_.get("env.mongodb_host", typ=str),
                            (
                                f':{di_.get("env.mongodb_port", typ=int)}'
                                if di_.get("env.mongodb_protocol", typ=str) == "mongodb"
                                else ''
                            ),
                            di_.get("env.mongodb_root_database", typ=str),
                        )
                    ),
                    'database_name': di.resolve_parameter(lambda di_: di_.get('env.mongodb_database', typ=str)),
                },
            ),
            # Transporters #
            (EventPublisher, EventPublishers(publishers=[])),
            (CommandBus, SimpleCommandBus(handlers=[])),
            (QueryBus, SimpleQueryBus(handlers=[])),
            (EventBus, SimpleEventBus(handlers=[])),
            (
                TokenFactory,
                JWTTokenFactory,
                {
                    'now': di.resolve_parameter(lambda _: lambda: datetime.utcnow()),
                    'secret': di.resolve_parameter(lambda di_: di_.get('env.oauth_secret', typ=str)),
                },
            ),
            # Notifiers #
            (
                UserNotifier,
                EmailUserNotifier,
                {
                    'config': di.resolve_parameter(
                        lambda di_: EmailConfig(
                            host=di_.get('env.email_host', typ=str),
                            port=di_.get('env.email_port', typ=int),
                            host_user=di_.get('env.email_host_user', typ=str),
                            host_password=di_.get('env.email_host_password', typ=str),
                            use_tls=di_.get('env.email_use_tls', typ=bool),
                            from_user=di_.get('env.email_from', typ=str),
                        )
                    ),
                },
            ),
            # Repositories #
            (AuthRepository, MongoDBAuthRepository),
            (UserRepository, MongoDBUserRepository),
            # Services #
            (
                TokenGeneratorService,
                TokenGeneratorService,
                {
                    'expiration_days': di.resolve_parameter(lambda di_: di_.get('env.oauth_expiration_days', typ=int)),
                    'token_type': 'Bearer',
                },
            ),
            # User
            AuthenticatorService,
            UserFinderService,
            UserFullFinderService,
            UserRegisterService,
            UserDeleterService,
            UserPasswordChangerService,
            UserPasswordResetterService,
            UserPasswordForgetService,
            UserRegisteredNotifierService,
            # CommandHandlers #
            # User
            RegisterUserCommandHandler,
            DeleteUserCommandHandler,
            ChangeUserPasswordCommandHandler,
            ForgetUserPasswordCommandHandler,
            ResetUserPasswordCommandHandler,
            NotifyUserRegisteredCommandHandler,
            # QueryHandlers #
            # User
            GenerateTokenQueryHandler,
            FindUserQueryHandler,
            FindFullUserQueryHandler,
            # EventHandlers #
            # User #
            NotifyUserRegisteredOnUserRegisteredEventHandler,
            # EventMappers #
            # User
            UserRegisteredEventMapper,
            UserDeletedEventMapper,
            UserPasswordChangedEventMapper,
            UserPasswordForgottenEventMapper,
            UserPasswordResettedEventMapper,
            UserRegisteredNotifiedEventMapper,
        ]
    )
    cast(SimpleCommandBus, di.get(CommandBus)).add_handler(handler=di.get(CommandHandler, instance_of=True))
    cast(SimpleQueryBus, di.get(QueryBus)).add_handler(handler=di.get(QueryHandler, instance_of=True))
    cast(SimpleEventBus, di.get(EventBus)).add_handler(handler=di.get(EventHandler, instance_of=True))
    cast(EventPublishers, di.get(EventPublisher)).add(
        publishers=[
            MongoDBEventPublisher(
                connection=di.get(MongoDBConnection),
                mapper=MongoDBEventPublisherMapper(mappers=di.get(EventMapper, instance_of=True)),
            ),
            InternalEventPublisher(
                event_bus=di.get(EventBus),
            ),
        ]
    )

    # services
    def shutdown() -> None:
        di.get(MongoDBConnection).close()  # pragma: no cover

    di.set('services.shutdown', val=shutdown)
    # assign and return
    _CONTAINER = di
    return di
