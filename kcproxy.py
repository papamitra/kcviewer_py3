#!/usr/bin/env python

from libmproxy.proxy.config import ProxyConfig
from libmproxy.proxy.server import ProxyServer
from libmproxy import controller, cmdline
import os

import re
import simplejson

class KCMaster(controller.Master):
    def __init__(self, server, on_response=None, on_request=None):
        controller.Master.__init__(self, server)
        self.on_response = on_response
        self.on_request = on_request

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, msg):
        if self.on_request:
            self.on_request(msg)

        msg.reply()
        return msg

    def handle_response(self, msg):
        if self.on_response:
            self.on_response(msg)

        msg.reply()
        return msg


class KCProxy(object):
    def __init__(self, on_response=None, on_request=None):
        upstream = os.environ.get('http_proxy')
        config = ProxyConfig(
            port = 0,
            mode = 'upstream' if upstream else None,
            upstream_server = cmdline.parse_server_spec(upstream) if upstream else None,
            confdir = "./cert"
        )
        self.server = ProxyServer(config)
        self.master = KCMaster(self.server, on_response, on_request)

    def run(self):
        self.master.run()

    def shutdown(self):
        self.master.shutdown()

    def port(self):
        return self.server.address.port

if __name__ == '__main__':
    proxy = KCProxy()
    proxy.run()

