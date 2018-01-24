# -*- coding: utf-8 -*-
from sanic.router import Router as SanicRouter,\
    RouteExists as SanicRouteExists,\
    RouteDoesNotExist as SanicRouteDoesNotExist
from sanic.router import Route, Parameter, REGEX_TYPES,\
    ROUTER_CACHE_SIZE, url_hash


class Router(SanicRouter):
    pass


class RouteExists(SanicRouteExists):
    pass


class RouteDoesNotExist(SanicRouteDoesNotExist):
    pass


__all__ = ["Router", "RouteExists", "RouteDoesNotExist",
           "Route", "Parameter", "REGEX_TYPES",
           "ROUTER_CACHE_SIZE", "url_hash"]
