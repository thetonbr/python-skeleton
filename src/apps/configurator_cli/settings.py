from os import getenv
from typing import Optional


def _get_env(key: str, default: Optional[str] = None) -> str:
    """Get an environment variable, return default if it is empty or doesn't exist."""
    value = getenv(key, default)
    return str(default) if not value or len(value) == 0 else value


ENVIRONMENT = _get_env('ENVIRONMENT', 'production')
LIVE_RELOAD = _get_env('LIVE_RELOAD', '0')

DEBUG = _get_env('DEBUG', '0')
DEBUG_HOST = _get_env('DEBUG_PORT', '0.0.0.0')
DEBUG_PORT = _get_env('DEBUG_PORT', '5678')

HTTP_HOST = _get_env('HTTP_HOST', '0.0.0.0')
HTTP_PORT = _get_env('HTTP_PORT', '80')

MONGODB_USERNAME = _get_env('MONGODB_ROOT_USERNAME', 'admin')
MONGODB_PASSWORD = _get_env('MONGODB_ROOT_PASSWORD', 'admin')
MONGODB_HOST = _get_env('MONGODB_HOST', '0.0.0.0')
MONGODB_PORT = _get_env('MONGODB_PORT', '27017')
MONGODB_ROOT_DATABASE = _get_env('MONGODB_ROOT_DATABASE', 'admin')

RABBITMQ_USER = _get_env('RABBITMQ_ROOT_USER', 'guest')
RABBITMQ_PASSWORD = _get_env('RABBITMQ_ROOT_PASSWORD', 'guest')
RABBITMQ_HOST = _get_env('RABBITMQ_HOST', '0.0.0.0')
RABBITMQ_PORT = _get_env('RABBITMQ_PORT', '5672')
RABBITMQ_VHOST = _get_env('RABBITMQ_ROOT_VHOST', 'example')
