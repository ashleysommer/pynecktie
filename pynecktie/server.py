# -*- coding: utf-8 -*-
import traceback

import asyncio
from httptools import HttpRequestParser
from httptools.parser.errors import HttpParserError
from sanic.server import CIDict as SanicCIDict,\
    HttpProtocol as SanicHttpProtocol,\
    Signal as SanicSignal
from sanic.server import serve as sanic_serve, serve_multiple as sanic_serve_multiple,\
    trigger_events, update_current_time, current_time

from pynecktie.exceptions import ServerError, RequestTimeout, ServiceUnavailable, PayloadTooLarge, InvalidUsage
from pynecktie.log import logger
from pynecktie.request import Request


class CIDict(SanicCIDict):
    pass


class Signal(SanicSignal):
    pass


class HttpProtocol(SanicHttpProtocol):
    __slots__ = tuple()

    def __init__(self, *, loop, request_handler, error_handler,
                 signal=Signal(), connections=set(), request_timeout=60,
                 response_timeout=60, keep_alive_timeout=5,
                 request_max_size=None, request_class=None, access_log=True,
                 keep_alive=True, is_request_stream=False, router=None,
                 state=None, debug=False, **kwargs):
        request_class = request_class or Request
        super(HttpProtocol, self).\
            __init__(loop=loop, request_handler=request_handler,
                     error_handler=error_handler, signal=signal,
                     connections=connections, request_timeout=request_timeout,
                     response_timeout=response_timeout, keep_alive_timeout=keep_alive_timeout,
                     request_max_size=request_max_size, request_class=request_class,
                     access_log=access_log, keep_alive=keep_alive,
                     is_request_stream=is_request_stream,
                     router=router, state=state, debug=debug, **kwargs)

    def request_timeout_callback(self):
        # See the docstring in the RequestTimeout exception, to see
        # exactly what this timeout is checking for.
        # Check if elapsed time since request initiated exceeds our
        # configured maximum request timeout value
        time_elapsed = current_time - self._last_request_time
        if time_elapsed < self.request_timeout:
            time_left = self.request_timeout - time_elapsed
            self._request_timeout_handler = (
                self.loop.call_later(time_left,
                                     self.request_timeout_callback)
            )
        else:
            if self._request_stream_task:
                self._request_stream_task.cancel()
            if self._request_handler_task:
                self._request_handler_task.cancel()
            try:
                raise RequestTimeout('Request Timeout')
            except RequestTimeout as exception:
                self.write_error(exception)

    def response_timeout_callback(self):
        # Check if elapsed time since response was initiated exceeds our
        # configured maximum request timeout value
        time_elapsed = current_time - self._last_request_time
        if time_elapsed < self.response_timeout:
            time_left = self.response_timeout - time_elapsed
            self._response_timeout_handler = (
                self.loop.call_later(time_left,
                                     self.response_timeout_callback)
            )
        else:
            try:
                raise ServiceUnavailable('Response Timeout')
            except ServiceUnavailable as exception:
                self.write_error(exception)

    def data_received(self, data):
        # Check for the request itself getting too large and exceeding
        # memory limits
        self._total_request_size += len(data)
        if self._total_request_size > self.request_max_size:
            exception = PayloadTooLarge('Payload Too Large')
            self.write_error(exception)

        # Create parser if this is the first time we're receiving data
        if self.parser is None:
            assert self.request is None
            self.headers = []
            self.parser = HttpRequestParser(self)

        # requests count
        self.state['requests_count'] = self.state['requests_count'] + 1

        # Parse request chunk or close connection
        try:
            self.parser.feed_data(data)
        except HttpParserError:
            message = 'Bad Request'
            if self._debug:
                message += '\n' + traceback.format_exc()
            exception = InvalidUsage(message)
            self.write_error(exception)

    def on_header(self, name, value):
        self._header_fragment += name

        if value is not None:
            if self._header_fragment == b'Content-Length' \
                    and int(value) > self.request_max_size:
                exception = PayloadTooLarge('Payload Too Large')
                self.write_error(exception)
            try:
                value = value.decode()
            except UnicodeDecodeError:
                value = value.decode('latin_1')
            self.headers.append(
                    (self._header_fragment.decode().casefold(), value))
            self._header_fragment = b''

    def on_headers_complete(self):
        self.request = self.request_class(
            url_bytes=self.url,
            headers=CIDict(self.headers),
            version=self.parser.get_http_version(),
            method=self.parser.get_method().decode(),
            transport=self.transport
        )
        # Remove any existing KeepAlive handler here,
        # It will be recreated if required on the new request.
        if self._keep_alive_timeout_handler:
            self._keep_alive_timeout_handler.cancel()
            self._keep_alive_timeout_handler = None
        if self.is_request_stream:
            self._is_stream_handler = self.router.is_stream_handler(
                self.request)
            if self._is_stream_handler:
                self.request.stream = asyncio.Queue()
                self.execute_request_handler()

    def write_response(self, response):
        """
        Writes response content synchronously to the transport.
        """
        if self._response_timeout_handler:
            self._response_timeout_handler.cancel()
            self._response_timeout_handler = None
        try:
            keep_alive = self.keep_alive
            self.transport.write(
                response.output(
                    self.request.version, keep_alive,
                    self.keep_alive_timeout))
            self.log_response(response)
        except AttributeError:
            logger.error('Invalid response object for url %s, '
                         'Expected Type: HTTPResponse, Actual Type: %s',
                         self.url, type(response))
            self.write_error(ServerError('Invalid response type'))
        except RuntimeError:
            if self._debug:
                logger.error('Connection lost before response written @ %s',
                             self.request.ip)
            keep_alive = False
        except Exception as e:
            self.bail_out(
                "Writing response failed, connection closed {}".format(
                    repr(e)))
        finally:
            if not keep_alive:
                self.transport.close()
                self.transport = None
            else:
                self._keep_alive_timeout_handler = self.loop.call_later(
                    self.keep_alive_timeout,
                    self.keep_alive_timeout_callback)
                self._last_response_time = current_time
                self.cleanup()

    async def stream_response(self, response):
        """
        Streams a response to the client asynchronously. Attaches
        the transport to the response so the response consumer can
        write to the response as needed.
        """
        if self._response_timeout_handler:
            self._response_timeout_handler.cancel()
            self._response_timeout_handler = None
        try:
            keep_alive = self.keep_alive
            response.transport = self.transport
            await response.stream(
                self.request.version, keep_alive, self.keep_alive_timeout)
            self.log_response(response)
        except AttributeError:
            logger.error('Invalid response object for url %s, '
                         'Expected Type: HTTPResponse, Actual Type: %s',
                         self.url, type(response))
            self.write_error(ServerError('Invalid response type'))
        except RuntimeError:
            if self._debug:
                logger.error('Connection lost before response written @ %s',
                             self.request.ip)
            keep_alive = False
        except Exception as e:
            self.bail_out(
                "Writing response failed, connection closed {}".format(
                    repr(e)))
        finally:
            if not keep_alive:
                self.transport.close()
                self.transport = None
            else:
                self._keep_alive_timeout_handler = self.loop.call_later(
                    self.keep_alive_timeout,
                    self.keep_alive_timeout_callback)
                self._last_response_time = current_time
                self.cleanup()

    def bail_out(self, message, from_error=False):
        if from_error or self.transport.is_closing():
            logger.error("Transport closed @ %s and exception "
                         "experienced during error handling",
                         self.transport.get_extra_info('peername'))
            logger.debug('Exception:\n%s', traceback.format_exc())
        else:
            exception = ServerError(message)
            self.write_error(exception)
            logger.error(message)

def serve(host, port, request_handler, error_handler, *args, before_start=None,
          after_start=None, before_stop=None, after_stop=None, debug=False,
          request_timeout=60, response_timeout=60, keep_alive_timeout=5,
          ssl=None, sock=None, request_max_size=None, reuse_port=False,
          loop=None, protocol=HttpProtocol, backlog=100,
          register_sys_signals=True, run_async=False, connections=None,
          signal=Signal(), request_class=None, access_log=True,
          keep_alive=True, is_request_stream=False, router=None,
          websocket_max_size=None, websocket_max_queue=None, state=None,
          graceful_shutdown_timeout=15.0, **kwargs):
    return sanic_serve(host, port, request_handler, error_handler, *args,
                       before_start=before_start, after_start=after_start, before_stop=before_stop,
                       after_stop=after_stop, debug=debug, request_timeout=request_timeout,
                       response_timeout=response_timeout, keep_alive_timeout=keep_alive_timeout,
                       ssl=ssl, sock=sock, request_max_size=request_max_size, reuse_port=reuse_port,
                       loop=loop, protocol=protocol, backlog=backlog,
                       register_sys_signals=register_sys_signals, run_async=run_async,
                       connections=connections, signal=signal, request_class=request_class,
                       access_log=access_log, keep_alive=keep_alive,
                       is_request_stream=is_request_stream, router=router,
                       websocket_max_size=websocket_max_size,
                       websocket_max_queue=websocket_max_queue, state=state,
                       graceful_shutdown_timeout=graceful_shutdown_timeout, **kwargs)


def serve_multiple(server_settings, workers):
    server_settings.setdefault('protocol', HttpProtocol)
    server_settings.setdefault('signal', Signal())
    return sanic_serve_multiple(server_settings, workers)


__all__ = ["CIDict", "Signal", "HttpProtocol",
           "serve", "serve_multiple", "trigger_events", "update_current_time"]
