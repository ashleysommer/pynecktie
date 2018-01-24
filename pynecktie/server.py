# -*- coding: utf-8 -*-

from sanic.server import CIDict as SanicCIDict,\
    HttpProtocol as SanicHttpProtocol,\
    Signal as SanicSignal
from sanic.server import serve as sanic_serve, serve_multiple as sanic_serve_multiple,\
    trigger_events, update_current_time

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
