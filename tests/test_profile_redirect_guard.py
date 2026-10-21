"""The documented Python 3.11 minimum must retain the isolation boundary."""
from pathlib import Path
import stat,tempfile,unittest
from types import SimpleNamespace
from unittest.mock import Mock
from codex_desktop_workflow.isolated_run import _redirected


class ProfileRedirectGuard(unittest.TestCase):
    def test_normal_and_not_yet_created_directory(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertFalse(_redirected(Path(root)))
            self.assertFalse(_redirected(Path(root)/'not-created'))

    def test_windows_junction_requires_only_lstat(self):
        # Path.is_junction was introduced in Python 3.12:
        # https://docs.python.org/3/library/pathlib.html#pathlib.Path.is_junction
        path=SimpleNamespace(lstat=lambda:SimpleNamespace(st_mode=stat.S_IFDIR,st_file_attributes=0x400))
        self.assertTrue(_redirected(path))

    def test_symbolic_link_without_windows_attributes(self):
        path=SimpleNamespace(lstat=lambda:SimpleNamespace(st_mode=stat.S_IFLNK))
        self.assertTrue(_redirected(path))

    def test_access_error_cannot_be_misread_as_safe(self):
        path=SimpleNamespace(lstat=Mock(side_effect=PermissionError('unreadable')))
        with self.assertRaises(PermissionError):_redirected(path)
