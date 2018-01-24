# -*- coding: utf-8 -*-

from sanic.websocket import WebSocketProtocol as SanicWebsocketProtocol
from pynecktie.request import Request
from pynecktie.server import Signal


class WebSocketProtocol(SanicWebsocketProtocol):
    def __init__(self, *args, websocket_max_size=None,
                 websocket_max_queue=None, **kwargs):
        kwargs.setdefault("signal", Signal())
        kwargs.setdefault("requequest_class", Request)
        super(WebSocketProtocol, self).__init__()


__all__ = ["WebSocketProtocol"]
