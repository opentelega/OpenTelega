from django.test import Client
from django.urls import reverse

from fileserver.OutputTableHeader import OutputTableHeader

from fileserver.TestWorker.AdminAuthTests import \
    CheckAdminAuthorization

from fileserver.TestWorker.UserAuthTests import \
    CheckUserAuthorization

from fileserver.ResponseFormatWorker import DecodeOutputIntoTable, \
    GetFormatForHttpQuery


def TestAdminGetVersion(login, password, format=None):
    print("TestAdminGetVersion...", end="")
    adress = 'fileserver:admin_get_version'
    params = {'adminUserName': login, 'adminPassword': password,\
        'outputFormat': GetFormatForHttpQuery(format)}

    client = Client()
    CheckAdminAuthorization(adress, format)

    response = client.post(reverse(adress), params)
    version = DecodeOutputIntoTable(\
        OutputTableHeader.GetVersion.value, \
        response.content, format)[0][0]

    assert(version == "1.0")
    print("OK")

def TestUserGetVersion(login, password, format=None):
    print("TestUserGetVersion...", end="")
    adress = 'fileserver:user_get_version'
    params = {'userName': login, 'password': password,\
        'outputFormat': GetFormatForHttpQuery(format)}

    client = Client()
    CheckUserAuthorization(adress, format)

    response = client.post(reverse(adress), params)
    version = DecodeOutputIntoTable(\
        OutputTableHeader.GetVersion.value, \
        response.content, format)[0][0]

    assert(version == "1.0")
    print("OK")