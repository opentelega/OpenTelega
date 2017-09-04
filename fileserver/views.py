from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from fileserver.UserWorker import GetUserFromPostRequest, \
    GetRecipientsFromPostRequest, GetUploadedFileFromPostRequest, \
    GetFileListByUser, GetFilesCountByUser, GetFileResponseFromPostRequest, \
    ChangePasswordFromPostRequest, SaveUploadedFile

from fileserver.ResponseWorker import ResponseByType, ResponseType

from fileserver.ResponseFormatWorker import GenerateOutput
from fileserver.OutputTableHeader import OutputTableHeader

@csrf_exempt
def upload_file(request):
    try:
        (getUserCode, user) = GetUserFromPostRequest(request)
        if (getUserCode != ResponseType.OK):
            return ResponseByType(getUserCode, request)

        (getRecipientsCode, recipients) = \
            GetRecipientsFromPostRequest(request)
        if (getRecipientsCode != ResponseType.OK):
            return ResponseByType(getRecipientsCode, request)

        (getFileCode, uploadedFile) = GetUploadedFileFromPostRequest(request)
        if (getFileCode != ResponseType.OK):
            return ResponseByType(getFileCode, request)

        (saveUploadedFileCode, fileId) = \
            SaveUploadedFile(uploadedFile, user, recipients)
        if (saveUploadedFileCode != ResponseType.OK):
            return ResponseByType(saveUploadedFileCode, request)

        header = OutputTableHeader.UploadFile.value
        data = ((str(fileId),),)
        return HttpResponse(GenerateOutput(header, data, request))
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def get_file_list(request):
    try:
        (getUserCode, user) = GetUserFromPostRequest(request)
        if (getUserCode != ResponseType.OK):
            return ResponseByType(getUserCode, request)

        (getFileListCode, fileList) = GetFileListByUser(request, user)
        if (getFileListCode != ResponseType.OK):
            return ResponseByType(getFileListCode, request)

        return HttpResponse(fileList)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def get_files_count(request):
    try:
        (getUserCode, user) = GetUserFromPostRequest(request)
        if (getUserCode != ResponseType.OK):
            return ResponseByType(getUserCode, request)

        (getFilesCountCode, count) = GetFilesCountByUser(user)
        if (getFilesCountCode != ResponseType.OK):
            return ResponseByType(getFilesCountCode, request)

        header = OutputTableHeader.GetNumberOfFiles.value
        data = ((str(count),),)
        return HttpResponse(GenerateOutput(header, data, request))
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def download_file_by_id(request):
    try:
        (getUserCode, user) = GetUserFromPostRequest(request)
        if (getUserCode != ResponseType.OK):
            return ResponseByType(getUserCode, request)

        (getFileResponseCode, fileResponse) = \
            GetFileResponseFromPostRequest(request, user)
        if (getFileResponseCode != ResponseType.OK):
            return ResponseByType(getFileResponseCode, request)

        return fileResponse
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def change_user_password(request):
    try:
        (getUserCode, user) = GetUserFromPostRequest(request)
        if (getUserCode != ResponseType.OK):
            return ResponseByType(getUserCode, request)

        changeNewPasswordCode = ChangePasswordFromPostRequest(request, user)
        return ResponseByType(changeNewPasswordCode, request)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def user_get_version(request):
    try:
        (getUserCode, user) = GetUserFromPostRequest(request)
        if (getUserCode != ResponseType.OK):
            return ResponseByType(getUserCode, request)

        header = OutputTableHeader.GetVersion.value
        data = (("1.0",),)
        outputTable = GenerateOutput(header, data, request)

        return HttpResponse(outputTable)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)