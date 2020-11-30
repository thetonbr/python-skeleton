from http import HTTPStatus

from aioddd import CommandBus, QueryBus
from fastapi import APIRouter, Depends

from project.apps.api.middleware.auth_handler import (
    UserAuth,
    auth_guard,
    get_current_asker,
    get_current_dispatcher,
    get_current_user,
)
from project.libs.user.application.finder_service import UserFinderResponse
from project.libs.user.infrastructure.cqrs.change_user_password_command_handler import (
    ChangeUserPasswordCommand,
)
from project.libs.user.infrastructure.cqrs.delete_user_command_handler import (
    DeleteUserCommand,
)
from project.libs.user.infrastructure.cqrs.find_user_query_handler import FindUserQuery

protected_users = APIRouter()


@protected_users.get(
    path='/me',
    response_model=UserAuth,
    status_code=HTTPStatus.OK,
    summary='Me',
)
async def me_get_controller(user_auth: UserAuth = Depends(get_current_user)) -> UserAuth:
    return user_auth


@protected_users.post(
    path='/change-password',
    status_code=HTTPStatus.OK,
    summary='Change password',
)
async def change_user_password_post_controller(
    command: ChangeUserPasswordCommand,
    user_auth: UserAuth = Depends(get_current_user),
    dispatcher: CommandBus = Depends(get_current_dispatcher),
) -> None:
    auth_guard(user_id=command.user_id, user_auth=user_auth)
    await dispatcher.dispatch(command)


@protected_users.delete(
    path='/{user_id}',
    status_code=HTTPStatus.OK,
    summary='Delete User',
)
async def delete_user_delete_controller(
    user_id: str,
    user_auth: UserAuth = Depends(get_current_user),
    dispatcher: CommandBus = Depends(get_current_dispatcher),
) -> None:
    auth_guard(user_id=user_id, user_auth=user_auth)
    await dispatcher.dispatch(DeleteUserCommand(user_id=user_id))


@protected_users.get(
    path='/{user_id}',
    response_model=UserFinderResponse,
    status_code=HTTPStatus.OK,
    summary='Find User',
)
async def find_user_get_controller(
    user_id: str,
    user_auth: UserAuth = Depends(get_current_user),
    asker: QueryBus = Depends(get_current_asker),
) -> UserFinderResponse:
    auth_guard(user_id=user_id, user_auth=user_auth)
    return await asker.ask(FindUserQuery(user_id=user_id))
