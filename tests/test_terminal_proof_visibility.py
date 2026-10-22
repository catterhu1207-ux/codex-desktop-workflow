"""Exercise the packaged proof transport across real lifecycle event ordering."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest


class TerminalProofVisibility(unittest.TestCase):
    def test_hidden_restore_native_race_failure_and_disposal(self):
        node=shutil.which('node')
        self.assertIsNotNone(node,'Node is required for the new renderer check')
        source=(Path(__file__).parents[1]/'src/codex_desktop_workflow/data/frontend_runtime_261016_8120.mjs').read_text(encoding='utf8')
        start=source.index('function publishTerminal(')
        end=source.index('\nexport async function r(',start)
        harness=r'''
const assert=require('node:assert/strict'),vm=require('node:vm');
function fixture(initial){
 const listeners={document:new Map(),window:new Map()},timers=new Map(),records=[];let id=0,nativeVisible=false;
 const target=(type)=>({addEventListener:(n,f)=>listeners[type].set(n,f),removeEventListener:(n,f)=>{if(listeners[type].get(n)===f)listeners[type].delete(n)}});
 const document={...target('document'),visibilityState:initial,querySelector:()=>({children:[{}]})},window=target('window');
 const context=vm.createContext({document,window,setTimeout:f=>{timers.set(++id,f);return id},clearTimeout:i=>timers.delete(i)});
 vm.runInContext(SOURCE+'\nthis.publish=publishTerminal',context);
 return {document,records,timers,listeners,publish:(status,extra)=>context.publish((s,v)=>records.push({status:s,extra:v,visible:nativeVisible}),status,extra),
  visible:v=>{nativeVisible=v},event:(type,n)=>listeners[type].get(n)?.(),flush:()=>{const all=[...timers.values()];timers.clear();all.forEach(f=>f())}};
}
const a=fixture('hidden'),payload={features:{sentinel:{passed:true}}};a.publish('passed',payload);
assert.equal(a.records.length,0);payload.features.sentinel.passed=false;
a.document.visibilityState='visible';a.visible(true);a.event('document','visibilitychange');a.flush();
assert.ok(a.records.filter(r=>r.status==='passed').length>=1);
assert.ok(a.records.filter(r=>r.status==='passed').every(r=>r.visible&&r.extra.features.sentinel.passed));
const b=fixture('visible');b.publish('passed',{proof:'actual-result'});assert.ok(b.records.every(r=>!r.visible));
b.visible(true);b.event('window','focus');b.flush();assert.ok(b.records.some(r=>r.status==='passed'&&r.visible));
for(let i=0;i<b.records.length;i+=2){assert.equal(b.records[i].status,'module_loaded');assert.equal(b.records[i+1].status,'passed')}
const f=fixture('hidden');f.publish('failed',{failure_code:'real-feature-failure'});f.document.visibilityState='visible';f.visible(true);f.event('document','visibilitychange');f.flush();
assert.ok(f.records.some(r=>r.status==='failed'));assert.ok(!f.records.some(r=>r.status==='passed'));
a.event('window','pagehide');const count=a.records.length;a.flush();a.event('window','focus');a.event('document','visibilitychange');
assert.equal(a.records.length,count);assert.equal(a.timers.size,0);assert.equal(a.listeners.document.size,0);assert.equal(a.listeners.window.size,0);
assert.throws(()=>fixture('visible').publish('module_loaded',{}),/invalid terminal proof/);
process.stdout.write(JSON.stringify({hidden_restore:true,native_visibility_race:true,failure_preserved:true,immutable_result:true,pagehide_disposal:true}));
'''.replace('SOURCE',json.dumps(source[start:end]))
        result=subprocess.run([node,'-e',harness],capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(all(json.loads(result.stdout).values()))

