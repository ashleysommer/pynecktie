# -*- coding: utf-8 -*-

from sanic.testing import SanicTestClient, HOST, PORT

class NecktieTestClient(SanicTestClient):
    def __init__(self, app, port=PORT):
        super(NecktieTestClient, self).__init__(app, port=port)


__all__ = ["NecktieTestClient", "HOST", "PORT"]
