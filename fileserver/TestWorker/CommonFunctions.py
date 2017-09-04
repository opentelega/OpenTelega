from fileserver.ResponseWorker import ResponseType
from fileserver.OutputTableHeader import OutputTableHeader

from fileserver.ResponseFormatWorker import DecodeOutputIntoTable

def IsCorrectStatusCodeResponse(response, statusCode, format=None):
    try:
        if (statusCode == ResponseType.OK):
            assert(response.status_code == 200)
        else:
            assert(response.status_code == 400)
        decodedStatusCodeTable = DecodeOutputIntoTable(\
            OutputTableHeader.StatusCode.value, \
            response.content, format)
        assert(len(decodedStatusCodeTable) == 1)
        assert(len(decodedStatusCodeTable[0]) == 1)

        decodedStatusCode = decodedStatusCodeTable[0][0]
        assert(ResponseType[decodedStatusCode] == statusCode)
        return True
    except Exception:
        return False