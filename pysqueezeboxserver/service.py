from twisted.application import service
from twisted.python import log

from utils import Logger


class SqueezeboxServerService(service.Service):

    """ Squeezebox Server Twisted Service """


    def __init__(self, 
                 reader=None, 
                 config=None, 
                 callbacks=None, 
                 verbose=False):

        """ Constructor """

        config = config or dict()
        callbacks = callbacks or dict()
        self.logger = Logger(verbose=verbose)
        self.reader = reader
        self.config = config
        self.callbacks = callbacks
        self.state = dict()
        self.players = dict()


    def get_player(self, 
                   ref=None, 
                   name=None):

        if ref is not None:
            return self.players.get(ref)
        elif name is not None:
            return filter(self.players, lambda p: name.lower() in p.name.lower())[0]


    def update_player(self, 
                      player, 
                      values):

        """ Update player object """

        if player not in self.players:
            self.players[player] = dict()
        self.players[player].update(values)


        print self.players


    # Twisted overrides


    def startService(self):

        """ Starts the service """

        service.Service.startService(self)
        log.msg("Done something")


