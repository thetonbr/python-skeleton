from json import loads

from aiocli.test_utils import TestCommander, TestClient
from aioddd import find_event_mapper_by_name
from behave import step  # pylint: disable=E0611
from behave.api.async_step import async_run_until_complete
from behave.model import Scenario
from behave.runner import Context

from src.apps.app_cli.__main__ import CliApp
from tests.functional import TEST_LOOP, BEFORE_SCENARIO_SETUP, AFTER_SCENARIO_CLEAN
from tests.functional.apps.contexts.amqp_middleware_context import ContextAMQPMiddleware
from tests.functional.apps.contexts.mongodb_middleware_context import ContextMongoDBMiddleware


def before_all(ctx: Context) -> None:
    ctx.cli_app = CliApp(TEST_LOOP)


@async_run_until_complete(loop=TEST_LOOP)
async def before_scenario(ctx: Context, sce: Scenario) -> None:
    app = await ctx.cli_app.__aenter__()
    ctx.container = ctx.cli_app.container
    ctx.exit_code = None
    if BEFORE_SCENARIO_SETUP == "1":
        await ContextMongoDBMiddleware.before_scenario(ctx, sce)
        await ContextAMQPMiddleware.before_scenario(ctx, sce)
    ctx.cli_commander = TestCommander(app, loop=TEST_LOOP)
    ctx.cli_client = TestClient(ctx.cli_commander)
    await ctx.cli_commander.start_commander()


class ContextCLI:
    @staticmethod
    @step('I execute the "{command_args}" command for "{seconds}" seconds')
    @async_run_until_complete(loop=TEST_LOOP)
    async def i_execute_the_command(ctx: Context, command_args: str, seconds: str) -> None:
        ctx.exit_code = await ctx.cli_client.handle(
            command_args.split(' '),
            timeout=float(seconds),
            timeout_exit_code=1,
        )

    @staticmethod
    @step('the exit code should be "{exit_code}"')
    def the_exit_status_code_should_be(ctx: Context, exit_code: str) -> None:
        actual = ctx.exit_code
        expected = int(exit_code)
        if expected != actual:
            raise AssertionError(f'Expected: {expected}', f'Actual: {actual}')

    @staticmethod
    @step('an existent published event with')
    @async_run_until_complete(loop=TEST_LOOP)
    async def an_existent_published_event_with(ctx: Context) -> None:
        body = loads(ctx.text)
        mapper = find_event_mapper_by_name(body['meta']['message'], ctx.container.shared.config_event_mappers.all())
        event = mapper.decode(body['attributes'])
        await ctx.container.shared.event_publisher.publish([event])


@async_run_until_complete(loop=TEST_LOOP)
async def after_scenario(ctx: Context, sce: Scenario) -> None:
    if AFTER_SCENARIO_CLEAN == "1":
        await ContextAMQPMiddleware.after_scenario(ctx, sce)
        await ContextMongoDBMiddleware.after_scenario(ctx, sce)
    await ctx.cli_commander.close()
