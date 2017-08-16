from enum import Enum
from fileserver.CsvGenerator import GenerateCsvWithHeader
from fileserver.XmlWorker import GenerateXmlTable
from fileserver.JsonGenerator import GenerateJsonTable

class ResponseFormat(Enum):
    csv = 0
    xml = 1
    json = 2

def DetermineOutputFormat(request):
    try:
        return ResponseFormat[request.POST['outputFormat']]
    except Exception:
        return ResponseFormat.json

def GenerateOutput(header, data, request=None):
    format = DetermineOutputFormat(request)
    if (format == ResponseFormat.csv):
        return GenerateCsvWithHeader(header, data)
    elif (format == ResponseFormat.xml):
        return GenerateXmlTable(header, data)
    elif (format == ResponseFormat.json):
        return GenerateJsonTable(header, data)
