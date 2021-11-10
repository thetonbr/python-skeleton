from aiodi import Container
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from project.apps.api.middleware.utils import get_current_container
from project.libs.user.application.authenticator_service import AuthenticatorService
from project.libs.user.application.finder_service import (
    UserFinderResponse,
    UserFinderService,
)
from project.libs.user.domain.errors import UserUnauthorizedError
from project.libs.user.domain.properties import UserId

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
