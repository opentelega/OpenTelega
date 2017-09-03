from enum import Enum

class OutputTableHeader(Enum):
    StatusCode = ("StatusCode", )
    InitializeServer = ("AdminUsername", "AdminPassword")
    GetOptionList = ("Name", "Value")
    RegisterUser = ("UserPassword", )
    ResetUserPassword = ("UserPassword", )
    ListAllUsers = ("Username", )
    UploadFile = ("FileId", )
    GetFileList = ("Id", "Date", "Sender", "Recipients", "Hashsum", \
        "Algorithm", "Size")
    GetNumberOfFiles = ("FilesCount",)