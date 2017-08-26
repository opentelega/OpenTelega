from django.test import Client
from django.urls import reverse

from fileserver.AdminWorker import generate_random_chars
from fileserver.ResponseFormatWorker import GetFormatForHttpQuery
from fileserver.ResponseWorker import ResponseType

from fileserver.TestWorker.CommonFunctions import \
    IsCorrectStatusCodeResponse

def CheckAdminAuthorization(relationAdress, format=None):
    client = Client()
    incorrectLogin = generate_random_chars(10)
    incorrectPassword = generate_random_chars(10)
    outputFormat = GetFormatForHttpQuery(format)

    credentialsSet = ({}, {'adminUserName': incorrectLogin}, 
        {'adminPassword': incorrectPassword})

    wrongCredentialsParams = {'adminUserName': incorrectLogin, \
        'adminPassword': incorrectPassword, \
        'outputFormat': outputFormat}

    for credentials in credentialsSet:
        params = {}
        params.update(credentials)
        params.update({'outputFormat': outputFormat})

        noCredentialsResponse = \
            client.post(reverse(relationAdress), params)

        assert(IsCorrectStatusCodeResponse(
            noCredentialsResponse, \
            ResponseType.NoCredentials, \
            format))

    wrongCredentialsResponse = \
        client.post(reverse(relationAdress), wrongCredentialsParams)

    assert(IsCorrectStatusCodeResponse(
        wrongCredentialsResponse, \
        ResponseType.WrongCredentials,\
        format))