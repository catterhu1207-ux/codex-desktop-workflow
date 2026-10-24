"""Require current-source evidence; historical release proof stays immutable."""
import ast,hashlib,json,unittest
from pathlib import Path
import codex_desktop_workflow
PACKAGE=Path(codex_desktop_workflow.__file__).parent
SOURCE=PACKAGE.parent
ROOT=Path(__file__).resolve().parents[1]
HISTORICAL='qualification-26.1016.8622.0.json'
METADATA_BEFORE=b'"""Public Codex desktop workflow adaptation entry point."""\n\n__version__ = "0.3.12"\n\n'

def release_metadata_only_proof(before,after):
    """Only the exact retained release constant may differ from its old bytes."""
    before=before.replace(b'\r\n',b'\n');after=after.replace(b'\r\n',b'\n')
    if before!=METADATA_BEFORE or after!=before.replace(b'__version__ = "0.3.12"',b'__version__ = "0.3.13"',1):
        raise ValueError('unexpected_release_metadata_source_change')
    old_tree,new_tree=ast.parse(before),ast.parse(after)
    old_assignments=[node for node in old_tree.body if isinstance(node,ast.Assign)]
    new_assignments=[node for node in new_tree.body if isinstance(node,ast.Assign)]
    if len(old_assignments)!=1 or len(new_assignments)!=1:
        raise ValueError('unexpected_release_metadata_ast')
    old,new=old_assignments[0],new_assignments[0]
    if (len(new.targets)!=1 or not isinstance(new.targets[0],ast.Name) or new.targets[0].id!='__version__'
            or not isinstance(old.value,ast.Constant) or not isinstance(new.value,ast.Constant)
            or old.value.value!='0.3.12' or new.value.value!='0.3.13'):
        raise ValueError('unexpected_release_metadata_ast')
    new.value.value='0.3.12'
    if ast.dump(old_tree,include_attributes=False)!=ast.dump(new_tree,include_attributes=False):
        raise ValueError('release_metadata_other_ast_changed')
    return {'status':'passed','path':'codex_desktop_workflow/__init__.py','constant':'__version__',
        'before_version':'0.3.12','after_version':'0.3.13','before_sha256':hashlib.sha256(before).hexdigest(),
        'after_sha256':hashlib.sha256(after).hexdigest(),'remaining_bytes_unchanged':True,'remaining_ast_unchanged':True}

def digest(p):
    raw=p.read_bytes()
    return hashlib.sha256(raw if p.suffix=='.bin' else raw.replace(b"\r\n",b"\n")).hexdigest()

HISTORICAL_SHA='31f52274f5d5aaddebd6b305420789ed5d5ae67dee0dcdd911d39526bb783cd0'

class HistoricalMetadataProofTests(unittest.TestCase):
    def test_release_metadata_only_accepts_exact_version_constant(self):
        after=METADATA_BEFORE.replace(b'0.3.12',b'0.3.13')
        proof=release_metadata_only_proof(METADATA_BEFORE,after)
        self.assertTrue(proof['remaining_bytes_unchanged'])
        self.assertTrue(proof['remaining_ast_unchanged'])

    def test_release_metadata_only_rejects_other_source_changes(self):
        after=METADATA_BEFORE.replace(b'0.3.12',b'0.3.13')
        for invalid in (after+b'EXTRA=True\n',after.replace(b'entry point',b'changed entry'),
                        after.replace(b'0.3.13',b'0.3.14'),after.replace(b'__version__',b'other_name'),
                        after.replace(b' = ',b'='),METADATA_BEFORE):
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                release_metadata_only_proof(METADATA_BEFORE,invalid)
        with self.assertRaises(ValueError):release_metadata_only_proof(METADATA_BEFORE+b'# changed\n',after)


class ReleaseQualification(unittest.TestCase):
    def test_historical_release_evidence_remains_immutable(self):
        path=PACKAGE/'policies'/HISTORICAL
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),HISTORICAL_SHA)
        value=json.loads(path.read_text())
        self.assertEqual(value['status'],'passed')
        self.assertEqual(value['desktop_version'],'26.1016.8622.0')
        self.assertEqual(value['package_version'],'0.3.13')
        self.assertEqual(set(value['tested_artifacts']),{'official','compat','installed_wheel'})
        self.assertEqual(value['browser_isolation']['native_runs'],4)

    def test_current_source_has_complete_public_runtime_acceptance(self):
        from codex_desktop_workflow.release_sources import CURRENT,validate_current,source_inventory
        path=PACKAGE/'policies'/CURRENT
        self.assertTrue(path.is_file(),'Current release feature qualification is incomplete')
        value=json.loads(path.read_text())
        self.assertEqual(value['source_inputs'],source_inventory())
        self.assertEqual(validate_current(path,value)['status'],'passed')
        self.assertEqual(value['package_version'],codex_desktop_workflow.__version__)
        for kind in ('official','compat'):
            for profile in ('empty','synthetic_tasks'):
                proof=value['runtime_matrix'][kind][profile]
                self.assertRegex(proof['receipt_sha256'],r'^[0-9a-f]{64}$')
            self.assertEqual(value['native_ui'][kind]['first_send_cases'],6)
            self.assertEqual(value['native_ui'][kind]['cold_reopened_chats'],6)
        budget=value['background_history_budget']
        self.assertEqual(set(budget['callers']),{'prediction','ephemeral_metadata'})
        self.assertEqual(budget['maximum_history_bytes'],1073741824)
        self.assertFalse(budget['history_modified'])
        self.assertEqual(value['legacy_profile_regressions']['26.1016.8622.0']['status'],'passed')

    def test_current_distribution_is_separately_qualified(self):
        name='qualification-distribution-v'+codex_desktop_workflow.__version__+'.json'
        path=PACKAGE/'policies'/name
        self.assertTrue(path.is_file(),'Current distribution qualification is incomplete')
        value=json.loads(path.read_text())
        self.assertEqual(value['status'],'passed')
        self.assertEqual(value['package_version'],codex_desktop_workflow.__version__)
        self.assertEqual(value['installed_wheel']['status'],'passed')
        self.assertEqual(value['source_bundle']['status'],'passed')
        self.assertEqual(set(value['installer_dry_runs']),{'official','compat_manifest','compat_source'})
        for item in value['installer_dry_runs'].values():
            self.assertEqual(item['status'],'passed')
            self.assertFalse(item['compiled_or_started'])
        self.assertEqual(value['privacy_scan']['status'],'passed')
