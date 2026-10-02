from pathlib import Path
import importlib.util
import os
import queue
import sys
import tempfile
import unittest
from unittest.mock import Mock,patch

spec=importlib.util.spec_from_file_location('backend_awake_io',Path(__file__).resolve().parents[1]/'tools/backend/awake_io.py')
io=importlib.util.module_from_spec(spec);spec.loader.exec_module(io)

class BackendAwake(unittest.TestCase):
    def test_short_queue_timeouts_do_not_exhaust_awake_deadline(self):
        messages=Mock();messages.get.side_effect=[queue.Empty(),queue.Empty(),{'id':7}]
        with patch.object(io,'seconds',side_effect=[0,.1,.2]):
            self.assertEqual(io.message(messages,1),{'id':7})

    def test_elapsed_awake_budget_still_rejects_missing_message(self):
        messages=Mock()
        with patch.object(io,'seconds',return_value=2):
            with self.assertRaises(TimeoutError):io.message(messages,1)
        messages.get.assert_not_called()

    @unittest.skipUnless(os.name=='nt','Windows isolated process')
    def test_real_process_output_does_not_block(self):
        with tempfile.TemporaryDirectory() as root:
            env=os.environ.copy();env['CODEX_ACCEPTANCE_OUTPUT']=root
            result=io.run([sys.executable,'-c',"print('x'*100000)"],cwd=root,env=env,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(len(result.stdout.strip()),100000)

if __name__=='__main__':unittest.main()
