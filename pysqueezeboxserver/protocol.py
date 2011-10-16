import re
import sys
from twisted.protocols.basic import LineReceiver
from twisted.python import log


class SqueezeboxServerProtocol(LineReceiver):


    """ Squeezebox Server Twisted Protocol """

    delimiter = "\r"
    re_response_type = re.compile("([a-fA-F0-9]{2}[:|\-]?){6}")
    response_types  = {
        "displaytype": {"name": "display_type"},
        "isplayer": {"type": bool, "name": "is_player"},
        "canpoweroff": {"type": bool, "name": "can_power_off"},
        "signalstrength": {"type": int, "name": "signal_strength"}
    }


    def __init__(self, service):

        """ Constructor """

        self.service = service
        self.logger = self.service.logger
        self.reader = self.service.reader
        self.service.protocol = self
        self.logger.debug("Configuration")
        self.logger.debug(self.service.config)


    # General callback methods

    def on_connect(self):

        """ On connection callback """

        self.logger.debug("Connected")
        self.init()


    def on_data(self, data):

        """ On data received callback """

        self.logger.debug("Data: [%s]" % (data))


    def on_line(self, line):

        """ On line received callback """

        line = self._unquote(line).strip()

        is_player = self.re_response_type.match(line)
        line_type = "player" if is_player else "server"

        self.logger.debug("%s: [%s]" % (line_type, line))

        parts = line.split()
        player = parts[0] if is_player else None
        parts = parts[1:] if is_player else parts
        params = list()

        if parts[-1] == "?": return

        while parts:
            method_name = "_".join(parts)
            try:
                method_key = "%s_%s" % (line_type, method_name)
                method = getattr(self, "on_%s" % (method_key))
                method_params = params[::-1]
                if player is not None: method_params.insert(0, player)
                method(*method_params)
                if method_key in self.service.callbacks:
                    self.service.callbacks.get(method_key)(*method_params)
                break
            except AttributeError:
                params.append(parts[-1])
                parts = parts[:-1]
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception, e:
                print e



    def init(self,
             username=None,
             password=None):

        """ Initialisation helper method """

        self.send("version ?")
        self.send("login")
        self.send("listen 1")
        self.send("player count ?")


    def update_players(self, count):

        """ Update player metadata and state """

        for i in xrange(count):
            self.send("player id %i ?" % (i))


    # Squeezebox Server data callback helpers


    def on_server_version(self, version):

        """ Helper for 'version' """

        self.service.state["server.version"] = version
        self.logger.info("SqueezeboxServer Version %s" % (version))


    def on_server_login(self, *args):

        """ Helper for 'login' """

        self.service.state["logged_in"] = (args[0] == "******")


    def on_server_listen(self, *args):

        """ Helper for 'listen' """

        pass


    def on_server_player_count(self, *args):

        """ Helper for 'player_count' data """

        count = int(args[0])
        self.service.state["player_count"] = count
        self.update_players(count)


    def on_server_player_id(self, *args):

        """ Helper for 'player_id' data """
    
        player = int(args[0])
        addr = self._unquote(args[1])

        self.logger.debug("Player #%i: %s" % (player, addr))
        
        cmds = ["uuid", "name", "ip", "model", "isplayer",
                "displaytype", "canpoweroff", "signalstrength"]

        for cmd in cmds:
            self.send("player %s %s ?" % (cmd, addr))
        

    def on_server_player(self, *args):

        key, player = args[0], args[1]
        value = args[2] if len(args) > 2 else None

        prop = key
        if key in self.response_types:
            rtype = self.response_types.get(key)
            value = rtype.get("type", str)(value)
            prop = rtype.get("name", key)
            

        if value is not None:
            self.service.update_player(player, {prop: value})


    def on_player_play(self, player):

        self.logger.debug("Player '%s' playing" % (player))
        self.service.update_player(player, {"playing": True})


    def on_player_pause(self, player):

        self.logger.debug("Player '%s' pausing" % (player))
        self.service.update_player(player, {"playing": False})


    def on_player_prefset_server_volume(self, player, volume):

        volume = int(volume)
        self.logger.debug("Mixer Volume '%s' : %i" % (player, volume))
        self.service.update_player(player, {"volume": volume, "mute": (volume == 0)})


    def on_player_prefset_server_mute(self, player):

        self.service.update_player(player, {"mute": True})
        


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



