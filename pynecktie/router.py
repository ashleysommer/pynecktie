# -*- coding: utf-8 -*-
from functools import lru_cache

from sanic.router import Router as SanicRouter,\
    RouteExists as SanicRouteExists,\
    RouteDoesNotExist as SanicRouteDoesNotExist
from sanic.router import Route, Parameter, REGEX_TYPES,\
    ROUTER_CACHE_SIZE, url_hash

from pynecktie.exceptions import InvalidUsage, NotFound


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
        method_not_supported = InvalidUsage(
            'Method {} not allowed for URL {}'.format(
                method, url), status_code=405)
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


class RouteExists(SanicRouteExists):
    pass


class RouteDoesNotExist(SanicRouteDoesNotExist):
    pass


__all__ = ["Router", "RouteExists", "RouteDoesNotExist",
           "Route", "Parameter", "REGEX_TYPES",
           "ROUTER_CACHE_SIZE", "url_hash"]
