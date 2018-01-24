# -*- coding: utf-8 -*-
from sanic.request import Request as SanicRequest, RequestParameters as SanicRequestParameters
from sanic.request import File, DEFAULT_HTTP_CONTENT_TYPE, parse_multipart_form


class Request(SanicRequest):
    pass


class RequestParameters(SanicRequestParameters):
    pass


__all__ = ["Request", "RequestParameters", "File", "DEFAULT_HTTP_CONTENT_TYPE",
           "parse_multipart_form"]
