import unittest
from unittest.mock import Mock,patch
from codex_desktop_workflow import owned_verification as owned

class OwnedCleanup(unittest.TestCase):
    def test_exited_process_requires_fresh_empty_membership(self):
        job=Mock();job.pids.side_effect=[[42],[]]
        with patch.object(owned,'_owned_process_image',side_effect=OSError('already exited')):
            self.assertEqual(owned.owned_process_images(job),[])
        self.assertEqual(job.pids.call_count,2)

    def test_unreadable_process_still_owned_is_rejected(self):
        job=Mock();job.pids.return_value=[42]
        with patch.object(owned,'_owned_process_image',side_effect=OSError('access denied')):
            with self.assertRaisesRegex(RuntimeError,'identity_unavailable'):owned.owned_process_images(job)

    def test_failed_membership_refresh_is_not_an_exit(self):
        job=Mock();job.pids.side_effect=[[42],OSError('snapshot failed')]
        with patch.object(owned,'_owned_process_image',side_effect=OSError('unavailable')):
            with self.assertRaises(OSError):owned.owned_process_images(job)

    def test_live_identity_is_returned_for_qualification(self):
        job=Mock();job.pids.return_value=[42]
        with patch.object(owned,'_owned_process_image',return_value='C:/synthetic/unknown.exe'):
            self.assertEqual(owned.owned_process_images(job),[{'pid':42,'image':'C:/synthetic/unknown.exe'}])

if __name__=='__main__':unittest.main()
