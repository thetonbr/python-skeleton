from aioddd import CommandBus, Container, EventBus, QueryBus
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from project.apps.settings import container
from project.libs.user.application.authenticator_service import AuthenticatorService
from project.libs.user.application.finder_service import (
    UserFinderResponse,
    UserFinderService,
)
from project.libs.user.domain.errors import UserUnauthorizedError
from project.libs.user.domain.properties import UserId


def get_current_container() -> Container:
    return container()


def get_current_dispatcher(di: Container = Depends(get_current_container)) -> CommandBus:
    return di.get(CommandBus)


def get_current_asker(di: Container = Depends(get_current_container)) -> QueryBus:
    return di.get(QueryBus)


def get_current_notifier(di: Container = Depends(get_current_container)) -> EventBus:
    return di.get(EventBus)


UserAuth = UserFinderResponse


async def get_current_user(
    di: Container = Depends(get_current_container),
    token: str = Depends(OAuth2PasswordBearer(tokenUrl='/api/public/users/auth')),
) -> UserAuth:
    user_id = (await di.get(AuthenticatorService)(token)).user_id
    return await di.get(UserFinderService)(UserId(user_id))


def auth_guard(user_id: str, user_auth: UserAuth) -> None:
    if user_auth.id != user_id:
        raise UserUnauthorizedError.create(detail={'user_auth_id': user_auth.id, 'user_id': user_id})
