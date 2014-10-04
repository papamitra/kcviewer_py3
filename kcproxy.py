#!/usr/bin/env python

from libmproxy.proxy.config import ProxyConfig
from libmproxy.proxy.server import ProxyServer
from libmproxy import controller, cmdline
import os

import re
import simplejson

class KCMaster(controller.Master):
    def __init__(self, server, on_receive = None):
        controller.Master.__init__(self, server)
        self.on_receive = on_receive

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, msg):
        msg.reply()
        return msg

    def handle_response(self, msg):
        if self.on_receive:
            self.on_receive(msg)

        msg.reply()
        return msg


class KCProxy(object):
    def __init__(self, on_receive = None):
        config = ProxyConfig(
            port = 12345,
            confdir = "./cert"
            #    cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem"),
        )
        server = ProxyServer(config)
        self.master = KCMaster(server, on_receive)

    def run(self):
        self.master.run()

    def shutdown(self):
        self.master.shutdown()

if __name__ == '__main__':
    proxy = KCProxy()
    proxy.run()

