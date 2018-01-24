# -*- coding: utf-8 -*-
from sanic.handlers import ErrorHandler as SanicErrorHandler,\
    ContentRangeHandler as SanicContentRangeHandler


class ErrorHandler(SanicErrorHandler):
    pass


class ContentRangeHandler(SanicContentRangeHandler):
    __slots__ = tuple()


__all__ = ["ErrorHandler", "ContentRangeHandler"]

