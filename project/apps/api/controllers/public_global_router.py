from http import HTTPStatus
from os import environ
from typing import Any

from aiodi import Container
from fastapi import APIRouter, Depends

from project.apps.api.middleware.utils import get_current_container

public_global = APIRouter()


@public_global.get(
    path='/',
    response_model=dict[str, Any],
    status_code=HTTPStatus.OK,
    summary='Root endpoint',
)
async def root_get_controller(di: Container = Depends(get_current_container)) -> dict[str, Any]:
    return {'app': di.get('env', typ=dict), 'server': environ} if di.get('env.debug') else {}
