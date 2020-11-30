import pytest

from tests.functional.project.apps.cli.context import CLIContext


@pytest.mark.asyncio
async def test_print_envs_command_handler() -> None:
    async with CLIContext() as ctx:
        await ctx.i_execute_the_command(args='print-envs', timeout_seconds=1)
        await ctx.the_exit_status_code_should_be(exit_code=0)
