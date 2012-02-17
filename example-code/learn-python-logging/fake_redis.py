import logging


conn_log = logging.getLogger("redis.connection")

class StrictRedis(object):

    def __init__(self):
        self.state = {}
        self.connected = False

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def set(self, key, val):
        if not self.connected:
            self.connect = True
            conn_log.debug("Connected to redis")

        self.state[key] = val

