#!/usr/bin/env python

from libmproxy.proxy.config import ProxyConfig
from libmproxy.proxy.server import ProxyServer
from libmproxy import controller, cmdline
import os

import re
import simplejson

class KCMaster(controller.Master):
    def __init__(self, server):
        controller.Master.__init__(self, server)

    def run(self):
        try:
            return controller.Master.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, msg):
        msg.reply()
        return msg

    def handle_response(self, msg):
	print(msg.headers["Content-Type"])
        """
        try:
            if re.search("application/json", msg.headers["Content-Type"][0]):
                print("response:", msg.headers)
                print("msg.content ----------------")
                print(msg.content)
                print("decode json -----------------")
                js = simplejson.loads(msg.content)
                print(simplejson.dumps(js, sort_keys=True, indent=4).split("\n"))
                #print(msg.get_decoded_content())
            elif re.search("text/plain", msg.headers["Content-Type"][0]):
                if 0 == msg.content.index("svdata="):
                    js = simplejson.loads(msg.content[7:])
                    print(simplejson.dumps(js, sort_keys=True, indent=4).split("\n"))
                    
        except Exception, e:
                print(e)
        """
        msg.reply()
        return msg


config = ProxyConfig(
    confdir = "./cert"
#    cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem"),
)

server = ProxyServer(config, 12345, '127.0.0.1')
m = KCMaster(server)
m.run()
