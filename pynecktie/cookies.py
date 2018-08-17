# -*- coding: utf-8 -*-
from sanic.cookies import Cookie as SanicCookie, CookieJar as SanicCookieJar


class CookieJar(SanicCookieJar):
    def __setitem__(self, key, value):
        # If this cookie doesn't exist, add it to the header keys
        if not self.cookie_headers.get(key):
            cookie = Cookie(key, value)
            cookie['path'] = '/'
            self.cookie_headers[key] = self.header_key
            self.headers.add(self.header_key, cookie)
            return super().__setitem__(key, cookie)
        else:
            self[key].value = value


class Cookie(SanicCookie):
    pass


__all__ = ["Cookie", "CookieJar"]

