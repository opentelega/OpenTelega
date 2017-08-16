from django.http import HttpResponse

from fileserver.models import User, File, Option

from PTTpy.settings import MEDIA_ROOT

from fileserver.UserWorker import RegisterUser, ChangePassword, \
    GetCsvFileList, GetFileResponseByFile, GetUserByUserName

from fileserver.CsvGenerator import GenerateCsvString
from fileserver.ResponseWorker import ResponseType, ResponseByType
from fileserver.HashCalc import get_salted_password
from fileserver.ResponseFormatWorker import GenerateOutput

from fileserver.OptionWorker import UpdateOrCreateOption, GetOptionValue, \
    PublicOptionKey, PrivateOptionKey, UpdateOption, OptionExists

import base64
import os

FILE_SIZE_LIMIT = 1073741824 # 1 GB
LIMIT_MESSAGES_FOR_QUERY = 1000

def generate_random_chars(n):
    return str(base64.b64encode(os.urandom(n)).lower(), "utf-8")

def generate_salt():
    return generate_random_chars(128)

def GenerateAdmin():
    try:
        login = generate_random_chars(6)
        password = generate_random_chars(12)
        generatedSalt = generate_salt()
        hashedPass = get_salted_password(generatedSalt, password)

        loginCode = UpdateOrCreateOption(
            PrivateOptionKey.AdminLogin, login, False)
        if (loginCode != ResponseType.OK):
            return (loginCode, None)

        passCode = UpdateOrCreateOption(
            PrivateOptionKey.AdminHashedPassword, hashedPass, False)
        if (passCode != ResponseType.OK):
            return (passCode, None)

        saltCode = UpdateOrCreateOption(
            PrivateOptionKey.AdminSalt, generatedSalt, False)
        if (saltCode != ResponseType.OK):
            return (saltCode, None)

        return (ResponseType.OK, (login, password))
    except Exception:
        return (ResponseType.UnknownError, None)

def CheckAdmin(login, password):
    (loginCode, dbLogin) = GetOptionValue(
        PrivateOptionKey.AdminLogin)
    (passCode, dbPassword) = GetOptionValue(
        PrivateOptionKey.AdminHashedPassword)
    (saltCode, dbSalt) = GetOptionValue(
        PrivateOptionKey.AdminSalt)
    if not all(tuple(map(lambda x: x == ResponseType.OK, \
        (loginCode, passCode, saltCode)))):
        return ResponseType.AdminDidNotCreated

    hashedPass = get_salted_password(dbSalt, password)

    isValidLogin = (dbLogin == login)
    isValidPassword = (hashedPass == dbPassword)
    if not (isValidLogin & isValidPassword):
        return ResponseType.WrongCredentials
    return ResponseType.OK

def InitializeVariables():
    try:
        fileSizeLimitCode = UpdateOrCreateOption(
            PublicOptionKey.FileSizeLimit, str(FILE_SIZE_LIMIT))
        if (fileSizeLimitCode != ResponseType.OK):
            return fileSizeLimitCode

        limitMessagesForQueryCode = UpdateOrCreateOption(
            PublicOptionKey.LimitMessagesForQuery, \
            str(LIMIT_MESSAGES_FOR_QUERY))
        if (limitMessagesForQueryCode != ResponseType.OK):
            return limitMessagesForQueryCode

        isInitializedCode = UpdateOrCreateOption(
            PrivateOptionKey.IsInitialized, "True", False)
        if (isInitializedCode != ResponseType.OK):
            return isInitializedCode
    except Exception:
        return ResponseType.UnknownError
    return ResponseType.OK

def ChangeAdminPasswordFromPostRequest(request):
    try:
        newPassword = request.POST['newAdminPassword']
    except Exception:
        return ResponseType.CouldNotGetNewPassword

    generatedSalt = generate_salt()
    hashedPass = get_salted_password(generatedSalt, newPassword)

    passCode = UpdateOrCreateOption(
        PrivateOptionKey.AdminHashedPassword, hashedPass, False)
    if (passCode != ResponseType.OK):
        return passCode

    saltCode = UpdateOrCreateOption(
        PrivateOptionKey.AdminSalt, generatedSalt, False)
    if (saltCode != ResponseType.OK):
        return saltCode

    return ResponseType.OK

# Todo: Журнал
def CheckAdminFromPostRequest(request):
    try:
        userName = request.POST['adminUserName']
        password = request.POST['adminPassword']
    except Exception:
        return ResponseType.NoCredentials

    return CheckAdmin(userName, password)

def CreateUserFromPostRequest(request):
    try:
        try:
            username = request.POST['usernameForRegistration']
        except:
            return (ResponseType.NotEnoughArguments, None)

        password = generate_random_chars(12)

        registerUserCode = RegisterUser(username, password)
        if (registerUserCode != ResponseType.OK):
            return (registerUserCode, None)

        return (ResponseType.OK, password)
    except Exception:
        return (ResponseType.UnknownError, None)

def GetUsersList(request):
    users = tuple((user.username,) for user in User.objects.all())
    header = ("Username",)
    return GenerateOutput(header, users, request)

def ResetUserPasswordFromPostRequest(request):
    try:
        targetUserName = request.POST['usernameForResetPassword']
    except Exception:
        return (ResponseType.NotEnoughArguments, None)
    try:
        user = GetUserByUserName(targetUserName)
    except Exception:
        return (ResponseType.UserNotFound, None)

    newPassword = generate_random_chars(12)

    try:
        ChangePassword(user, newPassword)
    except:
        return (ResponseType.UnknownError, None)

    return (ResponseType.OK, newPassword)

def DeleteUserFromPostRequest(request):
    try:
        targetUserName = request.POST['usernameForDelete']
    except Exception:
        return ResponseType.NotEnoughArguments
    try:
        user = GetUserByUserName(targetUserName)
    except Exception:
        return ResponseType.UserNotFound

    try:
        user.delete()
    except Exception:
        return ResponseType.UnknownError
    return ResponseType.OK

def GetFileList(request):
    try:
        outputTable = GetCsvFileList(File.objects.all(), request)
        return (ResponseType.OK, outputTable)
    except Exception:
        return (ResponseType.GetFileListError, None)

def AdminDeleteFileFromPostRequest(request):
    try:
        targetId = request.POST['targetId']
    except Exception:
        return ResponseType.NotEnoughArguments

    try:
        targetFile = File.objects.get(id=targetId)
    except Exception:
        return ResponseType.FileNotFound

    try:
        targetFile.delete()
    except Exception:
        return ResponseType.UnknownError

    return ResponseType.OK

def AdminGetFileResponseFromPostRequest(request):
    try:
        targetId = request.POST['targetId']
    except Exception:
        return (ResponseType.NotEnoughArguments, None)

    try:
        targetFile = File.objects.get(id=targetId)
        response = GetFileResponseByFile(targetFile)
        return (ResponseType.OK, response)
    except Exception:
        return (ResponseType.FileNotFound, None)

def CleanMediaDirectory(request):
    filesForDeleteInDb = []
    dbFilesPaths = set()
    for f in File.objects.all():
        try:
            filePath = f.uploaded_file.path
            if not os.path.exists(filePath):
                filesForDeleteInDb.append(f)
            else:
                dbFilesPaths.add(filePath)
        except Exception:
            filesForDeleteInDb.append(f)

    mediaFolderFiles = (f for f in os.scandir(MEDIA_ROOT) if f.is_file())
    filesForDeleteInFs = [f for f in mediaFolderFiles \
        if f.path not in dbFilesPaths]

    deletedFilesFromDb = []
    errorsDuringDeleteFilesFromDb = []
    for f in filesForDeleteInDb:
        fileId = f.id
        try:
            f.delete()
            deletedFilesFromDb.append(fileId)
        except Exception:
            errorsDuringDeleteFilesFromDb.append(fileId)            

    deletedFilesInFs = []
    errorsDuringDeleteFilesInFs = []
    for f in filesForDeleteInFs:
        fileName = f.name
        try:
            os.remove(f.path)
            deletedFilesInFs.append(fileName)
        except Exception:
            errorsDuringDeleteFilesInFs.append(fileName)

    header = ("SuccessfullDeletedFilesFromDb",
        "DeleteFilesFromDbError",
        "SuccessfullDeletedFilesFromFs",
        "DeleteFilesFromFsError")

    contentData = (deletedFilesFromDb, errorsDuringDeleteFilesFromDb,
        deletedFilesInFs, errorsDuringDeleteFilesInFs)
    content = (tuple(map(GenerateCsvString, contentData)),)

    return GenerateOutput(header, content, request)