from django.http import HttpResponse

from fileserver.models import User, File

import base64
import os

from fileserver.HashCalc import HashSumType, hashsum, hashsumOfPassword, \
    get_salted_password
from fileserver.ResponseWorker import ResponseType
from fileserver.OptionWorker import GetOptionValue, PublicOptionKey
from fileserver.ResponseFormatWorker import GenerateOutput

def generate_rand():
    return str(base64.b64encode(os.urandom(128)).lower(), "utf-8")

def get_sender_from_file(fileObj):
    try:
        return fileObj.sender.username
    except:
        return "#unknown_sender#"

def report_bad_file(fileId):
    pass

def GetCsvFileList(files, request=None):
    headers = ("Id", "Date", "Sender", "Recipients", \
        "Hashsum", "Algorithm", "Size")
    fileList = []
    for f in files:
        try:
            fileList.append((f.id, f.date_of_creating, \
                get_sender_from_file(f), f.get_recipients(), f.hash_sum, \
                HashSumType(f.hash_alg).name, f.uploaded_file.size,))
        except Exception:
            report_bad_file(f.id)

    return GenerateOutput(headers, fileList, request)

def ChangePassword(user, newPassword):
    generatedSalt = generate_rand()
    hashedPass = get_salted_password(generatedSalt, newPassword)
    user.salt = generatedSalt
    user.hashed_pass = hashedPass
    user.save()

def CheckUser(userName, password):
    try:
        user = User.objects.get(username = userName.lower())
        return user.CheckPassword(password)
    except Exception:
        return False

def GetUserByUserName(userName):
    return User.objects.get(username = userName.lower())

def GetUsersByUserNames(userNames):
    userNameList = userNames.lower().split(";")
    return tuple(User.objects.get(username = un) for un in userNameList)

def RegisterUser(userName, password):
    dbUserName = userName.lower()
    allowedChars = "abcdefghijklmnopqrstuvwxyz0123456789-_"
    if not all(map(lambda x: x in allowedChars, dbUserName)):
        return ResponseType.InvalidParameters
    try:
        existedUser = User.objects.get(username=dbUserName)
        return ResponseType.AlreadyRegistredUser 
    except:
        pass
    generatedSalt = generate_rand()
    hashedPass = get_salted_password(generatedSalt, password)
    User(username = dbUserName,
        salt = generatedSalt, hashed_pass = hashedPass).save()
    return ResponseType.OK

def GetRecipientsFromPostRequest(request):
    try:
        recipientsRawString = request.POST['recipients']
    except Exception:
        return (ResponseType.NoRecipients, None)

    try:
        recipients = GetUsersByUserNames(recipientsRawString)
    except Exception:
        return (ResponseType.WrongRecipients, None)

    return (ResponseType.OK, recipients)
    
def GetUserFromPostRequest(request):
    try:
        userName = request.POST['userName']
        password = request.POST['password']
    except Exception:
        return (ResponseType.NoCredentials, None)

    if not CheckUser(userName, password):
        return (ResponseType.WrongCredentials, None)

    try:
        user = GetUserByUserName(userName)
    except Exception:
        return (ResponseType.UnknownError, None)

    return (ResponseType.OK, user)

def ChangePasswordFromPostRequest(request, user):
    try:
        newPassword = request.POST['newPassword']
    except Exception:
        return ResponseType.CouldNotGetNewPassword

    try:
        ChangePassword(user, newPassword)
    except:
        return ResponseType.UnknownError

    return ResponseType.OK


def GetUploadedFileFromPostRequest(request):
    try:
        uploadedFile = request.FILES['uploadedFile']
    except Exception:
        return (ResponseType.UploadFileError, None)

    (fileSizeLimitCode, fileSizeLimit) = \
        GetOptionValue(PublicOptionKey.FileSizeLimit)
    if (fileSizeLimitCode != ResponseType.OK):
        return (fileSizeLimitCode, None)

    if (uploadedFile.size > int(fileSizeLimit)):
        return (ResponseType.FileSizeExceedsLimit, None)

    return (ResponseType.OK, uploadedFile)

def GetFileListByUser(request, user):
    startFromId = 0
    if ('startFromId' in request.POST):
        try:
            startFromId = int(request.POST['startFromId'])
        except Exception:
            return (ResponseType.InvalidParameters, None)

    try:
        (limitMessagesForQueryCode, limitMessagesForQuery) = \
            GetOptionValue(PublicOptionKey.LimitMessagesForQuery)
        if (limitMessagesForQueryCode != ResponseType.OK):
            return (limitMessagesForQueryCode, None)
        files = File.objects.filter(recipients=user).filter(
            id__gte=startFromId)[:int(limitMessagesForQuery)]
        outputTable = GetCsvFileList(files, request)
        return (ResponseType.OK, outputTable)
    except Exception:
        return (ResponseType.GetFileListError, None)

def GetFilesCountByUser(user):
    try:
        count = str(len(File.objects.filter(recipients=user)))
        return (ResponseType.OK, count)
    except Exception:
        return (ResponseType.InvalidParameters, None)

def GetFileResponseByFile(targetFile):
    filename = str(targetFile.id)
    response = HttpResponse(targetFile.uploaded_file)
    response['Content-Disposition'] = \
        "attachment; filename={}".format(filename)
    return response

def GetFileResponseFromPostRequest(request, user):
    try:
        try:
            fileId = request.POST['id']
        except KeyError:
            return (ResponseType.NoFileId, None)
        f = File.objects.filter(recipients=user).get(id=fileId)
        response = GetFileResponseByFile(f)
        return (ResponseType.OK, response)
    except Exception:
        return (ResponseType.FileNotFound, None)

def SaveUploadedFile(uploadedFile, user, recipients):
    try:
        fileInstance = File(uploaded_file=uploadedFile)
        fileInstance.save()
        fileInstance.sender = user
        for recipient in recipients:
            fileInstance.recipients.add(recipient)
        fileInstance.save()
        return (ResponseType.OK, fileInstance.id)
    except Exception:
        return (ResponseType.DbWorkingError, None)