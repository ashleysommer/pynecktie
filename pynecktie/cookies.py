# -*- coding: utf-8 -*-
from sanic.cookies import Cookie as SanicCookie, CookieJar as SanicCookieJar,\
    MultiHeader as SanicMultiHeader


class Cookie(SanicCookie):
    pass


class MultiHeader(SanicMultiHeader):
    pass


class CookieJar(SanicCookieJar):
    def __setitem__(self, key, value):
        # If this cookie doesn't exist, add it to the header keys
        cookie_header = self.cookie_headers.get(key)
        if not cookie_header:
            cookie = Cookie(key, value)
            cookie['path'] = '/'
            cookie_header = MultiHeader("Set-Cookie")
            self.cookie_headers[key] = cookie_header
            self.headers[cookie_header] = cookie
            return super().__setitem__(key, cookie)
        else:
            self[key].value = value


__all__ = ["Cookie", "CookieJar", "MultiHeader"]

