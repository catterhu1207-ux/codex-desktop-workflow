import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
from codex_desktop_workflow.isolated_run import IsolatedRun
from electron_update_safety import lifecycle

class IsolatedVisibility(unittest.TestCase):
 def test_current_debug_run_preserves_args_and_disables_background_throttling(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'codex-desktop-workflow-manifest.json').write_text(json.dumps({'package_version':'26.1007.9446.0'}))
   with patch.object(lifecycle.IsolatedRun,'start',return_value='owned-test') as start:
    self.assertEqual(IsolatedRun.start(root/'ChatGPT.exe',root/'runs',args=['--test-marker'],debug_port=1234),'owned-test')
    args=start.call_args.kwargs['args'];self.assertIn('--test-marker',args);self.assertIn('--disable-background-timer-throttling',args);self.assertIn('--disable-features=CalculateNativeWinOcclusion',args)
 def test_normal_launch_and_old_profile_keep_existing_arguments(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);metadata=root/'codex-desktop-workflow-manifest.json'
   for version,port in [('26.1007.9446.0',None),('26.928.4866.0',1234)]:
    metadata.write_text(json.dumps({'package_version':version}))
    with patch.object(lifecycle.IsolatedRun,'start',return_value='owned-test') as start:
     IsolatedRun.start(root/'ChatGPT.exe',root/'runs',args=['--test-marker'],debug_port=port)
     self.assertEqual(start.call_args.kwargs['args'],['--test-marker'])

if __name__=='__main__':unittest.main()
