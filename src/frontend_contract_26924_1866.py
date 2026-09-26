"""Execute the exact 26.924 renderer graph with adversarial state fixtures."""
from pathlib import Path
import hashlib
import json
import subprocess

from frontend_feature_contracts import ContractError, _extract_function, _with_module_stubs, _validate_renderer_probe
import hotfix_profile_26924_1866 as p

INITIAL_FUNCTIONS = ('Lj','z5t','psn','hP','fsn','X$','ski','qZx','m7t','Q5t','Z4t','ytn','btn','t7t','X7t','ZM','e3t','t3t','X4t','u4t','p4t','T8r','BZi','q6i','O7t','qZp')
SHARED_FUNCTIONS = ('YRn','JRn','fJt','tj','ej','Qst')

def execute(functions, scenario, node='node', *, stubs=True):
    script = '\n'.join(functions.values()) + '\n' + scenario
    if stubs: script = _with_module_stubs(script, functions)
    result = subprocess.run([node, '-'], input=script, text=True, encoding='utf8', capture_output=True, timeout=40)
    if result.returncode:
        raise ContractError('26.924 packaged scenario: ' + result.stderr[-2000:])
    value = json.loads(result.stdout)
    value['executed'] = list(functions)
    value['script_sha256'] = hashlib.sha256(script.encode()).hexdigest()
    return value

def functions_from(raw, names):
    return {n: ('async ' if raw.count(('async function '+n+'(').encode()) == 1 else '') + _extract_function(raw.decode(), n) for n in names}

def run_semantics(initial, primary, shared, node='node'):
    functions = functions_from(initial, INITIAL_FUNCTIONS)
    functions.update(functions_from(shared, SHARED_FUNCTIONS))
    result = execute(functions, Path(__file__).parent.joinpath('codex_desktop_workflow/data', 'frontend_scenarios_26924_1866.js').read_text(encoding='utf8'), node)
    result['actual_row'] = run_row(initial, shared, node)
    return result

def run_row(initial, shared, node='node'):
    functions = functions_from(initial, ('W0i','CJi','KMi','X$','ski','cki','qZp'))
    functions.update(functions_from(shared, ('Mqt','Nqt','kR','d1','OR')))
    return execute(functions, Path(__file__).parent.joinpath('codex_desktop_workflow/data', 'frontend_row_scenarios_26924_1866.js').read_text(encoding='utf8'), node)

def require_feature_signatures(initial, primary, shared):
    for raw, groups in [(initial,p.PAIRS),(primary,p.SECONDARY_PAIRS),(shared,p.SHARED_PAIRS)]:
        for feature, pairs in groups.items():
            if any(raw.count(fixed)!=1 for _,fixed in pairs):
                raise ContractError('Feature wiring differs: '+feature)

ROUTES = {
 'archived_heartbeat_terminal_guard': [('main_entry_path',b'if(a.Xt(e)!==`thread_archived`)throw e;s();let n=i.jn(t.id);if(n?.kind!==`heartbeat`||n.status!==`ACTIVE`||n.targetThreadId!==t.targetThreadId)return;')],
 'plan_pending_detection': [('entry_path',b'let ot=Xd(Zl,at)'),('entry_path',b'Ct=ot?.pendingRequest'),('entry_path',b'statusState:$t,statusIndicatorReplacesMeta:Ae')],
 'priority_filter_live_resort': [('entry_path',b'v=new Map(h.map(({item:e,recencyAt:t})=>[gP(u,e),t]))')],
 'priority_filter_pinned_recency_sorting': [('entry_path',b'SP=Nr(G,(e,{get:t})=>')],
 'priority_project_context_subtitle': [('entry_path',b'function t7t({chatLabel:e,task:t,projectLabel:n')],
 'resume_history_on_demand': [('shared_entry_path',b'function YRn(e){return e.resumeState===`resumed`&&(')],
 'paginated_tail_retention': [('shared_entry_path',b'function JRn(e){return d1(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}')],
 'idle_history_eviction': [('shared_entry_path',b'function fJt({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a')],
 'remote_project_label': [('entry_path',b'Vjr=qe(G,({get:e})=>{let t=e(Mj),n=e(rN).groups,r=new Map(cN(e,t).map(e=>[e.task.key,e]));return Q5t(e(tN),n,r)})'),('entry_path',b'Jjr=qe(G,({get:e})=>Wjr(e(Vjr)))')],
 'work_remote_project_picker': [('secondary_entry_path',b'import(`./composer-project-picker-content-cefe9ab592b1.js`)'),('secondary_entry_path',b'workspaceProjectOptions:L'),('secondary_entry_path',b'workspaceProjectOptions:c,projectId:l,searchQuery:L')],
}

def require_routes(entries):
    for feature, locations in ROUTES.items():
        for key, signature in locations:
            if entries[key].count(signature)!=1:
                raise ContractError('Disconnected route: '+feature+' '+signature.decode())

def run_drop(initial, primary, node='node'):
    functions = functions_from(initial, ('T8r','q6i','p8r','m8r','D8r'))
    functions.update(functions_from(primary, ('XRt','W6t','K6t','G6t')))
    return execute(functions, Path(__file__).parent.joinpath('codex_desktop_workflow/data', 'frontend_drop_scenarios_26924_1866.js').read_text(encoding='utf8'), node)

def run_archive(main, node='node'):
    functions = functions_from(main, ('Tae',))
    scenario = r"""
const assert=(x,m)=>{if(!x)throw Error(m)};
let current={id:'automation',kind:'heartbeat',status:'ACTIVE',targetThreadId:'thread'},writes=[],deletes=[],notifications=0,code='thread_archived';
const mae=()=>({nextScheduledRunAt:2}),Nae=()=>null,Os=()=>({}),Mae=()=>({}),Ps=async()=>true,Is=async()=>null,ks=async()=>({}),Fs=async()=>{throw {code}},a={Xt:e=>e.code};
const i={Fn:()=>1,Wn:()=>{},jn:()=>current,Zn:e=>{writes.push(e);return e}};
const base={automation:{...current},now:1,assertCurrent:()=>{},appServerConnection:{readThread:async()=>({cwd:'/fixture'}),notifyAutomationRunTriggered:()=>{},notifyAutomationRunsUpdated:()=>notifications++},heartbeatThreadPermissions:new Map()};
(async()=>{
 await Tae({...base,deleteArchivedHeartbeat:async id=>{deletes.push(id);return 'deleted'}});
 assert(deletes.length===1&&notifications===1&&!writes.length,'archived heartbeat deleted once');
 deletes=[];notifications=0;await Tae(base);assert(writes.length===1&&writes[0].status==='PAUSED'&&notifications===1,'local terminal fallback');
 for(const changed of [{...current,status:'PAUSED'},{...current,targetThreadId:'another'},{...current,kind:'cron'},null]){
  current=changed;writes=[];deletes=[];notifications=0;await Tae({...base,deleteArchivedHeartbeat:async id=>{deletes.push(id);return 'deleted'}});assert(!writes.length&&!deletes.length&&!notifications,'concurrent canonical state preserved');
 }
 current={...base.automation};code='different_failure';let failed=false;try{await Tae(base)}catch(e){failed=e.code===code}assert(failed,'unrelated failure not swallowed');
 process.stdout.write(JSON.stringify({status:'passed',archived_terminal:true,delete_once:true,pause_fallback:true,concurrent_state_preserved:true,unrelated_error_preserved:true}));
})().catch(e=>{process.stderr.write(String(e.stack||e));process.exitCode=1});
"""
    return execute(functions, scenario, node, stubs=False)


def run_protocol(protocol, node='node'):
    functions = functions_from(protocol, ('F','I','E'))
    scenario = r"""
const a=require('node:path'),t={$i:s=>s.replace(/\\/g,'/')},h='-',g='fs',_='index.html',y='/@fs';
const assert=(x,m)=>{if(!x)throw Error(m)},root='C:/fixture/resources/app.asar/webview';
assert(a.resolve(E('app://-/x',root))===a.resolve(root+'/../../x.js'),'fixed module');
for(const url of ['https://-/x','app://evil/x','app://-/../x','app://-/%2e%2e/x','app://-/%2e%2e%5cx','app://-/..%20/x','app://-/%ZZ'])assert(E(url,root)===null,'unsafe URL '+url);
for(const url of ['app://-/x.js','app://-/x?query','app://-/assets/a.js'])assert(a.resolve(E(url,root)).startsWith(a.resolve(root)+a.sep),'ordinary path confinement');
process.stdout.write(JSON.stringify({status:'passed',fixed_module:true,traversal_rejected:true,foreign_host_rejected:true,siblings_confined:true}));
"""
    return execute(functions, scenario, node, stubs=False)

def validate(source_asar, portable_asar, node='node'):
    import hotfix_builder as b
    profile=p.PROFILE
    fields=('entry_path','secondary_entry_path','shared_entry_path','main_entry_path','attestation_protocol_entry_path')
    def read(path):
        hs,_,meta=b.read_asar(path)
        return {key:b.read_entry(path,hs,b.get_entry_meta(meta,profile[key]))[1] for key in fields}
    src,out=read(source_asar),read(portable_asar)
    if b.sha256_path(source_asar)!=profile['asar_source_sha256']:
        raise ContractError('Official ASAR identity changed')
    for key in fields:
        hashkey=key.replace('_path','_source_sha256').replace('attestation_protocol_entry_source','attestation_protocol_source')
        if b.sha256_bytes(src[key])!=profile[hashkey]:raise ContractError('Official entry identity changed: '+key)
    require_feature_signatures(out['entry_path'],out['secondary_entry_path'],out['shared_entry_path'])
    require_routes(out)
    actual=run_semantics(out['entry_path'],out['secondary_entry_path'],out['shared_entry_path'],node)
    actual['file_drop']=run_drop(out['entry_path'],out['secondary_entry_path'],node)
    actual['archived_heartbeat']=run_archive(out['main_entry_path'],node)
    actual['protocol_security']=run_protocol(out['attestation_protocol_entry_path'],node)
    from frontend_work_contract_26924_1866 import run as run_work, PICKER_PATH, PICKER_SHA256
    hs,_,header=b.read_asar(portable_asar)
    picker=b.read_entry(portable_asar,hs,b.get_entry_meta(header,PICKER_PATH))[1]
    if b.sha256_bytes(picker)!=PICKER_SHA256:raise ContractError('Picker chunk changed')
    actual['composer_selector']=run_work(out['entry_path'],out['secondary_entry_path'],picker,out['shared_entry_path'],node)
    probe=_validate_renderer_probe(out['entry_path'],portable_asar,b,profile)
    inspected,_=b.inspect_archive(source_asar)
    aliases={'plan_pending_unread_indicator':('plan_pending_detection','plan_pending_yellow_indicator'),'attention_highlight_color_semantics':('plan_pending_detection','plan_pending_yellow_indicator')}
    contracts={}
    for name in b.FEATURE_STATUSES:
        locations=[];patched=False
        for dep in aliases.get(name,(name,)):
            for key,groups in [('entry_path',p.PAIRS),('secondary_entry_path',p.SECONDARY_PAIRS)]:
                for _,fixed in groups.get(dep,()):locations.append((key,fixed));patched=True
            locations.extend(('entry_path',sig) for sig in p.OFFICIAL_FEATURE_SIGNATURES.get(dep,()))
            locations.extend(('shared_entry_path',sig) for sig in p.SHARED_OFFICIAL_FEATURE_SIGNATURES.get(dep,()))
            locations.extend(ROUTES.get(dep,()))
        counts=[out[key].count(sig) for key,sig in locations]
        component=not locations and name in b.NON_RENDERER_ATTESTATION_FEATURES and inspected['features'][name]['status']=='official_fixed'
        if not (locations or component) or any(n!=1 for n in counts):raise ContractError('Feature route gate failed: '+name+' '+str(counts))
        keys=sorted({key for key,_ in locations});nonrenderer=name in b.NON_RENDERER_ATTESTATION_FEATURES
        payload=b'\x00'.join(sig for _,sig in locations) or json.dumps(inspected['features'][name],sort_keys=True).encode()
        contracts[name]={'status':'patched_verified' if patched else 'native_verified','source_identity':{'status':'passed','official_asar_sha256':profile['asar_source_sha256'],'entry_paths':[profile[k] for k in keys],'official_entry_sha256':{profile[k]:b.sha256_bytes(src[k]) for k in keys},'portable_entry_sha256':{profile[k]:b.sha256_bytes(out[k]) for k in keys},'component_gate':inspected['features'][name] if component else None},'semantic_execution':{'status':'passed','method':'actual_bundle_execution' if not nonrenderer else 'exact_component_gate_and_non_target_hash'},'route_wiring':{'status':'passed','unique_signature_counts':counts,'component_gate':component},'runtime_attestation':{'status':'preverified_non_renderer' if nonrenderer else 'pending_live_renderer','attestation_version':'2.5.0','protocol':'component_contract_v1' if nonrenderer else probe['protocol'],'scope':'main_process' if name in {'windows_watch_path_normalization','process_registry_resilience'} else 'guarded_interaction' if nonrenderer else 'renderer','artifact_id':probe['artifact_id'],'content_logged':False},'evidence_sha256':b.sha256_bytes(payload)}
    result={'schema_version':2,'validator_version':'2.5.0','status':'bundle_qualified_only','source_asar_sha256':profile['asar_source_sha256'],'portable_asar_sha256':b.sha256_path(portable_asar),'frontend_entry_path':profile['entry_path'],'frontend_entry_sha256':b.sha256_bytes(out['entry_path']),'secondary_entry_path':profile['secondary_entry_path'],'secondary_entry_sha256':b.sha256_bytes(out['secondary_entry_path']),'shared_entry_path':profile['shared_entry_path'],'shared_entry_sha256':b.sha256_bytes(out['shared_entry_path']),'feature_contracts':contracts,'blocked_feature_ids':[],'actual_javascript':actual,'live_renderer_probe':probe,'content_logged':False}
    result['summary_sha256']=b.sha256_bytes(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    return result
