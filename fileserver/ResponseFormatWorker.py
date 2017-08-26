from enum import Enum

from fileserver.CsvGenerator import GenerateCsvWithHeader, \
    ConvertCsvIntoTable

from fileserver.XmlWorker import GenerateXmlTable, \
    ConvertXmlIntoTable

from fileserver.JsonGenerator import GenerateJsonTable, \
    DecodeJsonIntoTable

class ResponseFormat(Enum):
    csv = 0
    xml = 1
    json = 2

DEFAULT_FORMAT = ResponseFormat.json

def DetermineOutputFormat(request):
    try:
        return ResponseFormat[request.POST['outputFormat']]
    except Exception:
        return DEFAULT_FORMAT

def GetFormatForHttpQuery(format):
    try:
        determinedFormat = ResponseFormat(format)
    except Exception:
        return "Unknown"
    return determinedFormat.name

def GenerateOutput(header, data, request=None):
    format = DetermineOutputFormat(request)
    if (format == ResponseFormat.csv):
        return GenerateCsvWithHeader(header, data)
    elif (format == ResponseFormat.xml):
        return GenerateXmlTable(header, data)
    elif (format == ResponseFormat.json):
        return GenerateJsonTable(header, data)

def DecodeOutputIntoTable(header, output, format=None):
    try:
        determinedFormat = ResponseFormat(format)
    except Exception:
        determinedFormat = DEFAULT_FORMAT

    if (determinedFormat == ResponseFormat.csv):
        return ConvertCsvIntoTable(output, header)
    elif (determinedFormat == ResponseFormat.xml):
        return ConvertXmlIntoTable(output, header)
    elif (determinedFormat == ResponseFormat.json):
        return DecodeJsonIntoTable(output, header)

