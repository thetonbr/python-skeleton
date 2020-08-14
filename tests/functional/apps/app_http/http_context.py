from json import loads

from aiohttp.test_utils import TestClient, TestServer
from behave import step  # pylint: disable=E0611
from behave.api.async_step import async_run_until_complete
from behave.model import Scenario
from behave.runner import Context

from src.apps.app_http.__main__ import HttpApp
from tests.functional import TEST_LOOP
from tests.functional.apps.context_amqp_middleware import ContextAMQPMiddleware
from tests.functional.apps.context_mongodb_middleware import ContextMongoDBMiddleware
from tests.functional.apps.utils import sanitize_objects


def before_all(ctx: Context) -> None:
    ctx.http_app = HttpApp(TEST_LOOP)


@async_run_until_complete(loop=TEST_LOOP)
async def before_scenario(ctx: Context, sce: Scenario) -> None:
    app = await ctx.http_app.__aenter__()
    app.on_shutdown.clear()
    ctx.container = ctx.http_app.container
    ctx.http_response = None
    await ContextMongoDBMiddleware.before_scenario(ctx, sce)
    await ContextAMQPMiddleware.before_scenario(ctx, sce)
    ctx.http_server = TestServer(app)
    ctx.http_client = TestClient(ctx.http_server)
    await ctx.http_server.start_server()


class ContextHTTP:
    @staticmethod
    @step('I send JSON "{method}" request to "{uri}"')
    @async_run_until_complete(loop=TEST_LOOP)
    async def i_send_json_request_to(context: Context, method: str, uri: str) -> None:
        client: TestClient = context.http_client
        context.http_response = await client.request(method=method, path=uri, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': context.token if 'token' in context else ''
        })

    @staticmethod
    @step('I send JSON "{method}" request to "{uri}" with body')
    @async_run_until_complete(loop=TEST_LOOP)
    async def i_send_json_request_to_body(context: Context, method: str, uri: str) -> None:
        client: TestClient = context.http_client
        context.http_response = await client.request(method=method, path=uri, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': context.token if 'token' in context else ''
        }, data=context.text)

    @staticmethod
    @step('the response status code should be "{status_code}"')
    @async_run_until_complete(loop=TEST_LOOP)
    async def the_response_status_code_should_be(context: Context, status_code: str) -> None:
        actual = context.http_response.status
        expected = int(status_code)
        if expected != actual:
            raise AssertionError(
                f'Expected: {expected}',
                f'Actual: {actual}',
                f'Content: {await context.http_response.json()}'
            )

    @staticmethod
    @step('the response content should be')
    @async_run_until_complete(loop=TEST_LOOP)
    async def the_response_content_should_be(context: Context) -> None:
        actual = await context.http_response.json()
        expected = loads(context.text)
        if expected != actual:
            raise AssertionError(f"""
                Expected: {expected}
                Actual: {actual}
            """)

    @staticmethod
    @step('the response content should be contains')
    @async_run_until_complete(loop=TEST_LOOP)
    async def the_response_content_should_be_contains(context: Context) -> None:
        actual = await context.http_response.json()
        expected = loads(context.text)
        actual = sanitize_objects(expected, actual)
        if expected != actual:
            raise AssertionError(f'Expected: {expected}', f'Actual: {actual}')


@async_run_until_complete(loop=TEST_LOOP)
async def after_scenario(ctx: Context, sce: Scenario) -> None:
    await ContextAMQPMiddleware.after_scenario(ctx, sce)
    await ContextMongoDBMiddleware.after_scenario(ctx, sce)
    await ctx.http_server.close()
