import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from codex_desktop_workflow import update_awareness as awareness

class UpdateAwarenessTests(unittest.TestCase):
    def test_unknown_version_comparison_rejects_invalid_input(self):
        self.assertIsNone(awareness.version('26.1002.invalid.0'))
        self.assertGreater(awareness.version('26.1002.7124.0'),awareness.version('26.930.7945.0'))

    def test_absent_candidate_does_not_claim_readiness(self):
        self.assertIsNone(awareness.prepared_candidate(None))
        with tempfile.TemporaryDirectory() as tmp:
            current=Path(tmp)/'current';current.mkdir()
            other=Path(tmp)/'other';other.mkdir()
            (other/'codex-desktop-workflow-verification.json').write_text(json.dumps({'status':'passed'}))
            (other/'codex-desktop-workflow.json').write_text(json.dumps({'package_version':'26.1002.7124.0'}))
            self.assertIsNone(awareness.prepared_candidate(current))

    def test_unavailable_probe_preserves_previous_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache=Path(tmp)/'status.json';cache.write_bytes(b'previous verified cache')
            with patch.object(awareness,'fetch_package',return_value={'status':'unavailable'}),patch.object(awareness,'prepared_candidate',return_value=None),patch.object(awareness.urllib.request,'urlopen',side_effect=OSError('offline')):
                self.assertEqual(awareness.inspect(cache)['status'],'unavailable')
            self.assertEqual(cache.read_bytes(),b'previous verified cache')

    def test_package_availability_and_prepared_state_remain_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache=Path(tmp)/'status.json'
            package={'status':'manifest_verified','version':'26.930.7945.0'}
            prepared={'status':'adaptation_prepared','qualified':True,'version':'26.1002.7124.0'}
            with patch.object(awareness,'fetch_package',return_value=package),patch.object(awareness,'prepared_candidate',return_value=prepared),patch.object(awareness.urllib.request,'urlopen',side_effect=OSError('offline')):
                result=awareness.inspect(cache)
            self.assertEqual(result['last_status']['package']['version'],'26.930.7945.0')
            self.assertEqual(result['last_status']['prepared']['version'],'26.1002.7124.0')
            self.assertIsNone(result['last_status']['published_version'])

if __name__=='__main__':unittest.main()
