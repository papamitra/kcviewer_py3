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
            self.on_receive(msg.headers["Content-Type"])

        """
        try:
            if re.search("application/json", msg.headers["Content-Type"][0]):
                js = simplejson.loads(msg.content)
                print(simplejson.dumps(js, sort_keys=True, indent=4).split("\n"))
                #print(msg.get_decoded_content())
            elif re.search("text/plain", msg.headers["Content-Type"][0]):
                if 0 == msg.content.index("svdata="):
                    js = simplejson.loads(msg.content[7:])

        except Exception, e:
                print(e)
        """

        msg.reply()
        return msg


class KCProxy(object):
    def __init__(self, on_receive = None):
        config = ProxyConfig(
            confdir = "./cert"
            #    cacert = os.path.expanduser("~/.mitmproxy/mitmproxy-ca.pem"),
        )
        server = ProxyServer(config, 12345, '127.0.0.1')
        self.master = KCMaster(server, on_receive)

    def run(self):
        self.master.run()

    def shutdown(self):
        self.master.shutdown()

if __name__ == '__main__':
    proxy = KCProxy()
    proxy.run()
