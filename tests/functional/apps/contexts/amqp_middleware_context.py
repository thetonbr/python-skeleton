from asyncio import sleep
from os import getenv
from typing import final

from behave.model import Scenario
from behave.runner import Context
from requests import get


@final
class ContextAMQPMiddleware:
    @staticmethod
    async def before_scenario(_: Context, __: Scenario) -> None:
        await sleep(0.01)
        _execute_amqp_query('setup')

    @staticmethod
    async def after_scenario(_: Context, __: Scenario) -> None:
        await sleep(0.01)
        _execute_amqp_query('clean')


def _execute_amqp_query(action: str) -> None:
    res = get('http://{0}:{1}/api/cnf/protected/amqp-{2}'.format(
        getenv('CNF_HOST'),
        getenv('CNF_PORT'),
        action,
    ))
    if res.status_code != 200:
        raise AssertionError('Expected: 200', 'Actual: {0}'.format(res.status_code))
