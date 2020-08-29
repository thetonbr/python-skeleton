from os import getenv
from typing import Optional


def _get_env(key: str, default: Optional[str] = None) -> str:
    """Get an environment variable, return default if it is empty or doesn't exist."""
    value = getenv(key, default)
    return str(default) if not value or len(value) == 0 else value


ENVIRONMENT = _get_env('ENVIRONMENT', 'production')
OAUTH_SECRET = _get_env('OAUTH_SECRET', 'secret')
OAUTH_EXPIRATION_DAYS = _get_env('OAUTH_EXPIRATION_DAYS', '14')
LIVE_RELOAD = _get_env('LIVE_RELOAD', '0')
ENABLE_EVENT_HANDLERS = _get_env('ENABLE_EVENT_HANDLERS', '1')

DEBUG = _get_env('DEBUG', '0')
DEBUG_HOST = _get_env('DEBUG_HOST', '0.0.0.0')
DEBUG_PORT = _get_env('DEBUG_PORT', '5678')

HTTP_HOST = _get_env('APP_HOST', '0.0.0.0')
HTTP_PORT = _get_env('APP_PORT', '80')

MONGODB_USERNAME = _get_env('MONGODB_USERNAME', 'admin')
MONGODB_PASSWORD = _get_env('MONGODB_PASSWORD', 'secret')
MONGODB_HOST = _get_env('MONGODB_HOST', '0.0.0.0')
MONGODB_PORT = _get_env('MONGODB_PORT', '27017')
MONGODB_DATABASE = _get_env('MONGODB_DATABASE', 'example')
MONGODB_ROOT_DATABASE = _get_env('MONGODB_ROOT_DATABASE', 'admin')

MONGODB_DATABASE_ACCOUNT = _get_env('MONGODB_DATABASE_ACCOUNT', 'example_account')

RABBITMQ_USER = _get_env('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = _get_env('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_HOST = _get_env('RABBITMQ_HOST', '0.0.0.0')
RABBITMQ_PORT = _get_env('RABBITMQ_PORT', '5672')
RABBITMQ_VHOST = _get_env('RABBITMQ_VHOST', 'example')
RABBITMQ_EXCHANGE = _get_env('RABBITMQ_EXCHANGE', 'example')

RABBITMQ_EXCHANGE_ACCOUNT = _get_env('RABBITMQ_EXCHANGE_ACCOUNT', 'example.account')
