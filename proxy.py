#!/usr/bin/env python

from libmproxy import controller, proxy
import os

import re
import json

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
        msg.reply()
        return msg

    def handle_response(self, msg):
        #hid = (msg.request.host, msg.request.port)
        # if msg.headers["set-cookie"]:
        #     self.stickyhosts[hid] = msg.headers["set-cookie"]
	print(msg.headers["Content-Type"])
        try:
            if re.search("text/javascript", msg.headers["Content-Type"][0]):
                #print("response:", msg.headers)
                #print(msg)
                js = json.loads(msg.get_decoded_content())
                print(json.dumps(js, sort_keys=True, indent=4).split("\n"))
                #print(msg.get_decoded_content())
        except Exception, e:
                print(e)
        msg.reply()
        return msg

config = proxy.ProxyConfig(
    cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem")
)

server = proxy.ProxyServer(config, 12345, '127.0.0.1')
m = TestMaster(server)
m.run()
