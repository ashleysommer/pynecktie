# -*- coding: utf-8 -*-
import traceback
from sanic.testing import SanicTestClient, HOST, PORT
from pynecktie.exceptions import MethodNotSupported
from pynecktie.log import logger
from pynecktie.response import text

class NecktieTestClient(SanicTestClient):
    def __init__(self, app, port=PORT):
        super(NecktieTestClient, self).__init__(app, port=port)
        self._sanic_endpoint_test = self._necktie_endpoint_test

    ## async def _local_request(self, method, uri, cookies=None, *args, **kwargs):

    def _necktie_endpoint_test(
            self, method='get', uri='/', gather_request=True,
            debug=False, server_kwargs={"auto_reload": False},
            *request_args, **request_kwargs):
        results = [None, None]
        exceptions = []

        if gather_request:
            def _collect_request(request):
                if results[0] is None:
                    results[0] = request
            self.app.request_middleware.appendleft(_collect_request)

        @self.app.exception(MethodNotSupported)
        async def error_handler(request, exception):
            if request.method in ['HEAD', 'PATCH', 'PUT', 'DELETE']:
                return text(
                    '', exception.status_code, headers=exception.headers
                )
            else:
                return self.app.error_handler.default(request, exception)

        @self.app.listener('after_server_start')
        async def _collect_response(sanic, loop):
            try:
                response = await self._local_request(
                    method, uri, *request_args,
                    **request_kwargs)
                results[-1] = response
            except Exception as e:
                logger.error(
                    'Exception:\n{}'.format(traceback.format_exc()))
                exceptions.append(e)
            self.app.stop()

        self.app.run(host=HOST, debug=debug, port=self.port, **server_kwargs)
        self.app.listeners['after_server_start'].pop()

        if exceptions:
            raise ValueError("Exception during request: {}".format(exceptions))

        if gather_request:
            try:
                request, response = results
                return request, response
            except BaseException:
                raise ValueError(
                    "Request and response object expected, got ({})".format(
                        results))
        else:
            try:
                return results[-1]
            except BaseException:
                raise ValueError(
                    "Request object expected, got ({})".format(results))


__all__ = ["NecktieTestClient", "HOST", "PORT"]
