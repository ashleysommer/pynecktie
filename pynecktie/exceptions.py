# -*- coding: utf-8 -*-
from sanic.exceptions import SanicException
from pynecktie.response import STATUS_CODES

_necktie_exceptions = {}


def add_status_code(code):
    """
    Decorator used for adding exceptions to _sanic_exceptions.
    """
    def class_decorator(cls):
        cls.status_code = code
        _necktie_exceptions[code] = cls
        return cls
    return class_decorator


class NecktieException(SanicException):
    pass


@add_status_code(404)
class NotFound(NecktieException):
    pass


@add_status_code(400)
class InvalidUsage(NecktieException):
    pass


@add_status_code(500)
class ServerError(NecktieException):
    pass


@add_status_code(503)
class ServiceUnavailable(NecktieException):
    """The server is currently unavailable (because it is overloaded or
    down for maintenance). Generally, this is a temporary state."""
    pass


class URLBuildError(ServerError):
    pass


class FileNotFound(NotFound):
    pass

    def __init__(self, message, path, relative_url):
        super().__init__(message)
        self.path = path
        self.relative_url = relative_url


@add_status_code(408)
class RequestTimeout(NecktieException):
    """The Web server (running the Web site) thinks that there has been too
    long an interval of time between 1) the establishment of an IP
    connection (socket) between the client and the server and
    2) the receipt of any data on that socket, so the server has dropped
    the connection. The socket connection has actually been lost - the Web
    server has 'timed out' on that particular socket connection.
    """
    pass


@add_status_code(413)
class PayloadTooLarge(NecktieException):
    pass


class HeaderNotFound(InvalidUsage):
    pass


@add_status_code(416)
class ContentRangeError(NecktieException):
    pass

    def __init__(self, message, content_range):
        super().__init__(message)
        self.headers = {
            'Content-Type': 'text/plain',
            "Content-Range": "bytes */%s" % (content_range.total,)
        }


@add_status_code(403)
class Forbidden(NecktieException):
    pass


class InvalidRangeType(ContentRangeError):
    pass


@add_status_code(401)
class Unauthorized(NecktieException):
    """
    Unauthorized exception (401 HTTP status code).

    :param message: Message describing the exception.
    :param status_code: HTTP Status code.
    :param scheme: Name of the authentication scheme to be used.

    When present, kwargs is used to complete the WWW-Authentication header.

    Examples::

        # With a Basic auth-scheme, realm MUST be present:
        raise Unauthorized("Auth required.",
                           scheme="Basic",
                           realm="Restricted Area")

        # With a Digest auth-scheme, things are a bit more complicated:
        raise Unauthorized("Auth required.",
                           scheme="Digest",
                           realm="Restricted Area",
                           qop="auth, auth-int",
                           algorithm="MD5",
                           nonce="abcdef",
                           opaque="zyxwvu")

        # With a Bearer auth-scheme, realm is optional so you can write:
        raise Unauthorized("Auth required.", scheme="Bearer")

        # or, if you want to specify the realm:
        raise Unauthorized("Auth required.",
                           scheme="Bearer",
                           realm="Restricted Area")
    """
    def __init__(self, message, status_code=None, scheme=None, **kwargs):
        super().__init__(message, status_code)

        # if auth-scheme is specified, set "WWW-Authenticate" header
        if scheme is not None:
            values = ["{!s}={!r}".format(k, v) for k, v in kwargs.items()]
            challenge = ', '.join(values)

            self.headers = {
                "WWW-Authenticate": "{} {}".format(scheme, challenge).rstrip()
            }


def abort(status_code, message=None):
    """
    Raise an exception based on NecktieException. Returns the HTTP response
    message appropriate for the given status code, unless provided.

    :param status_code: The HTTP status code to return.
    :param message: The HTTP response body. Defaults to the messages
                    in response.py for the given status code.
    """
    if message is None:
        message = STATUS_CODES.get(status_code)
        # These are stored as bytes in the STATUS_CODES dict
        message = message.decode('utf8')
    necktie_exception = _necktie_exceptions.get(status_code, NecktieException)
    raise necktie_exception(message=message, status_code=status_code)
