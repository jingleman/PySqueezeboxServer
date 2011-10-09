import re
import sys
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.python import log


class SqueezeboxServerProtocol(LineReceiver):


    """ Squeezebox Server Twisted Protocol """

    delimiter = "\r"


    def __init__(self):

        """ Constructor """

        pass
        self.state = dict()
        self.players = dict()


    # General callback methods

    def on_connect(self):

        """ On connection callback """

        log.msg("Connected")


    def on_data(self, data):

        """ On data received callback """

        log.msg("Data: [%s]" % (data))


    def on_line(self, line):

        """ On line received callback """

        line = self._unquote(line).strip()

        is_event = re.compile("([a-fA-F0-9]{2}[:|\-]?){6}").match(line)
        line_type = "Event" if is_event else "Response"

        log.msg("%s: [%s]" % (line_type, line))

        parts = line.split()
        params = list()

        if is_event:
            self.on_event(parts[0], parts[1:])
            return

        while parts:
            method_name = "_".join(parts)
            try:
                method = getattr(self, "on_%s" % (method_name))
                method(*params[::-1])
                break
            except AttributeError:
                params.append(parts[-1])
                parts = parts[:-1]
            except KeyboardInterrupt:
                sys.exit(0)



    def init(self,
             username=None,
             password=None):

        """ Initialisation helper method """

        self.send("login")
        self.send("listen 1")
        self.send("player count ?")


    def on_event(self, player, args):

        """ On event helper method """

        log.msg("Event for player '%s': %s" % (player, args))


    def update_players(self, count):

        """ Update player metadata and state """

        for i in xrange(count):
            self.send("player id %i ?" % (i))


    # Squeezebox Server data callback helpers


    def on_login(self, *args):

        """ Helper for 'login' """

        self.state["logged_in"] = (args[0] == "******")


    def on_listen(self, *args):

        """ Helper for 'listen' """

        print args


    def on_player_count(self, *args):

        """ Helper for 'player_count' data """

        count = int(args[0])
        self.state["player_count"] = count
        self.update_players(count)


    def on_player_id(self, *args):

        """ Helper for 'player_id' data """
    
        player = int(args[0])
        addr = self._unquote(args[1])
        
        log.msg("Player #%i: %s" % (player, addr))




    # Utility methods

    def send(self, line):

        """ Transport send helper """

        self.sendLine(line)


    # Twisted specific methods


    def connectionMade(self):

        """ Twisted connection made callback """

        self.on_connect()


    def rawDataReceived(self, data):

        """ Twisted data received callback """

        self.on_data(data)


    def lineReceived(self, line):

        """ Twisted line received callback """

        self.on_line(line)


    # General helper methods


    def _quote(self, text):

        """ Quote helper """

        try:
            import urllib.parse
            return urllib.parse.quote(text, encoding=self.charset)
        except ImportError:
            import urllib
            return urllib.quote(text)


    def _unquote(self, text):

        """ Unquote helper """
        
        try:
            import urllib.parse
            return urllib.parse.unquote(text, encoding=self.charset)
        except ImportError:
            import urllib
            return urllib.unquote(text)



class SqueezeboxServerFactory(ClientFactory):


    """ Squeezebox Server Twisted Client Factory """


    protocol = SqueezeboxServerProtocol


    def clientConnectionFailed(self, connector, reason):
        
        reactor.stop()


    def clientConnectionLost(self, connector, reason):

        reactor.stop()


    def startFactory(self):

        self.message_queue = []
        self.client_instance = None


    def clientReady(self, instance):
        
        self.client_instance = instance
        for msg in self.message_queue:
            self.sendMessage(msg)


    def sendMessage(self, msg):

        if self.client_instance is not None:
            self.client_instance.send_line(msg)
        else:
            self.message_queue.append(msg)
