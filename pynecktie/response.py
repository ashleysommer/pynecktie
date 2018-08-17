# -*- coding: utf-8 -*-
from sanic.response import BaseHTTPResponse as SanicBaseHTTPResponse, HTTPResponse as SanicHTTPResponse,\
    StreamingHTTPResponse as SanicStreamingHTTPResponse
from sanic.response import text, raw, json, file, file_stream, html, redirect, stream, json_dumps
from sanic import http
from sanic.http import STATUS_CODES

from pynecktie.cookies import CookieJar


class BaseHTTPResponse(SanicBaseHTTPResponse):
    @property
    def cookies(self):
        if self._cookies is None:
            self._cookies = CookieJar(self.headers)
        return self._cookies


class HTTPResponse(SanicHTTPResponse):
    @property
    def cookies(self):
        if self._cookies is None:
            self._cookies = CookieJar(self.headers)
        return self._cookies


class StreamingHTTPResponse(SanicStreamingHTTPResponse):
    pass


__all__ = ["BaseHTTPResponse", "HTTPResponse", "StreamingHTTPResponse",
           "text", "raw", "json", "file", "file_stream", "html",
           "redirect", "stream", "json_dumps", "STATUS_CODES"]


