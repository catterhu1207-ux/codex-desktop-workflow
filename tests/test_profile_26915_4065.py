"""Execute the real new bundle and reject behavioral regressions."""
from pathlib import Path
import os,unittest
import hotfix_builder as b
import hotfix_profile_26915_4065 as p
from frontend_feature_contracts import ContractError
from frontend_contract_26915_4065 import require_feature_signatures,require_routes,run_semantics,run_protocol,run_drop
from frontend_work_contract_26915_4065 import run as run_work,PICKER_PATH

class ExactProfile4065(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value=os.environ.get('CODEX_WORKFLOW_TEST_ASAR')
        if not value:raise unittest.SkipTest('Set CODEX_WORKFLOW_TEST_ASAR to a locally built 4065 artifact')
        path=Path(value)
        if not path.is_file():raise RuntimeError('Explicit artifact does not exist')
        h,_,meta=b.read_asar(path)
        read=lambda name:b.read_entry(path,h,b.get_entry_meta(meta,name))[1]
        cls.initial=read(p.PROFILE['entry_path']);cls.primary=read(p.PROFILE['secondary_entry_path'])
        cls.protocol=read(p.PROFILE['attestation_protocol_entry_path']);cls.picker=read(PICKER_PATH)
    def mutate(self,data,old,new):
        self.assertEqual(data.count(old),1);return data.replace(old,new,1)
    def test_real_bundle(self):
        require_feature_signatures(self.initial,self.primary);require_routes(self.initial,self.primary)
        self.assertEqual(run_semantics(self.initial,self.primary)['status'],'passed')
        self.assertEqual(run_work(self.initial,self.primary,self.picker)['status'],'passed')
        self.assertEqual(run_protocol(self.protocol,'node')['status'],'passed')
        self.assertEqual(run_drop(self.initial,self.primary,'node')['status'],'passed')
    def test_plan_must_be_yellow_even_when_pinned(self):
        data=self.mutate(self.initial,b'`#eab308`',b'`#ff8549`')
        with self.assertRaises(ContractError):run_semantics(data,self.primary)
        data=self.mutate(self.initial,b'e.p?`#eab308`:e.i&&n?`danger`',b'e.i&&n?`danger`:e.p?`#eab308`')
        with self.assertRaises(ContractError):run_semantics(data,self.primary)
    def test_display_scalar_cannot_replace_pending_request(self):
        data=self.mutate(self.initial,b'Wt=qZp(mt,Q,Vt,Ht,Ut)',b'Wt=qZp(pt,Q,Vt,Ht,Ut)')
        with self.assertRaises(ContractError):require_feature_signatures(data,self.primary)
    def test_pinned_dependency_must_recompute(self):
        data=self.mutate(self.initial,b't[131]!==gt||t[132]!==w||t[154]!==b',b't[131]!==gt||t[132]!==w')
        with self.assertRaises(ContractError):require_feature_signatures(data,self.primary)
    def test_live_sort_must_be_connected(self):
        old,new=p.PAIRS['priority_filter_live_resort'][0]
        with self.assertRaises(ContractError):require_feature_signatures(self.mutate(self.initial,new,old),self.primary)
    def test_raw_uuid_cannot_return(self):
        data=self.mutate(self.initial,b'a=t?.map(e=>({...e,label:qZx(e)}))||[]',b'a=t||[]')
        with self.assertRaises(ContractError):run_work(data,self.primary,self.picker)
    def test_live_merge_must_preserve_saved_label_and_current_keys(self):
        old,new=p.PAIRS['remote_project_label'][1]
        with self.assertRaises(ContractError):run_semantics(self.mutate(self.initial,new,old),self.primary)
    def test_inherited_remote_selection_survives(self):
        data=self.mutate(self.primary,b'p?.projectId??null:n',b'(p?.type===`local`?p.projectId:null):n')
        with self.assertRaises(ContractError):run_work(self.initial,data,self.picker)
    def test_remote_kind_preserved(self):
        old,new=p.SECONDARY_PAIRS['work_remote_project_picker'][2]
        with self.assertRaises(ContractError):run_work(self.initial,self.mutate(self.primary,new,old),self.picker)
    def test_lazy_route_must_exist(self):
        data=self.mutate(self.primary,b'import(`./composer-project-picker-content-cee23446c3c9.js`)',b'import(`./missing.js`)')
        with self.assertRaises(ContractError):require_routes(self.initial,data)
    def test_protocol_rejects_foreign_hosts(self):
        data=self.mutate(self.protocol,b'if(e===`app://-/x`)',b'if(r==`/x`)')
        with self.assertRaises(ContractError):run_protocol(data,'node')
    def test_drop_callback_must_execute(self):
        data=self.mutate(self.primary,b'r(t.files,`drop`,e.dataTransfer,l)',b'void 0')
        with self.assertRaises(ContractError):run_drop(self.initial,data,'node')

if __name__=='__main__':unittest.main()
