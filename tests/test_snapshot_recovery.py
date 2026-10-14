import json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from codex_desktop_workflow import isolated_run

class SnapshotRecovery(unittest.TestCase):
    def make_run(self,root):
        run=object.__new__(isolated_run.IsolatedRun);run.run_directory=Path(root);return run

    def test_cancelled_cim_read_requires_a_fresh_successful_snapshot(self):
        with tempfile.TemporaryDirectory() as root:
            run=self.make_run(root)
            bad=subprocess.CompletedProcess([],1,'','HRESULT 0x80041032')
            good=subprocess.CompletedProcess([],0,json.dumps([{'ProcessId':77,'ParentProcessId':1,'ExecutablePath':'C:/synthetic/app.exe','CreationDate':'/Date(1000)/'}]),'')
            with patch.object(isolated_run.os,'name','nt'),patch.object(isolated_run,'run_awake',side_effect=[bad,good]) as capture:
                rows=run._snapshot()
            self.assertEqual(capture.call_count,2);self.assertEqual(rows[0].pid,77)
            self.assertEqual(len((Path(root)/'process-snapshot-retries.jsonl').read_text().splitlines()),1)

    def test_three_failures_remain_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            run=self.make_run(root);bad=subprocess.CompletedProcess([],1,'','read failed')
            with patch.object(isolated_run.os,'name','nt'),patch.object(isolated_run,'run_awake',return_value=bad) as capture:
                with self.assertRaisesRegex(RuntimeError,'failed_after_three_reads'):run._snapshot()
            self.assertEqual(capture.call_count,3)

    def test_empty_success_is_not_a_process_identity_proof(self):
        with tempfile.TemporaryDirectory() as root:
            run=self.make_run(root);empty=subprocess.CompletedProcess([],0,'[]','')
            with patch.object(isolated_run.os,'name','nt'),patch.object(isolated_run,'run_awake',return_value=empty):
                with self.assertRaisesRegex(RuntimeError,'failed_after_three_reads'):run._snapshot()
