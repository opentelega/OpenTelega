from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from fileserver.HashCalc import HashSumType, hashsum, hashsum_of_file
from fileserver.ResponseWorker import ResponseByType, ResponseType

from fileserver.AdminWorker import InitializeVariables, GenerateAdmin, \
    CheckAdminFromPostRequest, ChangeAdminPasswordFromPostRequest, \
    CreateUserFromPostRequest, ResetUserPasswordFromPostRequest, \
    DeleteUserFromPostRequest, GetUsersList, GetFileList, \
    AdminGetFileResponseFromPostRequest, AdminDeleteFileFromPostRequest, \
    CleanMediaDirectory

from fileserver.OptionWorker import IsInitialized, GetOptionList, \
    ChangeOptionFromPostRequest

from fileserver.ResponseFormatWorker import GenerateOutput
from fileserver.OutputTableHeader import OutputTableHeader

@csrf_exempt
def initialize_server(request):
    try:
        if IsInitialized():
            return ResponseByType(ResponseType.PermissionDenied, request)

        initializeVariablesCode = InitializeVariables()
        if (initializeVariablesCode != ResponseType.OK):
            return ResponseByType(initializeVariablesCode, request)

        (generateAdminCode, (login, password)) = GenerateAdmin()
        if (generateAdminCode != ResponseType.OK):
            return ResponseByType(generateAdminCode, request)

        header = OutputTableHeader.InitializeServer.value
        data = ((login, password),)
        outputTable = GenerateOutput(header, data, request)

        return HttpResponse(outputTable)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def change_admin_password(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        changeAdminPasswordCode = ChangeAdminPasswordFromPostRequest(request)
        if (changeAdminPasswordCode != ResponseType.OK):
            return ResponseByType(changeAdminPasswordCode, request)

        return ResponseByType(ResponseType.OK, request)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def register_user(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        (createUserCode, password) = CreateUserFromPostRequest(request)
        if (createUserCode != ResponseType.OK):
            return ResponseByType(createUserCode, request)

        header = OutputTableHeader.RegisterUser.value
        data = ((password,),)
        outputTable = GenerateOutput(header, data, request)

        return HttpResponse(outputTable)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def reset_user_password(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        (resetUserPasswordCode, password) = \
            ResetUserPasswordFromPostRequest(request)
        if (resetUserPasswordCode != ResponseType.OK):
            return ResponseByType(resetUserPasswordCode, request)

        header = OutputTableHeader.ResetUserPassword.value
        data = ((password,),)
        outputTable = GenerateOutput(header, data, request)

        return HttpResponse(outputTable)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def delete_user(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        deleteUserCode = DeleteUserFromPostRequest(request)
        if (deleteUserCode != ResponseType.OK):
            return ResponseByType(deleteUserCode, request)

        return ResponseByType(ResponseType.OK, request)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def list_all_users(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        usersList = GetUsersList(request)

        return HttpResponse(usersList)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def get_options_list(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        optionList = GetOptionList(request)

        return HttpResponse(optionList)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def change_option(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        changeOptionCode = ChangeOptionFromPostRequest(request)

        return ResponseByType(changeOptionCode, request)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def list_all_files(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        (getFileListCode, outputTable) = GetFileList(request)
        if (getFileListCode != ResponseType.OK):
            return ResponseByType(getFileListCode, request)

        return HttpResponse(outputTable)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def admin_download_file(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        (downloadCode, fileResponse) = \
            AdminGetFileResponseFromPostRequest(request)
        if (downloadCode != ResponseType.OK):
            return ResponseByType(downloadCode, request)

        return fileResponse
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def delete_file(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        deleteFileCode = AdminDeleteFileFromPostRequest(request)
        if (deleteFileCode != ResponseType.OK):
            return ResponseByType(deleteFileCode, request)

        return ResponseByType(ResponseType.OK, request)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def clean_media_directory(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        outputTable = CleanMediaDirectory(request)
        return HttpResponse(outputTable)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)

@csrf_exempt
def admin_get_version(request):
    try:
        checkAdminCode = CheckAdminFromPostRequest(request)
        if (checkAdminCode != ResponseType.OK):
            return ResponseByType(checkAdminCode, request)

        header = ("Version",)
        data = (("1.0",),)
        outputTable = GenerateOutput(header, data, request)

        return HttpResponse(outputTable)
    except Exception:
        return ResponseByType(ResponseType.UnknownError, request)