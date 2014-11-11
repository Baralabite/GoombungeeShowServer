import socketserver
from eventhandler import EventHandler
from threading import Thread, current_thread
import logging
from config import *
from events import Events
from ast import literal_eval

class WebRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        self.running = True
        EventHandler.addListener("onQuit"+str(current_thread().ident), Events.SERVER_SHUTDOWN, self.shutdown)
        self.logger = logging.getLogger(Config.LOGGING_NAME+".SocketServer.RequestHandler")
        #self.logger.debug("Connection from %s", self.client_address)

        packetStarted = False
        packetContents = ""
        while self.running:
            receivedData = self.request.recv(1)
            if not receivedData: break  # If there is no dataz, then probably the client disconnected.
            try:
                receivedData = receivedData.decode("utf-8")
            except:
                continue

            if not packetStarted:       # If the packetStarted flag has not been set, set it when "{" is received
                if receivedData == "~":
                    packetStarted = True
                    packetContents = packetContents + "{"
            elif packetStarted:         # If the packet has started, append stuff to it until "}" is received
                if receivedData == "~":
                    packetContents = packetContents + "}"
                    packetStarted = False

                    # If the packet is valid, then fire an event - if not report it through logging
                    try:
                        EventHandler.callEvent(Events.PACKET_RECEIVED, (literal_eval(packetContents), self.request.send))
                        packetContents = ""
                        packetContents = ""
                    except ValueError:
                        self.logger.error(packetContents)
                        self.logger.error("Malformed packet! - VALUE ERROR")
                        packetContents = ""
                        break
                    except SyntaxError:
                        self.logger.error(packetContents)
                        self.logger.error("Malformed packet! - SYNTAX ERROR")
                        packetContents = ""
                        break

                else:
                    packetContents = packetContents + receivedData

        self.request.close()
        #self.logger.debug("Disconnected from %s", self.client_address)

    def shutdown(self, data):
        self.running = False

class WebSocketServer():
    def __init__(self):
        self.logger = logging.getLogger(Config.LOGGING_NAME+".SocketServer")
        EventHandler.addListener("onQuitWebSocketServer", Events.SERVER_SHUTDOWN, self.stop)

        HOST = ('', 1998)

        self.server = socketserver.ThreadingTCPServer(HOST, WebRequestHandler)
        self.logger.info("Binding SocketServer to %s", HOST)

    def start(self):
        self.serverThread = Thread(target=self.loop)
        self.serverThread.setDaemon(True)
        self.serverThread.start()

    def stop(self, data):
        self.server.shutdown()
        self.logger.info("Shutting down the WebSocketServer...")

    def loop(self):
        self.logger.info("SocketServer started")
        self.server.serve_forever()