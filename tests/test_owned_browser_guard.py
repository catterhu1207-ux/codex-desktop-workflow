import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from codex_desktop_workflow import owned_verification as owned


class OwnedBrowserGuard(unittest.TestCase):
    def exercise(self, *, check_error=None, close_error=None, start_error=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        portable = root / 'app'
        portable.mkdir()
        (portable / 'codex-desktop-workflow-manifest.json').write_text(json.dumps({'package_version': 'synthetic-unsealed'}))
        job, worker, guard = Mock(), Mock(), Mock()
        job.pids.return_value = []
        worker.poll.side_effect = [None, 0, 0]
        worker.returncode = 0
        guard.check.side_effect = check_error
        guard.close.side_effect = close_error
        guard.close.return_value = {'status': 'passed', 'before_during_after_unchanged': True}
        guard.start.side_effect = start_error
        def popen(command, **_):
            request = Path(command[-1])
            (request.parent / 'result.json').write_text(json.dumps({'runtime': [], 'bundle': {'package_version': 'synthetic-unsealed'}}))
            return worker
        with patch.object(owned, 'SpaceJob', return_value=job), \
             patch.object(owned.subprocess, 'Popen', side_effect=popen) as launch, \
             patch.object(owned, 'owned_process_images', return_value=[]), \
             patch.object(owned.time, 'sleep'), \
             patch('codex_desktop_workflow.browser_isolation.SharedBrowserGuard', return_value=guard):
            try:
                value = owned.verify_owned(root, portable, root / 'runs', 60, 2)
                error = None
            except BaseException as caught:
                value, error = None, caught
        return portable, job, worker, guard, launch, value, error

    def test_parent_observes_before_during_and_after_worker_and_seals_guard_result(self):
        portable, job, _, guard, _, value, error = self.exercise()
        self.assertIsNone(error)
        guard.start.assert_called_once()
        self.assertGreaterEqual(guard.check.call_count, 2)
        guard.close.assert_called_once()
        self.assertEqual(value['browser_isolation']['status'], 'passed')
        job.close.assert_called_once()
        self.assertTrue((portable / 'codex-desktop-workflow-verification.json').is_file())

    def test_shared_change_closes_only_owned_job_and_never_writes_success(self):
        portable, job, _, _, _, value, error = self.exercise(check_error=RuntimeError('shared_browser_changed'))
        self.assertIn('shared_browser_changed', str(error))
        self.assertIsNone(value)
        job.close.assert_called_once()
        self.assertFalse((portable / 'codex-desktop-workflow-verification.json').exists())

    def test_final_readback_failure_cannot_seal_passed_worker(self):
        portable, job, _, _, _, _, error = self.exercise(close_error=RuntimeError('late_browser_change'))
        self.assertIn('late_browser_change', str(error))
        job.close.assert_called_once()
        self.assertFalse((portable / 'codex-desktop-workflow-verification.json').exists())

    def test_monitor_start_failure_does_not_launch_or_replace_original_error(self):
        portable, job, _, guard, launch, _, error = self.exercise(start_error=RuntimeError('registry_watch_denied'))
        self.assertIn('registry_watch_denied', str(error))
        launch.assert_not_called()
        guard.close.assert_not_called()
        job.close.assert_called_once()
        self.assertFalse((portable / 'codex-desktop-workflow-verification.json').exists())


if __name__ == '__main__':
    unittest.main()
