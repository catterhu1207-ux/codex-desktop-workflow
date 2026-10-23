"""A new installed release cannot qualify without an unchanged browser boundary."""
import copy
import unittest
from codex_desktop_workflow.qualification import require_browser_isolation,require_complete

class BrowserQualificationGate(unittest.TestCase):
    def value(self):
        return {'browser_isolation':{'status':'passed','before_during_after_unchanged':True,
                'samples':3,'registry_views':['32','64'],'automatic_restore':False}}

    def test_observed_unchanged_boundary_passes(self):
        require_browser_isolation(self.value())

    def test_absent_or_failed_browser_evidence_rejected(self):
        changes=[('status','failed'),('before_during_after_unchanged',False),
                 ('samples',0),('samples',True),('samples','3'),('registry_views',['64']),
                 ('registry_views',['32','64','64']),('automatic_restore',True)]
        for key,value in changes:
            with self.subTest(field=key,value=value):
                record=self.value();record['browser_isolation'][key]=value
                with self.assertRaisesRegex(ValueError,'public_browser_isolation_not_complete'):
                    require_browser_isolation(record)
        with self.assertRaisesRegex(ValueError,'public_browser_isolation_not_complete'):
            require_browser_isolation({})

    def test_installed_current_release_uses_browser_gate_before_release_record(self):
        value={'status':'passed','closed_log_readback':'passed','owned_cleanup':{'owned_job_empty':True}}
        with self.assertRaisesRegex(ValueError,'public_browser_isolation_not_complete'):
            require_complete(value,{'package_version':'26.1016.8622.0'})

if __name__=='__main__':unittest.main()
