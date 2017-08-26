from django.test import Client
from django.urls import reverse

from fileserver.AdminWorker import CheckAdmin
from fileserver.ResponseWorker import ResponseType
from fileserver.ResponseFormatWorker import GetFormatForHttpQuery
from fileserver.OptionWorker import PrivateOptionKey
from fileserver.models import Option
from fileserver.AdminWorker import generate_random_chars

from fileserver.TestWorker.AdminAuthTests import \
    CheckAdminAuthorization

from fileserver.TestWorker.CommonFunctions import \
    IsCorrectStatusCodeResponse

def TestAdminChangePassword(login, password, format=None):
    print("TestAdminChangePassword...", end="")
    adress = 'fileserver:change_admin_password'
    params = {'adminUserName': login, 'adminPassword': password,\
        'outputFormat': GetFormatForHttpQuery(format)}

    client = Client()
    CheckAdminAuthorization(adress, format)

    firstChangePasswordResponse = client.post(reverse(adress), params)
    assert(IsCorrectStatusCodeResponse(
        firstChangePasswordResponse, \
        ResponseType.CouldNotGetNewPassword,\
        format))

    privateOption = Option.objects.get(\
        name=PrivateOptionKey.AdminSalt.value)
    privateOption.is_accessible = True
    privateOption.save()

    secondChangePasswordParams = {}
    secondChangePasswordParams.update(params)
    secondChangePasswordParams.update(\
        {"newAdminPassword": generate_random_chars(10)})
    secondChangePasswordResponse = client.post(reverse(adress), \
        secondChangePasswordParams)

    assert(IsCorrectStatusCodeResponse(
        secondChangePasswordResponse, \
        ResponseType.PermissionDenied,\
        format))

    assert(CheckAdmin(login, password) == ResponseType.OK)

    privateOption.is_accessible = False
    privateOption.save()

    newPassword = generate_random_chars(10)
    thirdChangePasswordParams = {}
    thirdChangePasswordParams.update(params)
    thirdChangePasswordParams.update({"newAdminPassword": newPassword})
    thirdChangePasswordResponse = client.post(reverse(adress), \
        thirdChangePasswordParams)

    assert(CheckAdmin(login, newPassword) == ResponseType.OK)

    assert(IsCorrectStatusCodeResponse(
        thirdChangePasswordResponse, \
        ResponseType.OK,\
        format))

    print("OK")
    return newPassword