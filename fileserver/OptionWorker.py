from fileserver.models import Option
from fileserver.ResponseWorker import ResponseType
from fileserver.ResponseFormatWorker import GenerateOutput
from fileserver.OutputTableHeader import OutputTableHeader

from enum import Enum

class PublicOptionKey(Enum):
    FileSizeLimit = "FILE_SIZE_LIMIT"
    LimitMessagesForQuery = "LIMIT_MESSAGES_FOR_QUERY"

class PrivateOptionKey(Enum):
    IsInitialized = "is_initialized"
    AdminLogin = "admin_login"
    AdminHashedPassword = "admin_hashed_password"
    AdminSalt = "admin_salt"

def CheckAdminOptionsAccessibility():
    try:
        adminLoginIsAccessible = Option.objects.get(\
            name = PrivateOptionKey.AdminLogin.value).is_accessible

        adminHashedPasswordIsAccessible = Option.objects.get(\
            name=PrivateOptionKey.AdminHashedPassword.value).is_accessible

        adminSaltIsAccessible = Option.objects.get(\
            name=PrivateOptionKey.AdminSalt.value).is_accessible
    except Exception:
        ResponseType.CouldNotGetOption

    isAccessible = adminLoginIsAccessible | \
        adminHashedPasswordIsAccessible | adminSaltIsAccessible

    if not (isAccessible):
        return ResponseType.OK
    else:
        return ResponseType.PermissionDenied

def OptionExists(optionName):
    try:
        Option.objects.get(name=optionName)
        return True
    except Option.DoesNotExist:
        return False

def IsInitialized():
    return OptionExists(PrivateOptionKey.IsInitialized.value)

def GetOptionValue(optionName):
    try:
        opt = Option.objects.get(name=optionName.value).value
        return (ResponseType.OK, opt)
    except Exception:
        return (ResponseType.CouldNotGetOption, None)

def GetOptionObject(optionName):
    try:
        optObj = Option.objects.get(name=optionName)
        return (ResponseType.OK, optObj)
    except Exception:
        return (ResponseType.CouldNotGetOption, None)

def UpdateOption(optionName, optionValue):
    try:
        targetOption = Option.objects.filter(
            is_accessible=True).get(name=optionName)
    except Exception:
        return ResponseType.CouldNotGetOption

    targetOption.value = optionValue
    targetOption.save()

    return ResponseType.OK

def UpdateOrCreateOption(optionName, optionValue, optionAccessible=True):
    try:
        optObj = Option.objects.get(name=optionName.value)
        if (optObj.is_accessible != optionAccessible):
            return ResponseType.PermissionDenied
    except Option.DoesNotExist:
        optObj = Option(name=optionName.value, is_accessible=optionAccessible)

    optObj.value = optionValue
    optObj.save()

    return ResponseType.OK

def GetOptionList(request):
    options = Option.objects.filter(is_accessible=True)
    header = OutputTableHeader.GetOptionList.value
    optionForTable = tuple((o.name, o.value) for o in options)
    return GenerateOutput(header, optionForTable, request)

def ChangeOptionFromPostRequest(request):
    try:
        optionName = request.POST['optionName']
        optionValue = request.POST['optionValue']
    except Exception:
        return ResponseType.NotEnoughArguments

    updateOptionCode = UpdateOption(optionName, optionValue)
    return updateOptionCode