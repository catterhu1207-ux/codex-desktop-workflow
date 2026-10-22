import unittest
from unittest.mock import patch
from codex_desktop_workflow import windows_integrity as integrity


class IntegrityGate(unittest.TestCase):
    def test_low_file_is_rejected_even_with_normal_or_elevated_host(self):
        for host in (8192, 12288):
            with self.subTest(host=host), self.assertRaisesRegex(RuntimeError, 'executable_low_integrity'):
                integrity.require_desktop_integrity(4096, host)

    def test_low_host_is_not_repaired_by_changing_candidate_directory(self):
        with self.assertRaisesRegex(RuntimeError, 'host_low_integrity'):
            integrity.require_desktop_integrity(8192, 4096)

    def test_normal_candidate_keeps_security_settings(self):
        record = integrity.require_desktop_integrity(8192, 8192)
        self.assertEqual(record['status'], 'passed')
        self.assertFalse(record['security_settings_modified'])

    def test_unreadable_label_is_unknown_and_does_not_pass(self):
        with patch.object(integrity, 'executable_integrity', side_effect=OSError('unreadable')):
            with self.assertRaisesRegex(OSError, 'unreadable'):
                integrity.check_native_desktop('candidate.exe')

    def test_fresh_label_is_checked_on_every_launch(self):
        with patch.object(integrity, 'executable_integrity', side_effect=(8192, 4096)) as read, patch.object(integrity, 'process_integrity', return_value=8192):
            self.assertEqual(integrity.check_native_desktop('candidate.exe')['status'], 'passed')
            with self.assertRaisesRegex(RuntimeError, 'executable_low_integrity'):
                integrity.check_native_desktop('candidate.exe')
            self.assertEqual(read.call_count, 2)
