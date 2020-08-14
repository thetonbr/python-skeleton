from abc import ABC, abstractmethod
from datetime import date, datetime
from json import loads
from typing import Dict, Union, List, Any, Optional, final, Type, Iterable, Mapping
from uuid import UUID

from aioddd import CommandBus, QueryBus, Command, Query
from aiohttp.web import Request, Response as WebResponse, json_response, HTTPForbidden
from marshmallow import post_load
from marshmallow_jsonapi import Schema as JSONAPISchema, fields


@final
class HTTPValidator:
    @staticmethod
    def validate(
            schema: JSONAPISchema,
            data: Union[Mapping[str, Any], Iterable[Mapping[str, Any]]],
            *,
            type_: Optional[str] = None,
            type_class: Optional[Type[Any]] = None,
            to_primitives: bool = True,
    ) -> Any:
        if type_ is not None:
            schema.opts.type_ = type_  # Schema.Meta.type_
        schema.__dict__.setdefault('_to_primitives', to_primitives)
        result = schema.load(data)
        if type_class is not None:
            result = type_class(**result)
        return result


def _list_to_primitives(data: List[Any], **kwargs: Dict[Any, Any]) -> List[Any]:
    _data = data.copy()
    for i, value in enumerate(_data):
        if isinstance(value, dict):
            _data[i] = _dict_to_primitives(data=value, kwargs=kwargs)
        elif isinstance(value, (UUID, date, datetime)):
            _data[i] = value.__str__()
        elif isinstance(value, list):
            _data[i] = _list_to_primitives(data=value, kwargs=kwargs)
    return _data


def _dict_to_primitives(data: Dict[Any, Any], **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
    _data = data.copy()
    for key, value in _data.items():
        if isinstance(value, list):
            _data[key] = _list_to_primitives(data=value, kwargs=kwargs)
        elif isinstance(value, (UUID, date, datetime)):
            _data[key] = value.__str__()
        elif isinstance(value, dict):
            _data[key] = _dict_to_primitives(data=value, kwargs=kwargs)
    return _data


def _to_primitives(
        data: Union[Dict[Any, Any], List[Dict[Any, Any]]],
        **kwargs: Dict[Any, Any]
) -> Union[Dict[Any, Any], List[Dict[Any, Any]]]:
    return _list_to_primitives(data=data, kwargs=kwargs) \
        if isinstance(data, list) else _dict_to_primitives(data=data, kwargs=kwargs)


class Controller(ABC):
    __slots__ = ('_command_bus', '_query_bus', '_validator')

    class _Schema(JSONAPISchema):
        document_meta = fields.DocumentMeta(required=False)

        class Meta:
            strict = True
            type_ = 'unknown'

        @post_load
        def _post_load(
                self,
                data: Union[Dict[Any, Any], List[Dict[Any, Any]]],
                **kwargs: Dict[Any, Any]
        ) -> Union[Dict[Any, Any], List[Dict[Any, Any]], Any]:
            if self.__dict__.get('_to_primitives', False):
                return _to_primitives(data=data, kwargs=kwargs)
            return data

    class RequestSchema(_Schema):
        pass

    class ResponseSchema(_Schema):
        pass

    def __init__(self, command_bus: CommandBus, query_bus: QueryBus, validator: HTTPValidator) -> None:
        self._command_bus = command_bus
        self._query_bus = query_bus
        self._validator = validator

    @abstractmethod
    async def __call__(self, request: Request) -> WebResponse:
        pass

    async def _dispatch(self, command: Command) -> None:
        await self._command_bus.dispatch(command)

    async def _ask(self, query: Query) -> Any:
        return await self._query_bus.ask(query)

    async def _validate(
            self,
            req: Union[Request, Mapping[str, Any], Iterable[Mapping[str, Any]]],
            *,
            type_: Optional[str] = None,
            type_class: Optional[Type[Any]] = None,
            to_primitives: bool = True,
    ) -> Any:
        return self._validator.validate(
            schema=self.RequestSchema(),
            data=await req.json() if isinstance(req, Request) else req,
            type_=type_,
            type_class=type_class,
            to_primitives=to_primitives
        )

    @staticmethod
    async def _auth_guard(request: Request, user_id: Optional[str]) -> None:
        user_auth = loads(request.get('user_auth') or '{"user_id": null}')
        if user_auth['user_id'] != user_id:
            raise HTTPForbidden()

    def _response(
            self,
            status_code: int,
            data: Dict[Any, Any],
            type_: Optional[str] = None,
    ) -> WebResponse:
        data.setdefault('meta', {})
        if 'data' in data:
            if isinstance(data['data'], dict):
                data['data'].setdefault('type', type_)
                self._validator.validate(
                    schema=self.ResponseSchema(),
                    data=data,
                    type_=type_,
                    type_class=None,
                    to_primitives=False
                )
            elif isinstance(data['data'], list):
                for i, item in enumerate(data['data']):
                    if 'type' not in item:
                        data['data'][i]['type'] = type_
                    self._validator.validate(
                        schema=self.ResponseSchema(),
                        data={'data': {**data['data'][i]}, 'meta': {}},
                        type_=type_,
                        type_class=None,
                        to_primitives=False
                    )
        return json_response(status=status_code, data=data)
