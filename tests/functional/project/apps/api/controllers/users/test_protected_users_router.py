import pytest

from tests.functional.project.apps.api.context import APIContext
from tests.functional.project.libs.shared.user_context import UserContext
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
    UserPasswordMother,
)


@pytest.mark.asyncio
async def test_me_get_controller() -> None:
    async with APIContext() as ctx:
        cmd = {
            'id': UserIdMother.random().value(),
            'email': UserEmailMother.random().value(),
        }
        ctx.token = await UserContext.an_existent_authenticated_user_with(cmd=cmd)
        await ctx.i_send_json_request(method='GET', url='/api/protected/users/me')
        await ctx.the_response_status_code_should_be(status_code=200)
        await ctx.the_response_content_should_be_contains(data=cmd)


@pytest.mark.asyncio
async def test_change_user_password_post_controller() -> None:
    async with APIContext() as ctx:
        cmd = {
            'id': UserIdMother.random().value(),
            'email': UserEmailMother.random().value(),
            'password': UserPasswordMother.random().value(),
        }
        ctx.token = await UserContext.an_existent_authenticated_user_with(cmd=cmd)
        await ctx.i_send_json_request(
            method='POST',
            url='/api/protected/users/change-password',
            data={
                'id': cmd['id'],
                'old_password': cmd['password'],
                'new_password': UserPasswordMother.random().value(),
            },
        )
        await ctx.the_response_status_code_should_be(status_code=200)
        await ctx.the_response_content_should_be(data=None)


@pytest.mark.asyncio
async def test_delete_user_delete_controller() -> None:
    async with APIContext() as ctx:
        cmd = {
            'id': UserIdMother.random().value(),
        }
        ctx.token = await UserContext.an_existent_user_with_id(user_id=cmd["id"])
        await ctx.i_send_json_request(method='DELETE', url=f'/api/protected/users/{cmd["id"]}')
        await ctx.the_response_status_code_should_be(status_code=200)
        await ctx.the_response_content_should_be(data=None)


@pytest.mark.asyncio
async def test_find_user_get_controller() -> None:
    async with APIContext() as ctx:
        cmd = {
            'id': UserIdMother.random().value(),
            'email': UserEmailMother.random().value(),
        }
        ctx.token = await UserContext.an_existent_authenticated_user_with(cmd=cmd)
        await ctx.i_send_json_request(method='GET', url=f'/api/protected/users/{cmd["id"]}')
        await ctx.the_response_status_code_should_be(status_code=200)
        await ctx.the_response_content_should_be(data=cmd)
