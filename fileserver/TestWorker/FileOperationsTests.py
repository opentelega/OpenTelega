from django.test import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

import os
from io import BytesIO
import random

from fileserver.HashCalc import HashSumType, hashsum_of_data
from fileserver.ResponseWorker import ResponseType
from fileserver.OutputTableHeader import OutputTableHeader
from fileserver.models import File, Option, User
from fileserver.OptionWorker import PublicOptionKey

from fileserver.TestWorker.AdminAuthTests import \
    CheckAdminAuthorization

from fileserver.AdminWorker import generate_random_chars, \
    CleanMediaDirectory

from fileserver.TestWorker.UserAuthTests import \
    CheckUserAuthorization

from fileserver.ResponseFormatWorker import DecodeOutputIntoTable, \
    GetFormatForHttpQuery

from fileserver.TestWorker.CommonFunctions import \
    IsCorrectStatusCodeResponse

def TestUploadFile(login, password, fileData, format=None):
    print("TestUploadFile...", end="")
    adress = 'fileserver:upload_file'

    params = {'userName': login, 'password': password,\
        'outputFormat': GetFormatForHttpQuery(format)}

    client = Client()
    CheckUserAuthorization(adress, format)

    firstParams = {}
    firstParams.update(params)
    firstParams.update({"recipients": login})
    firstResponse = client.post(reverse(adress), firstParams)

    assert(IsCorrectStatusCodeResponse(
        firstResponse, \
        ResponseType.UploadFileError,\
        format))

    secondParams = {}
    secondParams.update(params)
    secondParams.update({"uploadedFile": BytesIO(fileData)})
    secondResponse = client.post(reverse(adress), secondParams)

    assert(IsCorrectStatusCodeResponse(
        secondResponse, \
        ResponseType.NoRecipients,\
        format))

    wrongRecipient = generate_random_chars(10)
    thirdParams = {}
    thirdParams.update(params)
    thirdParams.update({"uploadedFile": BytesIO(fileData)})
    thirdParams.update({"recipients": wrongRecipient})
    thirdResponse = client.post(reverse(adress), thirdParams)

    assert(IsCorrectStatusCodeResponse(
        thirdResponse, \
        ResponseType.WrongRecipients,\
        format))

    fileInstance = File(uploaded_file=SimpleUploadedFile(\
        "binary.bin", fileData))
    fileInstance.save()
    fileInstance.sender = User.objects.get(username=login)
    fileInstance.save()
    fileId = fileInstance.id
    uploadedFile = File.objects.get(id=fileId)
    hashAlg = uploadedFile.hash_alg
    hashSum = uploadedFile.hash_sum
    calculatedHashSum = hashsum_of_data(HashSumType(hashAlg), fileData)
    assert(calculatedHashSum == hashSum)    
    print("OK")

def UploadTestFiles(users):
    print("UploadTestFiles...", end="")
    File.objects.all().delete()
    count = 20
    minSize = 1000
    maxSize = 1000000
    files = []
    for i in range(count):
        fileData = os.urandom(random.randint(minSize, maxSize))
        fileInstance = File(uploaded_file=SimpleUploadedFile(\
            "binary.bin", fileData))
        fileInstance.save()
        recipientsCount = len(users) - 4
        senderLogin = random.choice(list(users.keys()))
        recipients = random.sample(list(users.keys()), recipientsCount)
        for r in recipients:
            fileInstance.recipients.add(User.objects.get(username = r))
        fileInstance.sender = User.objects.get(username=senderLogin)
        fileInstance.save()
        files.append((fileInstance.id, senderLogin, recipients,\
            fileInstance.hash_alg, fileInstance.hash_sum))
    print("OK")
    return files

def find_user_without_permission(users, file):
    targetUsers = filter(lambda x: x not in file[2], users)
    return random.choice(targetUsers)

def TestAuthentification(format=None):
    userFunctionAdresses = ('fileserver:get_file_list',\
        'fileserver:download_file_by_id', 'fileserver:get_files_count')

    adminFunctionAdresses = ('fileserver:list_all_files', \
        'fileserver:admin_download_file', 'fileserver:delete_file')

    for u in userFunctionAdresses:
        CheckUserAuthorization(u, format)

    for a in adminFunctionAdresses:
        CheckAdminAuthorization(a, format)


def TestFiles(users, files, adminCredentials, format=None):
    print("TestFiles...", end="")
    TestAuthentification(format)
    print("OK")


def TestFileCommands(users, adminCredentials, format=None):
    randomData = os.urandom(10000)
    targetUser = random.choice(tuple(users.keys()))
    TestUploadFile(targetUser, users[targetUser], randomData, format)
    files = UploadTestFiles(users)
    targetFiles = random.sample(files, 5)
    TestFiles(users, targetFiles, adminCredentials, format)
    CleanMediaDirectory(None)