from unittest.mock import MagicMock, PropertyMock

import pytest
from aioddd import (
    BadRequestError,
    BaseError,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    UnknownError,
)
from aioddd.testing import sanitize_objects
from orjson import loads
from pydantic import BaseModel, ValidationError
from pydantic.error_wrappers import ErrorWrapper
from starlette.datastructures import URL
from starlette.exceptions import HTTPException

from project.apps.api.middleware.exception_handler import exception_handler


@pytest.mark.parametrize(
    'code,status,err',
    [
        ('unknown', 500, Exception()),
        ('unauthorized', 401, HTTPException(401)),
        ('not_found', 404, HTTPException(404)),
        ('invalid_request_validation', 400, ValidationError([ErrorWrapper(Exception(), '')], BaseModel)),
        ('code', 500, BaseError.create()),
        ('unauthorized', 401, UnauthorizedError.create()),
        ('not_found', 404, NotFoundError.create()),
        ('conflict', 409, ConflictError.create()),
        ('bad_request', 400, BadRequestError.create()),
        ('unknown', 500, UnknownError.create()),
    ],
)
def test_exception_handler(code: str, status: int, err: Exception) -> None:
    mock_request = MagicMock()
    type(mock_request).url = PropertyMock(return_value=URL('/'))
    res = exception_handler(mock_request, err, False)
    expected = {'code': code, 'status': str(status)}
    assert res.status_code == status
    actual = loads(res.body)
    assert 'errors' in actual and len(actual['errors']) == 1
    actual = sanitize_objects(expected, actual['errors'][0])
    assert actual == expected, f'"Actual: {actual}, Expected: {expected}'
