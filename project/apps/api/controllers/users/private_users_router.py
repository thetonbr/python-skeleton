from http import HTTPStatus

from aioddd import QueryBus
from fastapi import APIRouter, Depends

from project.apps.api.middleware.auth_handler import (
    UserAuth,
    auth_guard,
    get_current_user,
)
from project.apps.api.middleware.utils import get_current_asker
from project.libs.user.application.finder_service import UserFullFinderResponse
from project.libs.user.infrastructure.cqrs.find_user_query_handler import (
    FindFullUserQuery,
)

private_users = APIRouter()


@private_users.get(
    path='/{user_id}',
    response_model=UserFullFinderResponse,
    status_code=HTTPStatus.OK,
    summary='Find User',
)
async def find_user_get_controller(
    user_id: str,
    user_auth: UserAuth = Depends(get_current_user),
    asker: QueryBus = Depends(get_current_asker),
) -> UserFullFinderResponse:
    auth_guard(user_id=user_id, user_auth=user_auth)
    return await asker.ask(FindFullUserQuery(user_id=user_id))
