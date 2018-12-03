from datetime import datetime

from config import Config

PARSE_TIME = "%d/%b/%Y:%H:%M:%S"

CONFIG = Config("config.yaml")

def filterRequests(request):
    now = datetime.now()
    timestamp = datetime.strptime(request['timestamp'][0], PARSE_TIME)

    diff = now - timestamp
    return diff.seconds <= CONFIG.getConfigValue("ALERT_TIME_PERIOD")

class Alerts(object):

    ALERT_TRIGGERED = 0
    ALERT_CLEARED = 1
    ALERT_NONE = 2

    def __init__(self):
        self._requests = []
        self._alert_triggered = False

    def getRequests(self):
        return self._requests

    def registerRequest(self, request):
        self._requests.append(request)

    def checkForAlert(self):
        self._requests = list(filter(filterRequests, self._requests))

        if len(self._requests) >= CONFIG.getConfigValue("ALERT_THRESHOLD") and not self._alert_triggered:
            self._alert_triggered = True
            return self.ALERT_TRIGGERED
        elif len(self._requests) < CONFIG.getConfigValue("ALERT_THRESHOLD") and self._alert_triggered:
            self._alert_triggered = False
            return self.ALERT_CLEARED
        else:
            return self.ALERT_NONE
