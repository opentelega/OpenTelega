from django.test import Client
from django.urls import reverse

import random

from fileserver.OutputTableHeader import OutputTableHeader
from fileserver.ResponseWorker import ResponseType
from fileserver.models import Option
from fileserver.AdminWorker import generate_random_chars

from fileserver.ResponseFormatWorker import DecodeOutputIntoTable, \
    GetFormatForHttpQuery

from fileserver.TestWorker.CommonFunctions import \
    IsCorrectStatusCodeResponse

from fileserver.TestWorker.AdminAuthTests import \
    CheckAdminAuthorization

def TestOptions(login, password, format=None):
    print("TestOptions...", end="")
    adress = 'fileserver:get_options_list'
    params = {'adminUserName': login, 'adminPassword': password,\
        'outputFormat': GetFormatForHttpQuery(format)}

    client = Client()
    CheckAdminAuthorization(adress, format)

    firstOptionListResponse = client.post(\
        reverse(adress), params)
    assert(firstOptionListResponse.status_code == 200)

    firstOptionListResponseContent = \
        DecodeOutputIntoTable(\
            OutputTableHeader.GetOptionList.value, \
            firstOptionListResponse.content, format)

    optionName, optionValue = \
        random.choice(firstOptionListResponseContent)

    changeOptionAdress = 'fileserver:change_option'
    CheckAdminAuthorization(changeOptionAdress, format)

    firstChangeOptionResponse = client.post(\
        reverse(changeOptionAdress), params)

    assert(IsCorrectStatusCodeResponse(
        firstChangeOptionResponse, \
        ResponseType.NotEnoughArguments,\
        format))

    secondChangeOption = {'optionValue': generate_random_chars(10),\
        'optionName': 'adminPassword'}
    secondChangeOptionParams = {}
    secondChangeOptionParams.update(params)
    secondChangeOptionParams.update(secondChangeOption)
    secondChangeOptionResponse = client.post(\
        reverse(changeOptionAdress), \
        secondChangeOptionParams)

    assert(IsCorrectStatusCodeResponse(
        secondChangeOptionResponse, \
        ResponseType.CouldNotGetOption,\
        format))

    assert(Option.objects.get(name=optionName).value == optionValue)

    newOptionValue = generate_random_chars(10)
    thirdChangeOption = {'optionValue': newOptionValue,\
        'optionName': optionName}
    thirdChangeOptionParams = {}
    thirdChangeOptionParams.update(params)
    thirdChangeOptionParams.update(thirdChangeOption)
    thirdChangeOptionResponse = client.post(\
        reverse(changeOptionAdress), \
        thirdChangeOptionParams)

    assert(IsCorrectStatusCodeResponse(
        thirdChangeOptionResponse, \
        ResponseType.OK,\
        format))

    assert(Option.objects.get(name=optionName).value == \
        newOptionValue)
    print("OK")