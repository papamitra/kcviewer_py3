#!/usr/bin/env python

from libmproxy.proxy.config import ProxyConfig
from libmproxy.proxy.server import ProxyServer
from libmproxy import controller, cmdline
import os

class TestMaster(controller.Master):
    def __init__(self, server):
        controller.Master.__init__(self, server)
        #self.stickyhosts = {}

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, msg):
        #hid = (msg.host, msg.port)
        # if msg.headers["cookie"]:
        #     self.stickyhosts[hid] = msg.headers["cookie"]
        # elif hid in self.stickyhosts:
        #     msg.headers["cookie"] = self.stickyhosts[hid]
        print("request:", msg.headers)
        print(msg)
        msg.reply()
        return msg

    def handle_response(self, msg):
        #hid = (msg.request.host, msg.request.port)
        # if msg.headers["set-cookie"]:
        #     self.stickyhosts[hid] = msg.headers["set-cookie"]
        print("response:", msg.headers)
        print(msg)
        msg.reply()
        return msg


config = ProxyConfig(
#    cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem"),
)
server = ProxyServer(config, 8080, '127.0.0.1')
m = TestMaster(server)
m.run()
