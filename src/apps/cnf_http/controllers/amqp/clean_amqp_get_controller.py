from http import HTTPStatus
from typing import final

from aiohttp.web import Request, Response

from src.apps.cnf_http.controllers.controller import Controller
from src.libs.shared.infrastructure.configurator.amqp.configurer import AMQPConfigurerService


@final
class CleanAMQPGetController(Controller):
    __slots__ = '_service'

    def __init__(self, service: AMQPConfigurerService):
        self._service = service

    async def __call__(self, request: Request) -> Response:
        try:
            await self._service.clean(
                only_exchange=request.query.get('amqp-exchange'),
                exchange_suffix=request.query.get('amqp-exchange-suffix')
            )
            return self.response(HTTPStatus.OK, data={'status': 'OK'})
        except Exception as err:
            return self.response(HTTPStatus.INTERNAL_SERVER_ERROR, data={'status': 'KO', 'message': str(err)})
