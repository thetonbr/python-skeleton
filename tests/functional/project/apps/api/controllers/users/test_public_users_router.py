import pytest

from tests.functional.project.apps.api.context import APIContext
from tests.functional.project.libs.shared.user_context import UserContext
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
    UserPasswordMother,
)


@pytest.mark.asyncio
async def test_register_user_put_controller() -> None:
    async with APIContext() as ctx:
        await ctx.i_send_json_request(
            method='PUT',
            url='/api/public/users',
            data={
                'id': UserIdMother.random().value(),
                'email': UserEmailMother.random().value(),
                'password': UserPasswordMother.random().value(),
            },
        )
        await ctx.the_response_status_code_should_be(status_code=201)
        await ctx.the_response_content_should_be(data=None)


@pytest.mark.asyncio
async def test_token_auth_post_controller() -> None:
    async with APIContext() as ctx:
        cmd = {
            'id': UserIdMother.random().value(),
            'email': UserEmailMother.random().value(),
            'password': UserPasswordMother.random().value(),
        }
        await UserContext.an_existent_user_with(cmd=cmd)
        await ctx.i_send_x_www_form_urlencoded_request(
            method='POST',
            url='/api/public/users/auth',
            data={
                'grant_type': 'password',
                'username': cmd['email'],
                'password': cmd['password'],
            },
        )
        await ctx.the_response_status_code_should_be(status_code=200)
        await ctx.the_response_content_should_be_contains(
            data={
                'user_id': cmd['id'],
                'token_type': 'Bearer',
            }
        )


@pytest.mark.asyncio
async def test_forget_user_password_post_controller() -> None:
    async with APIContext() as ctx:
        cmd = {
            'id': UserIdMother.random().value(),
            'email': UserEmailMother.random().value(),
            'password': UserPasswordMother.random().value(),
        }
        await UserContext.an_existent_user_with(cmd=cmd)
        await ctx.i_send_json_request(
            method='POST',
            url='/api/public/users/forget-password',
            data={
                'email': cmd['email'],
            },
        )
        await ctx.the_response_status_code_should_be(status_code=200)
        await ctx.the_response_content_should_be(data=None)


@pytest.mark.asyncio
async def test_reset_user_password_post_controller() -> None:
    async with APIContext() as ctx:
        cmd = {
            'id': UserIdMother.random().value(),
            'email': UserEmailMother.random().value(),
            'password': UserPasswordMother.random().value(),
        }
        ctx.token = await UserContext.an_existent_authenticated_user_with(cmd=cmd)
        await UserContext.forget_user_password_with_email(cmd['email'])
        full_user = await UserContext.find_full_user_with_id(cmd['id'])
        await ctx.i_send_json_request(
            method='POST',
            url='/api/public/users/reset-password',
            data={
                'email': cmd['email'],
                'refresh_token': full_user.refresh_token,
                'new_password': UserPasswordMother.random().value(),
            },
        )
        await ctx.the_response_status_code_should_be(status_code=200)
        await ctx.the_response_content_should_be(data=None)
