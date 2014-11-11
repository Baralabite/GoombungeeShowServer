from config import *
import time, threading, logging, random, string
from events import *
from eventhandler import *

class QueueManager:
    def __init__(self):
        self.queue = []

        self.currentPerson = ""
        self.currentPersonStartTime = 0

        self.logger = logging.getLogger(Config.LOGGING_NAME+".QueueManager")

    def processPerson(self):
        if len(self.queue) > 0:
            self.currentPerson = self.queue[0]
            self.currentPersonStartTime = round(time.time())
            threading.Timer(Config.CONTROL_TIME, self.endTurn).start()
            del self.queue[0]
            EventHandler.callEvent(Events.NEW_CLIENT_CONTROLLER, self.currentPerson)

    #Although unlikely, added in the while look to make sure that it never gets an ID
    #that's currently in the queue. That said, there's 1.7 * 10^48 possible combinations...
    def generateID(self):
        gen = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(6))
        if gen in self.queue:
            return self.generateID()
        else:
            self.logger.debug("Generated ID: %s"%gen)
            return gen


    def addToQueue(self, id):
        if id in self.queue:
            self.logger.warn("Person with ID %s tried to queue again"%id)
            return False
        else:
            self.queue.append(id)
            if self.currentPerson == "":
                self.processPerson()
            self.logger.info("Person queued with ID %s"%id)
            return True

    def endTurn(self):
        EventHandler.callEvent(Events.CLIENT_TIME_UP, self.currentPerson)
        self.currentPerson = ""
        self.currentPersonStartTime = 0
        self.processPerson()

    def getCurrentPerson(self):
        return self.currentPerson

    def getCurrentPersonRemainingTime(self):
        return Config.CONTROL_TIME - (round(time.time())-self.currentPersonStartTime)

    def getTimeUntilTurn(self, id):
        try:
            return self.queue.index(id)*30 + self.getCurrentPersonRemainingTime() + 1
        except:
            return -1

    def isTurn(self, id):
        return self.currentPerson == id or id == "MASTER"

    def getPlaceInQueue(self, id):
        try:
            return self.queue.index(id)+1
        except:
            return "None"

