from asyncio import AbstractEventLoop, get_event_loop_policy

from pytest import fixture

from project.apps.settings import env
from project.libs.shared.infrastructure.mongodb_connection import MongoDBConnection
from tests.unit.project.libs.shared.infrastructure.tests.faker import FAKE


@fixture(scope='session')
def event_loop() -> AbstractEventLoop:
    return get_event_loop_policy().new_event_loop()


@fixture(scope='session')
async def mongodb_disposable_connection() -> MongoDBConnection:
    connection = MongoDBConnection(
        uri_connection='mongodb://'
        f'{env("mongodb_username", typ=str)}:{env("mongodb_password", typ=str)}@'
        f'{env("mongodb_host", typ=str)}:{env("mongodb_port", typ=int)}/'
        f'{env("mongodb_root_database", typ=str)}',
        database_name=f'project_{FAKE.md5()}',
    )
    yield connection
    await connection.drop_database()
