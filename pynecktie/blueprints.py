# -*- coding: utf-8 -*-
from sanic.blueprints import Blueprint as SanicBlueprint


class Blueprint(SanicBlueprint):
    def route(self, uri, methods=frozenset({'GET'}), host=None,
              strict_slashes=None, stream=False, version=None, name=None):
        return super(Blueprint, self)\
            .route(uri, methods=methods, host=host,
                   strict_slashes=strict_slashes, stream=stream,
                   version=version, name=name)

    def websocket(self, uri, host=None, strict_slashes=None, version=None,
                  name=None):
        return super(Blueprint, self)\
            .websocket(uri, host=host, strict_slashes=strict_slashes,
                       version=version, name=name)

    def listener(self, event):
        return super(Blueprint, self).listener(event)

    def middleware(self, *args, **kwargs):
        """Create a blueprint middleware from a decorated function."""
        return super(Blueprint, self).middleware(*args, **kwargs)

    def exception(self, *args, **kwargs):
        """Create a blueprint exception from a decorated function."""
        return super(Blueprint, self).exception(*args, **kwargs)

    def static(self, uri, file_or_directory, *args, **kwargs):
        """Create a blueprint static route from a decorated function."""
        return super(Blueprint, self).static(uri, file_or_directory,
                                             *args, **kwargs)


__all__ = ["Blueprint"]
