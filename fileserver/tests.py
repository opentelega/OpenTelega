# todo: Проверить AdminDidNotCreated
import time
import random

from django.test import TestCase

from fileserver.ResponseFormatWorker import ResponseFormat

from fileserver.TestWorker.ServerInitializationTest import \
    TestServerInitialization

from fileserver.TestWorker.OptionTest import \
    TestOptions

from fileserver.TestWorker.AdminChangePasswordTest import \
    TestAdminChangePassword

from fileserver.TestWorker.UserAdminControlTests import \
    TestUserAdminControl

from fileserver.TestWorker.FileOperationsTests import \
    TestFileCommands

from fileserver.TestWorker.ChangePasswordByUserTest import \
    TestChangePasswordByUser

from fileserver.TestWorker.GetVersionTests import \
    TestAdminGetVersion, TestUserGetVersion

def TestScenario(format=None):
    login, password = TestServerInitialization(format)
    print("Login: \"{}\"; Password: \"{}\"".format(login, password))
    TestOptions(login, password, format)
    newPassword = TestAdminChangePassword(login, password, format)
    print("New password: \"{}\"".format(newPassword))
    usersAfterDelete = TestUserAdminControl(login, newPassword, format)
    TestFileCommands(usersAfterDelete, (login, newPassword), format)
    randomUser = random.choice(tuple(usersAfterDelete.keys()))
    randomUserNewPassword = TestChangePasswordByUser(\
        randomUser, usersAfterDelete[randomUser], format)
    TestAdminGetVersion(login, newPassword, format)
    TestUserGetVersion(randomUser, randomUserNewPassword, format)



class TestScenarioDefault(TestCase):
    def test_default(self):
        TestScenario()

class TestScenarioXml(TestCase):
    def test_default(self):
        TestScenario(ResponseFormat.xml)

class TestScenarioJson(TestCase):
    def test_default(self):
        TestScenario(ResponseFormat.json)

class TestScenarioCsv(TestCase):
    def test_default(self):
        TestScenario(ResponseFormat.csv)