from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from protocol import SqueezeboxServerProtocol


class SqueezeboxServerFactory(ClientFactory):


    """ Squeezebox Server Twisted Client Factory """


    protocol = SqueezeboxServerProtocol


    def __init__(self, service):

        """ Constructor """

        self.service = service
        self.reader = self.service.reader


    def buildProtocol(self, addr):

        """ Build Protocol """

        return self.protocol(service=self.service)


    def clientConnectionFailed(self, connector, reason):
        
        """ Client Connection Failure Callback """

        reactor.stop()


    def clientConnectionLost(self, connector, reason):

        """ Client Connection Drop Callback """

        reactor.stop()


    def startFactory(self):

        """ Factory Initialisation """

        self.message_queue = []
        self.client_instance = None


    def clientReady(self, instance):
        
        """ Client Ready Callback """

        self.client_instance = instance
        for msg in self.message_queue:
            self.sendMessage(msg)


    def sendMessage(self, msg):

        """ Message Sending Helper """

        if self.client_instance is not None:
            self.client_instance.send_line(msg)
        else:
            self.message_queue.append(msg)

