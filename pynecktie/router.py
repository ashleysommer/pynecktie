# -*- coding: utf-8 -*-
from functools import lru_cache

from sanic.router import Router as SanicRouter,\
    RouteExists as SanicRouteExists,\
    RouteDoesNotExist as SanicRouteDoesNotExist
from sanic.router import Route, Parameter, REGEX_TYPES,\
    ROUTER_CACHE_SIZE, url_hash

from pynecktie.exceptions import MethodNotSupported, NotFound


class Router(SanicRouter):
    @lru_cache(maxsize=ROUTER_CACHE_SIZE)
    def _get(self, url, method, host):
        """Get a request handler based on the URL of the request, or raises an
        error.  Internal method for caching.

        :param url: request URL
        :param method: request method
        :return: handler, arguments, keyword arguments
        """
        url = host + url
        # Check against known static routes
        route = self.routes_static.get(url)
        method_not_supported = MethodNotSupported(
            'Method {} not allowed for URL {}'.format(method, url),
            method=method,
            allowed_methods=self.get_supported_methods(url))
        if route:
            if route.methods and method not in route.methods:
                raise method_not_supported
            match = route.pattern.match(url)
        else:
            route_found = False
            # Move on to testing all regex routes
            for route in self.routes_dynamic[url_hash(url)]:
                match = route.pattern.match(url)
                route_found |= match is not None
                # Do early method checking
                if match and method in route.methods:
                    break
            else:
                # Lastly, check against all regex routes that cannot be hashed
                for route in self.routes_always_check:
                    match = route.pattern.match(url)
                    route_found |= match is not None
                    # Do early method checking
                    if match and method in route.methods:
                        break
                else:
                    # Route was found but the methods didn't match
                    if route_found:
                        raise method_not_supported
                    raise NotFound('Requested URL {} not found'.format(url))

        kwargs = {p.name: p.cast(value)
                  for value, p
                  in zip(match.groups(1), route.parameters)}
        route_handler = route.handler
        if hasattr(route_handler, 'handlers'):
            route_handler = route_handler.handlers[method]
        return route_handler, [], kwargs, route.uri

    def is_stream_handler(self, request):
        """ Handler for request is stream or not.
        :param request: Request object
        :return: bool
        """
        try:
            handler = self.get(request)[0]
        except (NotFound, MethodNotSupported):
            return False
        if (hasattr(handler, 'view_class') and
                hasattr(handler.view_class, request.method.lower())):
            handler = getattr(handler.view_class, request.method.lower())
        return hasattr(handler, 'is_stream')


class RouteExists(SanicRouteExists):
    pass


class RouteDoesNotExist(SanicRouteDoesNotExist):
    pass


__all__ = ["Router", "RouteExists", "RouteDoesNotExist",
           "Route", "Parameter", "REGEX_TYPES",
           "ROUTER_CACHE_SIZE", "url_hash"]
