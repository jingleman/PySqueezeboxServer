#!/usr/bin/env python

import sys
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor
from twisted.python import log
from protocol import SqueezeboxServerProtocol, SqueezeboxServerFactory


def on_protocol(p):

    """ On protocol helper """

    log.msg("On Protocol")
    p.init()


if __name__ == "__main__":

    """ Main script execution """

    log.startLogging(sys.stdout)
    factory = SqueezeboxServerFactory() # sys.argv?
    point = TCP4ClientEndpoint(reactor, "10.0.2.10", 9090)
    d = point.connect(factory)
    d.addCallback(on_protocol)
    reactor.run()




