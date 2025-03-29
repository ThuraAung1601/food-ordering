from unittest.mock import Mock

class MockTransaction:
    @staticmethod
    def commit():
        pass

    @staticmethod
    def abort():
        pass

transaction = MockTransaction()

class MockRoot:
    def __init__(self):
        self.menus = {}
        self.users = {}
        self.admins = {}

root = MockRoot()