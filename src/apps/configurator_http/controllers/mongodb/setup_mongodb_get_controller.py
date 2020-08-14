from http import HTTPStatus
from typing import final

from aiohttp.web import Request, Response

from src.apps.configurator_http.controllers.controller import Controller
from src.libs.configurator.mongodb.configurer import MongoDBConfigurerService


@final
class SetupMongoDBGetController(Controller):
    __slots__ = '_service'

    def __init__(self, service: MongoDBConfigurerService):
        self._service = service

    async def __call__(self, request: Request) -> Response:
        try:
            await self._service.setup(
                only_database=request.query.get('mongodb-database'),
                db_suffix=request.query.get('mongodb-database-suffix')
            )
            return self.response(HTTPStatus.OK, data={'status': 'OK'})
        except Exception as err:
            return self.response(HTTPStatus.INTERNAL_SERVER_ERROR, data={'status': 'KO', 'message': str(err)})
