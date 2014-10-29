import socketserver
from eventhandler import EventHandler
from threading import Thread, current_thread
import logging
from config import *
from events import Events
from ast import literal_eval

class WebRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.logger = logging.getLogger(LOGGING_NAME+".SocketServer.RequestHandler")
        self.logger.info("Connection from %s", self.client_address)

        packetStarted = False
        packetContents = ""
        while True:
            receivedData = self.request.recv(1)
            if not receivedData: break  # If there is no dataz, then probably the client disconnected.
            try:
                receivedData = receivedData.decode("utf-8")
            except:
                continue

            if not packetStarted:       # If the packetStarted flag has not been set, set it when "{" is received
                if receivedData == "{":
                    packetStarted = True
                    packetContents = packetContents + receivedData
            elif packetStarted:         # If the packet has started, append stuff to it until "}" is received
                if receivedData == "}":
                    packetContents = packetContents + receivedData
                    packetStarted = False

                    # If the packet is valid, then fire an event - if not report it through logging
                    print(packetContents)

                    try:
                        EventHandler.callEvent(Events.PACKET_RECEIVED, (literal_eval(packetContents), self.request.send))
                        packetContents = ""
                    except ValueError:
                        self.logger.error("Malformed packet!")
                        packetContents = ""
                        continue
                    except SyntaxError:
                        self.logger.error("Malformed packet!")
                        packetContents = ""
                        continue

                else:
                    packetContents = packetContents + receivedData

        self.request.close()
        self.logger.info("Disconnected from %s", self.client_address)

class WebSocketServer():
    def __init__(self):
        self.logger = logging.getLogger(LOGGING_NAME+".SocketServer")

        HOST = ('', 1998)

        self.server = socketserver.ThreadingTCPServer(HOST, WebRequestHandler)
        self.logger.info("Binding SocketServer to %s", HOST)

    def start(self):
        self.serverThread = Thread(target=self.loop)
        self.serverThread.setDaemon(True)
        self.serverThread.start()

    def stop(self):
        self.server.shutdown()

    def loop(self):
        self.logger.info("SocketServer started")
        self.server.serve_forever()