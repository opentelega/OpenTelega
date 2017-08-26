from django.test import Client
from django.urls import reverse

from fileserver.OutputTableHeader import OutputTableHeader
from fileserver.models import Option
from fileserver.ResponseWorker import ResponseType

from fileserver.ResponseFormatWorker import GetFormatForHttpQuery, \
    DecodeOutputIntoTable

from fileserver.TestWorker.CommonFunctions import \
    IsCorrectStatusCodeResponse

def TestServerInitialization(format=None):
    print("TestServerInitialization...", end="")
    formatStr = GetFormatForHttpQuery(format)
    Option.objects.all().delete()
    client = Client()

    response = \
        client.post(reverse('fileserver:initialize_server'), \
            {'outputFormat': formatStr})
    assert(response.status_code == 200)

    responseContent = \
        DecodeOutputIntoTable(\
            OutputTableHeader.InitializeServer.value, \
            response.content, format)
    assert(len(responseContent) == 1)
    assert(len(responseContent[0]) == 2)

    # Второй раз инициализировать сервер нельзя
    secondResponse = \
        client.post(reverse('fileserver:initialize_server'), \
            {'outputFormat': formatStr})
    assert(IsCorrectStatusCodeResponse(\
        secondResponse, ResponseType.PermissionDenied, format))

    login = responseContent[0][0]
    password = responseContent[0][1]

    print("OK")
    return (login, password)