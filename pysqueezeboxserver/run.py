import curses

from twisted.application.service import MultiService, Application
from twisted.application.internet import TCPServer, TCPClient
from twisted.internet import reactor

from factory import SqueezeboxServerFactory
from protocol import SqueezeboxServerProtocol
from service import SqueezeboxServerService
from gui import Screen

host = "higgs"
port = 9090
iface = "localhost"
something = "Hello"

ncurses_enabled = False
verbose = True

config = dict(hello="mum", goodbye="friend")
callbacks = {
    "player_play": lambda player: "Callback for Player '%s'" % (player)
}

top_service = MultiService()

reader = None

if ncurses_enabled:
    std_screen = curses.initscr()
    reader = Screen(std_screen)
    std_screen.refresh()
    reactor.addReader(reader)

sbs_service = SqueezeboxServerService(reader=reader, 
                                      config=config, 
                                      callbacks=callbacks,
                                      verbose=verbose)
sbs_service.setServiceParent(top_service)

factory = SqueezeboxServerFactory(sbs_service)
tcp_service = TCPClient(host, port, factory)
tcp_service.setServiceParent(top_service)

application = Application("pysqueezeboxserver")
top_service.setServiceParent(application)

