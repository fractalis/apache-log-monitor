from alerts import Alerts
from config import Config
from datetime import datetime

CONFIG = Config("config.yaml")
ALERT_THRESHOLD = CONFIG.getConfigValue("ALERT_THRESHOLD")
TIME_FORMAT = "%d/%b/%Y:%H:%M:%S"


def test_register_request():
    alerts = Alerts()
    for i in range(0,ALERT_THRESHOLD):
        alerts.registerRequest({"timestamp": datetime.strftime(datetime.now(), TIME_FORMAT)})
    assert len(alerts.getRequests()) == ALERT_THRESHOLD

def test_trigger_alert():
    alerts = Alerts()
    for i in range(0,ALERT_THRESHOLD):
        request = {"timestamp": [datetime.strftime(datetime.now(), TIME_FORMAT)]}
        alerts.registerRequest(request)
    assert(alerts.checkForAlert() == Alerts.ALERT_TRIGGERED)

def test_alert_clear():
    alerts = Alerts()
    for i in range(0, ALERT_THRESHOLD):
        request = {"timestamp": [datetime.strftime(datetime.now(), TIME_FORMAT)]}
        alerts.registerRequest(request)
    assert(alerts.checkForAlert() == Alerts.ALERT_TRIGGERED)

    # Simulate clearing old requests
    alerts._requests = []
    assert(alerts.checkForAlert() == Alerts.ALERT_CLEARED)

    # Test subsequent checkForAlert returns ALERT_NONE
    assert(alerts.checkForAlert() == Alerts.ALERT_NONE)
