from unittest.mock import Mock

def get_mock_db():
    mock_root = Mock()
    mock_root.users = {}
    mock_root.admins = {}
    mock_root.menus = {}
    return mock_root