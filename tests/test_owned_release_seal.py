import unittest
from pathlib import Path
from unittest import mock
from codex_desktop_workflow.owned_verification import _seal_closed_runtime

class CurrentReleaseSeal(unittest.TestCase):
    def sample(self,version='26.1016.6573.0'):
        return {'bundle':{'package_version':version},'runtime':[{'run_directory':'owned-fixture','pre_close':{'main':{'pid':123}}}]}
    def test_new_version_reads_closed_logs_and_seals_unchanged_inputs(self):
        value=self.sample();bindings={'candidate':'synthetic'}
        def seal(_,v):v['qualification_bindings']=bindings
        with mock.patch('codex_desktop_workflow.renderer_proof.parse_owned_logs',return_value={'status':'passed'}) as parser,mock.patch('codex_desktop_workflow.qualification.seal',side_effect=seal) as sealed:
            _seal_closed_runtime(Path('portable'),value,'26.1016.6573.0',bindings)
            parser.assert_called_once();sealed.assert_called_once()
        self.assertEqual(value['closed_log_readback'],'passed')
    def test_late_renderer_failure_cannot_be_sealed(self):
        value=self.sample()
        with mock.patch('codex_desktop_workflow.renderer_proof.parse_owned_logs',return_value={'status':'blocked'}),mock.patch('codex_desktop_workflow.qualification.seal') as sealed:
            with self.assertRaisesRegex(RuntimeError,'final_closed_renderer_proof_rejected'):
                _seal_closed_runtime(Path('portable'),value,'26.1016.6573.0',{})
            sealed.assert_not_called()
    def test_source_change_during_successful_run_is_rejected(self):
        value=self.sample()
        def seal(_,v):v['qualification_bindings']={'source':'after'}
        with mock.patch('codex_desktop_workflow.renderer_proof.parse_owned_logs',return_value={'status':'passed'}),mock.patch('codex_desktop_workflow.qualification.seal',side_effect=seal):
            with self.assertRaisesRegex(RuntimeError,'inputs_changed_during_run'):
                _seal_closed_runtime(Path('portable'),value,'26.1016.6573.0',{'source':'before'})
    def test_worker_cannot_select_an_older_gate(self):
        with self.assertRaisesRegex(RuntimeError,'verification_package_version_changed'):
            _seal_closed_runtime(Path('portable'),self.sample('26.915.3509.0'),'26.1016.6573.0',{})

if __name__=='__main__':unittest.main()
