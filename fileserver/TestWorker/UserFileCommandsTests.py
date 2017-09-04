from django.test import Client
from django.urls import reverse

import random

from fileserver.ResponseWorker import ResponseType
from fileserver.OutputTableHeader import OutputTableHeader
from fileserver.HashCalc import HashSumType, hashsum_of_data

from fileserver.ResponseFormatWorker import DecodeOutputIntoTable, \
    GetFormatForHttpQuery

from fileserver.TestWorker.CommonFunctions import \
    IsCorrectStatusCodeResponse

def TestGetFileListByUser(users, files, format):
    print("TestGetFileListByUser...", end="")
    adress = 'fileserver:get_file_list'
    randomUser = random.choice(tuple(users.keys()))
    randomUserFiles = filter(\
        lambda f: randomUser in f[2], files)
    randomUserFilesId = set(map(lambda f: str(f[0]), randomUserFiles))

    params = {'userName': randomUser, 'password': users[randomUser],\
        'outputFormat': GetFormatForHttpQuery(format)}

    client = Client()

    response = client.post(reverse(adress), params)

    successfullCommand = not IsCorrectStatusCodeResponse(\
        response,\
        ResponseType.GetFileListError,\
        format)
   
    if (successfullCommand):
        fileList = DecodeOutputIntoTable(\
            OutputTableHeader.GetFileList.value, \
            response.content, format)

        filesIdInResponse = set(map(lambda f: f[0], fileList))
        assert(randomUserFilesId == filesIdInResponse)

    print("OK")


def TestGetFilesNumber(users, files, format):
    print("TestGetFilesNumber...", end="")
    adress = 'fileserver:get_files_count'

    randomUser = random.choice(tuple(users.keys()))
    randomUserFiles = list(filter(\
        lambda f: randomUser in f[2], files))

    params = {'userName': randomUser, 'password': users[randomUser],\
        'outputFormat': GetFormatForHttpQuery(format)}

    client = Client()

    response = client.post(reverse(adress), params)

    numberOfFileTable = DecodeOutputIntoTable(\
            OutputTableHeader.GetNumberOfFiles.value, \
            response.content, format)

    assert(len(randomUserFiles) == int(numberOfFileTable[0][0]))

    print("OK")

def TestDownLoadFileByUser(users, files, format):
    print("TestDownLoadFileByUser...", end="")
    adress = 'fileserver:download_file_by_id'
    randomUser = random.choice(tuple(users.keys()))
    permittedFiles = list(filter(\
        lambda f: randomUser in f[2], files))
    permittedFilesId = set(map(lambda f: str(f[0]), permittedFiles))
    allFilesId = set(map(lambda f: str(f[0]), files))

    forbiddenFilesId = allFilesId - permittedFilesId

    permittedFile = random.choice(permittedFiles)
    permittedId = permittedFile[0]
    params = {'userName': randomUser, 'password': users[randomUser],\
        'outputFormat': GetFormatForHttpQuery(format)}

    # Проверяем скачивание файла случайным адресатом файла
    firstParams = {}
    firstParams.update(params)
    firstParams['id'] = permittedId

    client = Client()
    firstResponse = client.post(reverse(adress), firstParams)

    fileData = firstResponse.content
    hashAlg = permittedFile[3]
    calculatedHashSum = hashsum_of_data(HashSumType(hashAlg), fileData)
    assert(calculatedHashSum == permittedFile[4])

    # Проверяем невозможность скачивания файла левым пользователем
    secondParams = {}
    secondParams.update(params)
    forbiddenId = random.choice(list(forbiddenFilesId))
    secondParams['id'] = forbiddenId
    secondResponse = client.post(reverse(adress), secondParams)

    assert(IsCorrectStatusCodeResponse(\
        secondResponse,\
        ResponseType.FileNotFound,\
        format))

    print("OK")

def TestUserFileCommands(users, files, format=None):
    TestGetFileListByUser(users, files, format)
    TestGetFilesNumber(users, files, format)
    TestDownLoadFileByUser(users, files, format)
