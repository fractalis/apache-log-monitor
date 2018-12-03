from asciimatics.event import KeyboardEvent
from asciimatics.widgets import Frame, Layout, Widget, Label, TextBox, MultiColumnListBox, Divider, VerticalDivider
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.exceptions import ResizeScreenError, StopApplication

from collections import defaultdict
from datetime import datetime
from pyparsing import ParseException

from alerts import Alerts
from config import Config
from metrics import Metrics
from parsing import buildBNF

import sys

class MonitorFrame(Frame):
    def __init__(self, screen):
        super(MonitorFrame, self).__init__(screen,
                                           screen.height,
                                           screen.width,
                                           has_border=False,
                                           name="Monitoring")
        self._last_frame = 0
        self._sort = 5
        self._reverse = True
        self._file_cur_pos = 0
        self._config = Config("config.yaml")
        #self._log_file = "/home/fractalis/repos/Fake-Apache-Log-Generator/access.log"
        self._log_file = self._config.getConfigValue("LOG_FILE")
        self._log_bnf = buildBNF()
        self._metrics = Metrics()
        self._alerts = Alerts()


        self._file = open(self._log_file)

        # Create layout
        layout = Layout([5,1,5,1,5], fill_frame=True)
        self._header = TextBox(1, as_string=True)
        self._header.disabled = True
        self._header.custom_colour = "header_colour"
        self._header.value = (str("Stats"))

        self._sections = MultiColumnListBox(
            10,
            [10, 10],
            [],
            titles=["Section", "Requests"],
            name="section_list"
        )
        self._ip_addr = MultiColumnListBox(
            10,
            [16, 10],
            [],
            titles=["IP Address", "Requests"],
            name="ip_addr_list"
        )

        self._auth = MultiColumnListBox(
            10,
            [10, 10],
            [],
            titles=["Auth", "Requests"],
            name="auth_list"
        )

        self._totalBytesSent = TextBox(1, as_string=True)
        self._totalBytesSent.disabled = True
        self._periodBytesSent = TextBox(1, as_string=True)
        self._periodBytesSent.disabled = True

        self._alertHeader = TextBox(1, as_string=True)
        self._alertHeader.disabled = True
        self._alertHeader.value = (str("Alerts"))

        self.add_layout(layout)

        self._layout = layout

        layout.add_widget(self._header)
        layout.add_widget(Divider())
        layout.add_widget(self._sections)
        layout.add_widget(Divider())
        layout.add_widget(self._ip_addr)
        layout.add_widget(VerticalDivider(), 1)
        layout.add_widget(self._auth, 2)
        layout.add_widget(Divider(), 2)
        layout.add_widget(self._periodBytesSent, 2)
        layout.add_widget(self._totalBytesSent, 2)
        layout.add_widget(VerticalDivider(), 3)
        layout.add_widget(self._alertHeader, 4)

        self.fix()

        self.palette = defaultdict(
            lambda: (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK))
        self.palette["header_colour"] = (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_BLACK)
        self.palette["title"] = (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE)

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            raise StopApplication("User quit")
        return super(MonitorFrame, self).process_event(event)

    def _update(self, frame_no):
        if frame_no - self._last_frame >= self.frame_update_count or self._last_frame == 0:
            self._last_frame = frame_no

            f = open(self._log_file)
            f.seek(self._file_cur_pos, 0)
            self._metrics.resetPeriodMetrics()
            self._metrics.resetMetrics("ipAddr")
            self._metrics.resetMetrics("uriSection")
            self._metrics.resetMetrics("auth")

            for line in f:
                try:
                    fields = self._log_bnf.parseString(line)
                    ipAddr = fields['ipAddr']
                    section = fields['requestURI'].split('/')[1]
                    bytesSent = fields['numBytesSent']
                    auth = fields['auth']

                    self._alerts.registerRequest(fields)


                    self._metrics.addMetricHit("ipAddr", ipAddr)
                    self._metrics.addMetricHit("uriSection", section)
                    self._metrics.addMetricHit("auth", auth)
                    self._metrics.registerRequest()
                    self._metrics.incBytesSent(int(bytesSent))

                except ParseException:
                    pass

            # Check for Alerts
            alert = self._alerts.checkForAlert()

            if alert == Alerts.ALERT_TRIGGERED:
                txtbox = TextBox(1, as_string=True)
                txtbox.disabled = True
                txtbox.value = "Alert: {0}".format(datetime.now())
                self._layout.add_widget(txtbox,4)
                self.fix()
            elif alert == Alerts.ALERT_CLEARED:
                txtbox = TextBox(1, as_string=True)
                txtbox.disabled = True
                txtbox.value = "Clear: {0}".format(datetime.now())
                self._layout.add_widget(txtbox,4)
                self.fix()


            # Update Section Data
            sectionData = self._metrics.getMetrics("uriSection")
            new_data = [
                ([
                    x[0],
                    str(x[1])
                ], x[0]) for x in sectionData
            ]
            self._sections.options = new_data

            # Update IP Address List
            ipAddr = self._metrics.getMetrics("ipAddr")
            new_data = [
                ([
                    x[0],
                    str(x[1])
                ], x[0]) for x in ipAddr
            ]
            self._ip_addr.options = new_data

            # Update Auth List
            auth = self._metrics.getMetrics("auth")
            new_data = [
                ([
                    x[0],
                    str(x[1])
                ], x[0]) for x in auth
            ]
            self._auth.options = new_data

            bytesSent = self._metrics.getBytesSent()
            self._totalBytesSent.value = "Total Bytes Sent: {0}".format(bytesSent[0])
            self._periodBytesSent.value = "Period Bytes Sent: {0}".format(bytesSent[1])

            # Update File Position
            self._file_cur_pos = f.seek(0,2)
            f.close()

        super(MonitorFrame,self)._update(frame_no)

    @property
    def frame_update_count(self):
        # Refresh every 10 seconds
        return 201

def run(screen):
    screen.play([Scene([MonitorFrame(screen)], -1)], stop_on_resize=True)

while True:
    try:
        Screen.wrapper(run, catch_interrupt=True)
        sys.exit(0)
    except ResizeScreenError:
        pass
