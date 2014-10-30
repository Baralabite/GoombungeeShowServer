import logging
from config import *

class EventHandler:
    listeners = {}
    logger = logging.getLogger(Config.LOGGING_NAME+".EventHandler")

    def addListener(name, event, callback):
        if not event in EventHandler.listeners: EventHandler.listeners[event] = {}

        EventHandler.listeners[event][name] = callback

    def callEvent(event, data):
        #EventHandler.logger.debug("Event %s: %s", event, data)
        if not event in EventHandler.listeners: EventHandler.listeners[event] = {}

        for listener in EventHandler.listeners[event]:
            EventHandler.listeners[event][listener](data)