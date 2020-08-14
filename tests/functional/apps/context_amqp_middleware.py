from asyncio import sleep
from os import getenv

from behave.model import Scenario
from behave.runner import Context
from requests import get


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
    res = get('http://{0}/api/service-configurator/protected/amqp-{1}?amqp-exchange={2}'.format(
        getenv('SERVICE_CONFIGURATOR_HOST'),
        action,
        getenv('RABBITMQ_EXCHANGE')
    ))
    if res.status_code != 200:
        raise AssertionError('Expected: 200', f'Actual: {res.status_code}')
