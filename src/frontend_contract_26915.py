"""Execute the exact 26.915 bundle; independent fixtures never rewrite functions."""
from pathlib import Path
import json, subprocess, hashlib
from frontend_feature_contracts import ContractError, _extract_function, _with_module_stubs, _validate_renderer_probe
import hotfix_profile_26915_3509 as p


def _scenario_source() -> str:
    local = Path(__file__).with_name("frontend_scenarios_26915.js")
    if local.is_file():
        return local.read_text(encoding="utf-8")
    from importlib import resources

    return (
        resources.files("codex_desktop_workflow")
        .joinpath("data", "frontend_scenarios_26915.js")
        .read_text(encoding="utf-8")
    )


FUNCTIONS = ('iI','Moi','CZs','b3','Vxn','fPt','i6','v7s','qZx','C9r','Hoi','Hsi','QDi','$Di','Koi','$ti','PF','Gsi','Ksi','Vsi','sai','uai','tBt','rso','xSc','NTc','bti','qZp')

ROUTES={
 'plan_pending_detection':(('entry_path',b'pt=xf(vri,n),mt=xf(s8n,n)'),('entry_path',b's8n=HE((e,t)=>$4n(e,t(ptn)))')),
 'remote_project_label':(('entry_path',b'return Hoi(e(nI),n,r)'),('entry_path',b'Sgc as Th,'),('secondary_entry_path',b'Th as xse,')),
 'work_remote_project_picker':(('entry_path',b'xti as CSt,'),('secondary_entry_path',b'CSt as zs,'),('secondary_entry_path',b'jsx)(Q7,{menuOpen:nn,onMenuOpenChange:rn,projectId:ge??null,shortcut:an,subtleHover:!0,onProjectChange:void 0}'),('secondary_entry_path',b'jsx)(O0e,{})'),('secondary_entry_path',b'import(`./composer-project-picker-content-21970821f4a5.js`)'),('secondary_entry_path',b'F5e as Z,'),('secondary_entry_path',b'e7e as F,')),
 'new_chat_file_drop':(('secondary_entry_path',b'handleDrop:Gc,handlePaste:Kc}=OGe({'),('secondary_entry_path',b'QY as Gae,'),('entry_path',b'aso as QY,')),
}

def require_routes(initial,primary):
    entries={'entry_path':initial,'secondary_entry_path':primary}
    for name,locations in ROUTES.items():
        for key,signature in locations:
            if entries[key].count(signature)!=1:raise ContractError('Disconnected actual route: '+name+' '+signature.decode())

def require_feature_signatures(initial,primary):
    for entry,pairs in [(initial,p.PAIRS),(primary,p.SECONDARY_PAIRS)]:
        for name,values in pairs.items():
            if any(entry.count(fixed)!=1 for _,fixed in values):raise ContractError('Feature wiring differs: '+name)

def run_drop(initial,primary,node):
    functions={name:_extract_function(initial.decode(),name) for name in ('rso','NTc','Goo','Koo','aso')}
    functions.update({name:_extract_function(primary.decode(),name) for name in ('OGe','q5e','L7','J5e')})
    script='\n'.join(functions.values())+r'''
const assert=(v,m)=>{if(!v)throw Error(m)},memo=()=>new Array(60).fill(Symbol.for('react.memo_cache_sentinel'));
const kGe={c:memo},Y5e={c:memo},m2={useState:v=>[v,()=>{}],useEffectEvent:v=>v,useEffect:()=>{}},R7=m2;
const ig=rso,Ume=NTc,Gae=aso,kg=()=>false,Cr=f=>f.type?.startsWith('image/'),hso='Files',Node=class{},window={};
const file={name:'example.txt',size:8,type:'text/plain'},transfer={items:[{kind:'file',getAsFile:()=>file,webkitGetAsEntry:()=>null}],files:[file],types:['Files']};
const event=()=>({dataTransfer:transfer,preventDefault(){this.defaultPrevented=true},stopPropagation(){},currentTarget:{},target:{}});
let received=null,called=0;
let handlers=OGe({activeBrowserImageDragBrowserTabId:null,addFiles:(files,via)=>{received=files;assert(via==='drop','drop source')},addDraggedImage:()=>{throw Error('wrong image route')},directBrowserConversationId:null,dragCounterRef:{current:0},dropTargetPortalTarget:null,isDragActive:false,onAttachmentAdded:null,setIsDragActive:()=>{},setShowShiftOverlay:()=>{}});
let e=event();handlers.handleDrop(e);assert(e.defaultPrevented&&received[0]===file,'actual new-chat composer drop');
let h=q5e({disabled:false,dropTarget:null,onFilesDropped:files=>{called++;assert(files[0]===file,'drop identity')}});h.onDrop(event());assert(called===1,'enabled target');
q5e({disabled:true,dropTarget:null,onFilesDropped:()=>called++}).onDrop(event());assert(called===1,'disabled target');
transfer.items[0].webkitGetAsEntry=()=>({isDirectory:true});h.onDrop(event());assert(called===1,'directory excluded');
assert(!rso({items:[],types:['text/plain']}),'text excluded');
process.stdout.write(JSON.stringify({status:'passed',actual_composer_handler:true,file_identity_preserved:true,disabled_rejected:true,directory_excluded:true}));
'''
    cp=subprocess.run([node,'-'],input=_with_module_stubs(script,functions),text=True,capture_output=True,timeout=30)
    if cp.returncode:raise ContractError('26.915 file drop: '+cp.stderr[-2000:])
    return json.loads(cp.stdout)

def run_protocol(protocol,node):
    functions='\n'.join(_extract_function(protocol.decode(),name) for name in ('Ct','wt','mt'))
    script=r'''const u=require('node:path'),n={ul:s=>s.replace(/\\/g,'/')},rt='-',it='fs',at='index.html',st='/@fs';const Tt=()=>null;'''+functions+r'''
const assert=(v,m)=>{if(!v)throw Error(m)},root='C:/fixture/resources/app.asar/webview';
assert(u.resolve(mt('app://-/x',root))===u.resolve(root+'/../../x.js'),'fixed module');
for(const url of ['https://-/x','app://evil/x','app://-/../x','app://-/%2e%2e/x','app://-/%2e%2e%5cx','app://-/..%20/x','app://-/%ZZ'])assert(mt(url,root)===null,'unsafe URL '+url);
for(const url of ['app://-/x.js','app://-/x?query','app://-/assets/a.js'])assert(u.resolve(mt(url,root)).startsWith(u.resolve(root)+u.sep),'ordinary path confinement '+url);
process.stdout.write(JSON.stringify({status:'passed',fixed_module:true,traversal_rejected:true,foreign_host_rejected:true,siblings_confined:true}));
'''
    cp=subprocess.run([node,'-'],input=script,text=True,capture_output=True,timeout=20)
    if cp.returncode:raise ContractError('26.915 resource route: '+cp.stderr[-1800:])
    return json.loads(cp.stdout)

def run_semantics(initial, primary, node='node'):
    functions={name:_extract_function(initial.decode(),name) for name in FUNCTIONS}
    scenarios=_scenario_source()
    script='\n'.join(functions.values())+'\n'+scenarios
    cp=subprocess.run([node,'-'],input=_with_module_stubs(script,functions),text=True,capture_output=True,timeout=30)
    if cp.returncode: raise ContractError('26.915 actual function test: '+cp.stderr[-3000:])
    result=json.loads(cp.stdout)
    result['script_sha256']=hashlib.sha256(script.encode()).hexdigest()
    result['executed']=list(FUNCTIONS)
    return result

def validate(source_asar, portable_asar, node='node'):
    import hotfix_builder as b
    profile=p.PROFILE
    def read(path):
        hs,_,meta=b.read_asar(path)
        return {key:b.read_entry(path,hs,b.get_entry_meta(meta,profile[key]))[1] for key in ('entry_path','secondary_entry_path','main_entry_path','attestation_protocol_entry_path')}
    src=read(source_asar); out=read(portable_asar)
    if b.sha256_path(source_asar)!=profile['asar_source_sha256']:raise ContractError('Official ASAR identity changed')
    for key,hashkey in [('entry_path','entry_source_sha256'),('secondary_entry_path','secondary_entry_source_sha256'),('main_entry_path','main_entry_source_sha256'),('attestation_protocol_entry_path','attestation_protocol_source_sha256')]:
        if b.sha256_bytes(src[key])!=profile[hashkey]:raise ContractError('Official entry identity changed: '+key)
    actual=run_semantics(out['entry_path'],out['secondary_entry_path'],node)
    require_feature_signatures(out['entry_path'],out['secondary_entry_path'])
    require_routes(out['entry_path'],out['secondary_entry_path'])
    actual['file_drop']=run_drop(out['entry_path'],out['secondary_entry_path'],node)
    actual['protocol_security']=run_protocol(out['attestation_protocol_entry_path'],node)
    from frontend_work_contract_26915 import run as run_work,PICKER_PATH,PICKER_SHA256
    hs,_,header=b.read_asar(portable_asar)
    picker=b.read_entry(portable_asar,hs,b.get_entry_meta(header,PICKER_PATH))[1]
    if b.sha256_bytes(picker)!=PICKER_SHA256:raise ContractError('Actual picker chunk changed')
    actual['composer_selector']=run_work(out['entry_path'],out['secondary_entry_path'],picker,node)
    probe=_validate_renderer_probe(out['entry_path'],portable_asar,b,profile)
    inspected,_=b.inspect_archive(source_asar)
    aliases={'plan_pending_unread_indicator':('plan_pending_detection','plan_pending_yellow_indicator'),'attention_highlight_color_semantics':('plan_pending_detection','plan_pending_yellow_indicator')}
    fnmap={
      'priority_filter_recency_sorting':['iI'],'priority_filter_live_resort':['iI'],'priority_filter_pinned_recency_sorting':['iI'],
      'priority_filter_hold_membership':['CZs','b3'],'priority_click_hold':['xSc'],'priority_identity_migration':['Moi'],
      'priority_project_context_subtitle':['Koi'],'plan_pending_detection':['qZp'],'plan_pending_yellow_indicator':['i6','v7s'],
      'plan_pending_unread_indicator':['qZp','i6','v7s'],'attention_highlight_color_semantics':['qZp','i6','v7s'],
      'project_sorting':['Hsi','iI'],'active_priority_sort':['QDi','$Di'],'automation_priority_gate':['b3','CZs'],'pinned_priority_sync':['Moi'],
      'new_chat_file_drop':['OGe','q5e','rso','NTc','aso'],'resume_history_on_demand':['Vxn'],'paginated_tail_retention':['fPt'],
      'idle_history_eviction':['tBt'],'remote_project_label':['qZx','C9r','Hoi'],
      'work_remote_project_picker':['xti','Q7','a7e','z$','O0e','f9e','I','F5e','e7e','$ka']}
    contracts={}
    for name in b.FEATURE_STATUSES:
        locations=[];patched=False
        for dep in aliases.get(name,(name,)):
            for key,pairs in [('entry_path',p.PAIRS),('secondary_entry_path',p.SECONDARY_PAIRS)]:
                for _,fixed in pairs.get(dep,()):locations.append((key,fixed));patched=True
            locations.extend(('entry_path',sig) for sig in p.OFFICIAL_FEATURE_SIGNATURES.get(dep,()))
            locations.extend(ROUTES.get(dep,()))
        counts=[out[key].count(sig) for key,sig in locations]
        component=not locations and name in b.NON_RENDERER_ATTESTATION_FEATURES and inspected['features'][name]['status']=='official_fixed'
        passed=bool(locations or component) and all(n==1 for n in counts)
        if not passed:raise ContractError('Feature signature or component gate failed: '+name+' '+str(counts))
        paths=sorted({key for key,_ in locations})
        payload=b'\0'.join(sig for _,sig in locations) or json.dumps(inspected['features'][name],sort_keys=True).encode()
        nonrenderer=name in b.NON_RENDERER_ATTESTATION_FEATURES
        contracts[name]={
          'status':'patched_verified' if patched else 'native_verified',
          'source_identity':{'status':'passed','official_asar_sha256':profile['asar_source_sha256'],'entry_paths':[profile[k] for k in paths],
              'official_entry_sha256':{profile[k]:b.sha256_bytes(src[k]) for k in paths},'portable_entry_sha256':{profile[k]:b.sha256_bytes(out[k]) for k in paths},'component_gate':inspected['features'][name] if component else None},
          'semantic_execution':{'status':'passed','method':'actual_bundle_execution' if name in fnmap else 'exact_component_gate_and_non_target_hash','executed_functions':fnmap.get(name,[])},
          'route_wiring':{'status':'passed','unique_signature_counts':counts,'component_gate':component},
          'runtime_attestation':{'status':'preverified_non_renderer' if nonrenderer else 'pending_live_renderer','attestation_version':'2.4.7','protocol':'component_contract_v1' if nonrenderer else probe['protocol'],'scope':'main_process' if name in {'windows_watch_path_normalization','process_registry_resilience'} else 'guarded_interaction' if name=='archived_heartbeat_terminal_guard' else 'renderer','artifact_id':probe['artifact_id'],'content_logged':False},
          'evidence_sha256':b.sha256_bytes(payload)}
    result={'schema_version':2,'validator_version':'2.4.7','status':'bundle_qualified_only','source_asar_sha256':profile['asar_source_sha256'],
        'portable_asar_sha256':b.sha256_path(portable_asar),'frontend_entry_path':profile['entry_path'],'frontend_entry_sha256':b.sha256_bytes(out['entry_path']),
        'secondary_entry_path':profile['secondary_entry_path'],'secondary_entry_sha256':b.sha256_bytes(out['secondary_entry_path']),
        'feature_contracts':contracts,'blocked_feature_ids':[],'actual_javascript':actual,'live_renderer_probe':probe,'content_logged':False}
    result['summary_sha256']=b.sha256_bytes(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    return result
