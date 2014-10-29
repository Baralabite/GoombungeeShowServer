from webconnserver import WebSocketServer
from eventhandler import EventHandler
from events import *
import logging, time, datetime, code
from config import *

import BaralabaBob

class Application:
    def __init__(self):
        pass

    """ Starts the ball rolling """
    def start(self):
        self.initLogging()

        self.hexapod = BaralabaBob.Hexapod(("localhost", 1997))
        self.hexapod.start()

        self.webSocketServer = WebSocketServer()
        self.webSocketServer.start()

        EventHandler.addListener("echo", Events.PACKET_RECEIVED, self.onPacketReceived)


        self.loop()

    """ Sets up the logging """
    def initLogging(self):
        self.logger = logging.getLogger(LOGGING_NAME)
        self.logger.setLevel(logging.DEBUG)

        ts = time.time()
        #TODO: Uncomment for long term logging, not testing
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')# %H.%M.%S')
        fh = logging.FileHandler("logs/%s.txt"%st)
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(created)f %(thread)d %(filename)s,%(lineno)d %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    """ The main loop of the program"""
    def loop(self):
        code.interact(local=locals())
        pass

    def onPacketReceived(self, data):
        packet = data[0]
        sendFunc = data[1]
        def respond(value):
            sendFunc(('{"%s":"%s"}\n' % ("response", value)).encode("UTF-8"))

        if "command" in packet:
            args = packet["command"].split(" ")

            if args[0] == "Ping":
                respond("Pong")
            elif args[0] == "Handshake":
                respond("Handshake")

        else:
            respond("Command not found")




if __name__ == "__main__":
    app = Application()
    app.start()
else:
    print("This project is not a library! It has to be run as a standalone program.")