# -*- coding: utf-8 -*-
import os
import logging
import warnings
from functools import partial
from sanic.app import Sanic, Purpose, create_default_context
from sanic import reloader_helpers
from pynecktie.config import Config
from pynecktie.router import Router
from pynecktie.server import Signal, HttpProtocol, serve, serve_multiple
from pynecktie.handlers import ErrorHandler
from pynecktie.log import logger, error_logger, LOGGING_CONFIG_DEFAULTS
from pynecktie.testing import NecktieTestClient
from pynecktie.websocket import WebSocketProtocol


class Necktie(Sanic):

    def __init__(self, name=None, router=None, error_handler=None,
                 load_env=True, request_class=None,
                 strict_slashes=False, log_config=None,
                 configure_logging=True):
        log_config = log_config or LOGGING_CONFIG_DEFAULTS
        router = router or Router()
        error_handler = error_handler or ErrorHandler()
        super(Necktie, self).__init__(name, router, error_handler,
                                      load_env=False, request_class=request_class,
                                      strict_slashes=strict_slashes,
                                      log_config=log_config,
                                      configure_logging=configure_logging)
        self.config = Config(load_env=load_env)
        self.go_fast = self._necktie_serious

    # Decorator
    def route(self, uri, methods=frozenset({'GET'}), host=None,
              strict_slashes=None, stream=False, version=None, name=None):
        """Decorate a function to be registered as a route

        :param uri: path of the URL
        :param methods: list or tuple of methods allowed
        :param host:
        :param strict_slashes:
        :param stream:
        :param version:
        :param name: user defined route name for url_for
        :return: decorated function
        """
        return super(Necktie, self)\
            .route(uri, methods=methods, host=host,
                   strict_slashes=strict_slashes, stream=stream,
                   version=version, name=name)

    # Decorator
    def listener(self, event):
        """Create a listener from a decorated function.

        :param event: event to listen to
        """
        return super(Necktie, self).listener(event)

    # Decorator
    def websocket(self, uri, host=None, strict_slashes=None,
                  subprotocols=None, name=None):
        """Decorate a function to be registered as a websocket route

        :param uri: path of the URL
        :param subprotocols: optional list of strings with the supported
                             subprotocols
        :param host:
        :return: decorated function
        """
        return super(Necktie, self)\
            .websocket(uri, host=host, strict_slashes=strict_slashes,
                       subprotocols=subprotocols, name=name)

    def exception(self, *exceptions):
        """Decorate a function to be registered as a handler for exceptions

        :param exceptions: exceptions
        :return: decorated function
        """
        return super(Necktie, self).exception(*exceptions)

    def middleware(self, middleware_or_request):
        """Decorate and register middleware to be called before a request.
        Can either be called as @app.middleware or @app.middleware('request')
        """
        return super(Necktie, self).middleware(middleware_or_request)

    def static(self, uri, file_or_directory, pattern=r'/?.+',
               use_modified_since=True, use_content_range=False,
               stream_large_files=False, name='static', host=None,
               strict_slashes=None):
        """Register a root to serve files from. The input can either be a
        file or a directory. See
        """
        return super(Necktie, self)\
            .static(uri, file_or_directory, pattern=pattern,
                    use_modified_since=use_modified_since,
                    use_content_range=use_content_range,
                    stream_large_files=stream_large_files, name=name,
                    host=host, strict_slashes=strict_slashes)

    def blueprint(self, blueprint, **options):
        """Register a blueprint on the application.

        :param blueprint: Blueprint object
        :param options: option dictionary with blueprint defaults
        :return: Nothing
        """
        return super(Necktie, self).blueprint(blueprint, **options)

    @property
    def test_client(self):
        return NecktieTestClient(self)

    def run(self, host=None, port=None, debug=False, ssl=None,
            sock=None, workers=1, protocol=None,
            backlog=100, stop_event=None, register_sys_signals=True,
            access_log=True, **kwargs):
        """Run the HTTP Server and listen until keyboard interrupt or term
        signal. On termination, drain connections before closing.

        :param host: Address to host on
        :param port: Port to host on
        :param debug: Enables debug output (slows server)
        :param ssl: SSLContext, or location of certificate and key
                            for SSL encryption of worker(s)
        :param sock: Socket for the server to accept connections from
        :param workers: Number of processes
                            received before it is respected
        :param backlog:
        :param stop_event:
        :param register_sys_signals:
        :param protocol: Subclass of asyncio protocol class
        :return: Nothing
        """

        # Default auto_reload to false
        auto_reload = False
        # If debug is set, default it to true (unless on windows)
        if debug and os.name == 'posix':
            auto_reload = True
        # Allow for overriding either of the defaults
        auto_reload = kwargs.get("auto_reload", auto_reload)

        if sock is None:
            host, port = host or "127.0.0.1", port or 8000

        if protocol is None:
            protocol = (WebSocketProtocol if self.websocket_enabled
                        else HttpProtocol)
        if stop_event is not None:
            if debug:
                warnings.simplefilter('default')
            warnings.warn("stop_event will be removed from future versions.",
                          DeprecationWarning)
        server_settings = self._helper(
            host=host, port=port, debug=debug, ssl=ssl, sock=sock,
            workers=workers, protocol=protocol, backlog=backlog,
            register_sys_signals=register_sys_signals,
            access_log=access_log, auto_reload=auto_reload)

        try:
            self.is_running = True
            if workers == 1:
                if auto_reload and os.name != 'posix':
                    # This condition must be removed after implementing
                    # auto reloader for other operating systems.
                    raise NotImplementedError

                if auto_reload and \
                        os.environ.get('SANIC_SERVER_RUNNING') != 'true':
                    reloader_helpers.watchdog(2)
                else:
                    serve(**server_settings)
            else:
                serve_multiple(server_settings, workers)
        except BaseException:
            error_logger.exception(
                'Experienced exception while trying to serve')
            raise
        finally:
            self.is_running = False
        logger.info("Server Stopped")

    def _helper(self, host=None, port=None, debug=False,
                ssl=None, sock=None, workers=1, loop=None,
                protocol=HttpProtocol, backlog=100, stop_event=None,
                register_sys_signals=True, run_async=False, access_log=True,
                auto_reload=False):
        """Helper function used by `run` and `create_server`."""
        if isinstance(ssl, dict):
            # try common aliaseses
            cert = ssl.get('cert') or ssl.get('certificate')
            key = ssl.get('key') or ssl.get('keyfile')
            if cert is None or key is None:
                raise ValueError("SSLContext or certificate and key required.")
            context = create_default_context(purpose=Purpose.CLIENT_AUTH)
            context.load_cert_chain(cert, keyfile=key)
            ssl = context
        if stop_event is not None:
            if debug:
                warnings.simplefilter('default')
            warnings.warn("stop_event will be removed from future versions.",
                          DeprecationWarning)

        self.error_handler.debug = debug
        self.debug = debug

        server_settings = {
            'protocol': protocol,
            'request_class': self.request_class,
            'is_request_stream': self.is_request_stream,
            'router': self.router,
            'host': host,
            'port': port,
            'sock': sock,
            'ssl': ssl,
            'signal': Signal(),
            'debug': debug,
            'request_handler': self.handle_request,
            'error_handler': self.error_handler,
            'request_timeout': self.config.REQUEST_TIMEOUT,
            'response_timeout': self.config.RESPONSE_TIMEOUT,
            'keep_alive_timeout': self.config.KEEP_ALIVE_TIMEOUT,
            'request_max_size': self.config.REQUEST_MAX_SIZE,
            'keep_alive': self.config.KEEP_ALIVE,
            'loop': loop,
            'register_sys_signals': register_sys_signals,
            'backlog': backlog,
            'access_log': self.config.ACCESS_LOG,
            'websocket_max_size': self.config.WEBSOCKET_MAX_SIZE,
            'websocket_max_queue': self.config.WEBSOCKET_MAX_QUEUE,
            'websocket_read_limit': self.config.WEBSOCKET_READ_LIMIT,
            'websocket_write_limit': self.config.WEBSOCKET_WRITE_LIMIT,
            'graceful_shutdown_timeout': self.config.GRACEFUL_SHUTDOWN_TIMEOUT
        }

        # -------------------------------------------- #
        # Register start/stop events
        # -------------------------------------------- #

        for event_name, settings_name, reverse in (
                ("before_server_start", "before_start", False),
                ("after_server_start", "after_start", False),
                ("before_server_stop", "before_stop", True),
                ("after_server_stop", "after_stop", True),
        ):
            listeners = self.listeners[event_name].copy()
            if reverse:
                listeners.reverse()
            # Prepend app to the arguments when listeners are triggered
            listeners = [partial(listener, self) for listener in listeners]
            server_settings[settings_name] = listeners

        if self.configure_logging and debug:
            logger.setLevel(logging.DEBUG)
        if self.config.LOGO is not None and \
                os.environ.get('SANIC_SERVER_RUNNING') != 'true':
            logger.debug(self.config.LOGO)

        if run_async:
            server_settings['run_async'] = True

        # Serve
        if host and port and \
                os.environ.get('SANIC_SERVER_RUNNING') != 'true':
            proto = "http"
            if ssl is not None:
                proto = "https"
            logger.info('Service up @ {}://{}:{}'.format(proto, host, port))

        return server_settings

    def _necktie_serious(self, *args, **kwargs):
        raise NotImplementedError(
            "pyNecktie is a serious library for serious business.\n"
            "Use `run()`.")


__all__ = ['Necktie']
