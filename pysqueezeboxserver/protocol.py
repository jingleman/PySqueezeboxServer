import sys
from twisted.protocols.basic import LineReceiver


class SqueezeboxServer(LineReceiver):


    """ Squeezebox Server Twisted Protocol """

    delimiter = "\r"


    def __init__(self):

        """ Constructor """

        pass
        self.state = dict()
        self.players = dict()
        #self.setLineMode()


    # General callback methods

    def on_connect(self):

        """ On connection callback """

        print "Connected"
        self.on_init()


    def on_init(self):

        """ On initialisation callback """

        self.send("login")
        self.send("player count ?")


    def on_data(self, data):

        """ On data received callback """

        print "Data: [%s]" % (data)
        print data[-1] == "\n"


    def on_line(self, line):

        """ On line received callback """

        print "Line: [%s]" % (line)

        parts = line.split()
        params = list()

        while parts:
            method_name = "_".join(parts)
            try:
                print "Looking for method 'on_%s'" % (method_name)
                method = getattr(self, "on_%s" % (method_name))
                method(*params[::-1])
                break
            except AttributeError:
                params.append(parts[-1])
                parts = parts[:-1]
            except KeyboardInterrupt:
                sys.exit(0)





    def update_players(self, count):

        """ Update player metadata and state """

        for i in xrange(count):
            self.send("player id %i ?" % (i))



    # Squeezebox Server data callback helpers

    def on_player_count(self, *args):

        """ Helper for 'player_count' data """

        count = int(args[0])
        self.state["player_count"] = count
        self.update_players(count)


    def on_player_id(self, *args):

        """ Helper for 'player_id' data """
    
        player = int(args[0])
        addr = self._unquote(args[1])
        
        print "Player #%i: %s" % (player, addr)




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

        print "Data Received"
        self.on_data(data)


    def lineReceived(self, line):

        """ Twisted line received callback """

        print "Line Received"
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
