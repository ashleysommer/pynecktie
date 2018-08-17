# -*- coding: utf-8 -*-

from sanic.websocket import WebSocketProtocol as SanicWebsocketProtocol
from pynecktie.request import Request
from pynecktie.server import Signal


class WebSocketProtocol(SanicWebsocketProtocol):
    def __init__(self, *args, websocket_timeout=10,
                 websocket_max_size=None,
                 websocket_max_queue=None,
                 websocket_read_limit=2 ** 16,
                 websocket_write_limit=2 ** 16, **kwargs):
        kwargs.setdefault("signal", Signal())
        kwargs.setdefault("requequest_class", Request)
        super(WebSocketProtocol, self).__init__(*args,
            websocket_timeout=websocket_timeout,
            websocket_max_size=websocket_max_size,
            websocket_max_queue=websocket_max_queue,
            websocket_read_limit=websocket_read_limit,
            websocket_write_limit=websocket_write_limit,
            **kwargs)


__all__ = ["WebSocketProtocol"]
