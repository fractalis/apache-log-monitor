from pyparsing import alphas, nums, dblQuotedString, Combine, Word, Group, delimitedList, Suppress, removeQuotes
import string

def getFields(s,l,t):
    t["method"], t["requestURI"], t["protocolVersion"] = t[0].strip('"').split()

def buildBNF():

    integer = Word(nums)
    ipAddress = delimitedList(integer, ".", combine=True)

    timeZoneOffset = Word("+-", nums)
    month = Word(string.ascii_uppercase, string.ascii_lowercase, exact=3)
    serverDateTime = Group(Suppress("[") +
                           Combine( integer + "/" + month + "/" + integer +
                                   ":" + integer + ":" + integer + ":" + integer ) +
                           timeZoneOffset +
                           Suppress("]"))

    loglineBNF = (ipAddress.setResultsName("ipAddr") +
                  Suppress("-") +
                  ("-" | Word(alphas+nums+"@._")).setResultsName("auth") +
                  serverDateTime.setResultsName("timestamp") +
                  dblQuotedString.setResultsName("cmd").setParseAction(getFields) +
                  (integer | "-").setResultsName("statusCode") +
                  (integer | "-").setResultsName("numBytesSent"))

    return loglineBNF
