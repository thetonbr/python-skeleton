from http import HTTPStatus
from typing import Any, Dict

from aioddd import Container
from fastapi import APIRouter, Depends

from project.apps.api.middleware.auth_handler import get_current_container

public_global = APIRouter()


@public_global.get(
    path='/',
    response_model=Dict[str, Any],
    status_code=HTTPStatus.OK,
    summary='Root endpoint',
)
async def root_get_controller(di: Container = Depends(get_current_container)) -> Dict[str, Any]:
    return {} if di.get('env.environment', typ=str) == 'production' else di.get('env', typ=dict)
