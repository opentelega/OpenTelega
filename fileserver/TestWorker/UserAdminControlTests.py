from django.test import Client
from django.urls import reverse

import random
import base64
import os

from fileserver.ResponseWorker import ResponseType
from fileserver.OutputTableHeader import OutputTableHeader
from fileserver.UserWorker import CheckUser
from fileserver.models import User

from fileserver.TestWorker.CommonFunctions import \
    IsCorrectStatusCodeResponse

from fileserver.ResponseFormatWorker import DecodeOutputIntoTable, \
    GetFormatForHttpQuery

from fileserver.TestWorker.AdminAuthTests import \
    CheckAdminAuthorization

def CheckUserExistance(login):
    return login.lower() not in \
        [user.username for user in User.objects.all()]

def generate_random_login(nbyte):
    return str(base64.b32encode(os.urandom(nbyte)).lower(), "utf-8")

def GetPasswordFromResponse(response, format=None):
    content = DecodeOutputIntoTable(\
        OutputTableHeader.RegisterUser.value, \
        response.content, format)
    assert(len(content) == 1)
    assert(len(content[0]) == 1)
    return str(content[0][0])

def CheckUsersByDict(userDict):
    for user in userDict.keys():
        validUser = CheckUser(user, userDict[user])
        if not validUser:
            return False
    return True

def TestUserRegistration(login, password, format=None):
    print("TestUserRegistration...", end="")
    adress = 'fileserver:register_user'

    params = {'adminUserName': login, 'adminPassword': password,\
        'outputFormat': GetFormatForHttpQuery(format)}

    client = Client()
    CheckAdminAuthorization(adress, format)

    firstResponse = client.post(reverse(adress), params)

    assert(IsCorrectStatusCodeResponse(
        firstResponse, \
        ResponseType.NotEnoughArguments,\
        format))

    users = {}

    for i in range(10):
        username = generate_random_login(5)
        secondParams = {}
        secondParams.update(params)
        secondParams["usernameForRegistration"] = username
        secondResponse = client.post(reverse(adress), secondParams)
        userPassword = GetPasswordFromResponse(secondResponse, format)
        users[username] = userPassword

    invalidLogin = generate_random_login(5) + ":-("
    thirdParams = {}
    thirdParams.update(params)
    thirdParams["usernameForRegistration"] = invalidLogin
    thirdResponse = client.post(reverse(adress), thirdParams)

    assert(IsCorrectStatusCodeResponse(
        thirdResponse, \
        ResponseType.InvalidParameters,\
        format))

    assert(CheckUserExistance(invalidLogin))

    existedLogin = random.choice(tuple(users.keys())).upper()
    fourthParams = {}
    fourthParams.update(params)
    fourthParams["usernameForRegistration"] = existedLogin
    fourthResponse = client.post(reverse(adress), fourthParams)

    assert(IsCorrectStatusCodeResponse(
        fourthResponse, \
        ResponseType.AlreadyRegistredUser,\
        format))

    assert(CheckUsersByDict(users))
    print("OK")
    return users

def TestUserResetPassword(login, password, users, format=None):
    print("TestUserResetPassword...", end="")
    adress = 'fileserver:reset_user_password'
    CheckAdminAuthorization(adress, format)

    params = {'adminUserName': login, 'adminPassword': password,\
        'outputFormat': GetFormatForHttpQuery(format)}

    client = Client()
    usersAfterResetPassword = {}
    usersAfterResetPassword.update(users)
    targetUserLogin = random.choice(\
        tuple(usersAfterResetPassword.keys()))

    firstResponse = client.post(reverse(adress), params)

    assert(IsCorrectStatusCodeResponse(
        firstResponse, \
        ResponseType.NotEnoughArguments,\
        format))

    invalidLogin = generate_random_login(5)
    secondParams = {}
    secondParams.update(params)
    secondParams["usernameForResetPassword"] = invalidLogin
    secondResponse = client.post(reverse(adress), secondParams)

    assert(IsCorrectStatusCodeResponse(
        secondResponse, \
        ResponseType.UserNotFound,\
        format))

    assert(CheckUserExistance(invalidLogin))

    thirdParams = {}
    thirdParams.update(params)
    thirdParams["usernameForResetPassword"] = targetUserLogin
    thirdResponse = client.post(reverse(adress), thirdParams)
    newPassword = GetPasswordFromResponse(thirdResponse, format)
    usersAfterResetPassword[targetUserLogin] = newPassword
    assert(CheckUsersByDict(usersAfterResetPassword))
    print("OK")
    return usersAfterResetPassword

def TestDeleteUser(login, password, users, format=None):
    print("TestDeleteUser...", end="")
    adress = 'fileserver:delete_user'
    CheckAdminAuthorization(adress, format)

    params = {'adminUserName': login, 'adminPassword': password,\
        'outputFormat': GetFormatForHttpQuery(format)}

    client = Client()
    usersAfterDelete = {}
    usersAfterDelete.update(users)
    targetUserLogin = random.choice(tuple(usersAfterDelete.keys()))
    firstResponse = client.post(reverse(adress), params)

    assert(IsCorrectStatusCodeResponse(
        firstResponse, \
        ResponseType.NotEnoughArguments,\
        format))

    invalidLogin = generate_random_login(5)
    secondParams = {}
    secondParams.update(params)
    secondParams["usernameForDelete"] = invalidLogin
    secondResponse = client.post(reverse(adress), secondParams)

    assert(IsCorrectStatusCodeResponse(
        secondResponse, \
        ResponseType.UserNotFound,\
        format))

    thirdParams = {}
    thirdParams.update(params)
    thirdParams["usernameForResetPassword"] = targetUserLogin.upper()
    thirdResponse = client.post(reverse(adress), thirdParams)

    assert(not CheckUserExistance(targetUserLogin))
    del usersAfterDelete[targetUserLogin]
    assert(CheckUsersByDict(usersAfterDelete))
    print("OK")
    return usersAfterDelete

def TestListAllUsers(login, password, users, format=None):
    print("TestListAllUsers...", end="")
    adress = 'fileserver:list_all_users'
    CheckAdminAuthorization(adress, format)

    params = {'adminUserName': login, 'adminPassword': password,\
        'outputFormat': GetFormatForHttpQuery(format)}

    client = Client()
    response = client.post(reverse(adress), params)

    content = DecodeOutputIntoTable(\
        OutputTableHeader.ListAllUsers.value, \
        response.content, format)

    assert(all(map(lambda username: username in \
        map(lambda responseUserRow: responseUserRow[0], content), \
        users.keys())))
    print("OK")

def TestUserAdminControl(login, password, format=None):
    users = TestUserRegistration(login, password, format=None)

    usersAfterResetPassword = \
        TestUserResetPassword(login, password, users, format=None)

    usersAfterDelete = TestDeleteUser(login, password, \
        usersAfterResetPassword, format=None)

    TestListAllUsers(login, password, usersAfterDelete)

    return usersAfterDelete