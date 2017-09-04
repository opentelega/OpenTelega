from django.test import Client
from django.urls import reverse

from fileserver.ResponseWorker import ResponseType
from fileserver.AdminWorker import generate_random_chars
from fileserver.UserWorker import CheckUser

from fileserver.ResponseFormatWorker import DecodeOutputIntoTable, \
    GetFormatForHttpQuery

from fileserver.TestWorker.CommonFunctions import \
    IsCorrectStatusCodeResponse

def TestChangePasswordByUser(login, password, format=None):
    print("TestChangePasswordByUser...", end="")
    adress = 'fileserver:change_user_password'
    client = Client()

    params = {'userName': login, \
        'password': password, \
        'outputFormat': GetFormatForHttpQuery(format)}

    firstResponse = client.post(reverse(adress), params)

    assert(IsCorrectStatusCodeResponse(
        firstResponse, \
        ResponseType.CouldNotGetNewPassword,\
        format))

    newPassword = generate_random_chars(10)
    secondParams = {}
    secondParams.update(params)
    secondParams["newPassword"] = newPassword
    secondResponse = client.post(reverse(adress), secondParams)

    assert(IsCorrectStatusCodeResponse(
        secondResponse, \
        ResponseType.OK,\
        format))

    assert(CheckUser(login, newPassword))
    print("OK")
    return newPassword