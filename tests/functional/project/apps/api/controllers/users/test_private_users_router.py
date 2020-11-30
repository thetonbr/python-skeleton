import pytest

from tests.functional.project.apps.api.context import APIContext
from tests.functional.project.libs.shared.user_context import UserContext
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
)


@pytest.mark.asyncio
async def test_find_user_get_controller() -> None:
    async with APIContext() as ctx:
        cmd = {
            'id': UserIdMother.random().value(),
            'email': UserEmailMother.random().value(),
        }
        ctx.token = await UserContext.an_existent_authenticated_user_with(cmd=cmd)
        await UserContext.forget_user_password_with_email(cmd['email'])
        await ctx.i_send_json_request(method='GET', url=f"/api/private/users/{cmd['id']}")
        await ctx.the_response_status_code_should_be(status_code=200)
        await ctx.the_response_content_should_be_contains(data=cmd)
