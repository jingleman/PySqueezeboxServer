#!/usr/bin/env python

from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor

from protocol import SqueezeboxServer

def on_protocol():
    print "on protocol"

factory = Factory()
factory.protocol = SqueezeboxServer
point = TCP4ClientEndpoint(reactor, "10.0.2.10", 9090)
d = point.connect(factory)
d.addCallback(on_protocol)
reactor.run()
