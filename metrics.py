class Metrics:
    def __init__(self):
        self.sectionHits = {}
        self.totalRequests = 0
        self.totalPeriodRequests = 0
        self.metrics = {}
        self.totalBytesSent = 0
        self.periodBytesSent = 0

    def registerRequest(self):
        self.totalRequests = self.totalRequests + 1
        self.totalPeriodRequests += 1

    def addMetricHit(self, metric_name, metric_key):
        if not metric_name in self.metrics.keys():
            self.metrics[metric_name] = {}
        if not metric_key in self.metrics[metric_name]:
            self.metrics[metric_name][metric_key] = 1
        else:
            self.metrics[metric_name][metric_key] += 1

    def getMetrics(self, metric_name):
        list_data = []
        for metric_key in self.metrics[metric_name].keys():
            list_data.append([metric_key, self.metrics[metric_name][metric_key]])
        return list_data

    def resetMetrics(self, metric_name):
        self.metrics[metric_name] = {}

    def incBytesSent(self, bytesSent):
        self.totalBytesSent += bytesSent
        self.periodBytesSent += bytesSent

    def getBytesSent(self):
        return (self.totalBytesSent, self.periodBytesSent)

    def resetPeriodMetrics(self):
        self.sectionHits = {}
        self.totalPeriodRequests = 0
        self.periodBytesSent = 0

    def outputMetrics(self):
        for key in self.sectionHits.keys():
            print("Section: {0} Requests: {1}".format(key, self.sectionHits[key]))
        print("---")
        print("Total Period Requests: {0}".format(self.totalPeriodRequests))
        print("Total Requests: {0}".format(self.totalRequests))
        print("Total Bytes Sent: {0}".format(self.totalBytesSent))
        print("Period Bytes Sent: {0}".format(self.periodBytesSent))
