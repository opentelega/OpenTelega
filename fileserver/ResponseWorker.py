from django.http import HttpResponse, HttpResponseBadRequest
from enum import Enum
from fileserver.ResponseFormatWorker import GenerateOutput

class ResponseType(Enum):
    OK = 0
    NoCredentials = 1
    WrongCredentials = 2
    InvalidParameters = 3
    UploadFileError = 4
    FileSizeExceedsLimit = 5
    WrongRecipients = 6
    NoRecipients = 7
    FileNotFound = 8
    GetFileListError = 9
    NoFileId = 10
    CouldNotGetNewPassword = 11
    AdminDidNotCreated = 12
    CouldNotGetOption = 13
    UserNotFound = 14
    PermissionDenied = 15
    NotEnoughArguments = 16
    AlreadyRegistredUser = 17
    DbWorkingError = 18
    UnknownError = 19

def ResponseByType(responseType, request):
    header = ("StatusCode", )
    value = ((responseType.name,),)
    output = GenerateOutput(header, value, request)
    if (responseType == ResponseType.OK):
        return HttpResponse(output)
    else:
        return HttpResponseBadRequest(output)