"""Execute the exact 26.917 bundle; independent fixtures never rewrite functions."""
from pathlib import Path
import json, subprocess, hashlib
from frontend_feature_contracts import ContractError, _extract_function, _with_module_stubs, _validate_renderer_probe
import hotfix_profile_26917_9434 as p


def _scenario_source() -> str:
    local = Path(__file__).with_name('frontend_scenarios_26917_9434.js')
    if local.is_file():
        return local.read_text(encoding='utf-8')
    from importlib import resources
    return resources.files('codex_desktop_workflow').joinpath(
        'data', 'frontend_scenarios_26917_9434.js'
    ).read_text(encoding='utf-8')
FUNCTIONS = ('sF', 'RJr', 'kls', 'Y2', 'S1t', 'Wlt', 'L4', 'zbs', 'qZx', 'gYr', 'ZJr', 'cWr', 'EQr', 'DQr', 'tYr', 'WYr', 'ZF', 'dWr', 'fWr', 'sWr', 'mqr', 'vqr', 'zgt', 'LFa', 'FUs', 'tGs', 'AYr', 'qZp')
ROUTES = {'plan_pending_detection': (('entry_path', b'let st=He(gE,ot),ct=st!=null'), ('entry_path', b'xt=st?.pendingRequest'), ('entry_path', b'Zt=qZp(xt,Q,Jt,Yt,Xt)')), 'remote_project_label': (('entry_path', b'return ZJr(e(eI),n,r)'), ('entry_path', b'jHs as $p,'), ('secondary_entry_path', b'$p as gee,')), 'work_remote_project_picker': (('entry_path', b'jYr as iSt,'), ('secondary_entry_path', b'iSt as lye,'), ('secondary_entry_path', b'jsx)(Z7,{menuOpen:an,onMenuOpenChange:on,projectId:_e??null,shortcut:sn,subtleHover:!0,onProjectChange:void 0}'), ('secondary_entry_path', b'jsx)(rut,{})'), ('secondary_entry_path', b'import(`./composer-project-picker-content-38b3bdacb67c.js`)'), ('secondary_entry_path', b'ogt as $,'), ('secondary_entry_path', b'Tgt as L,')), 'new_chat_file_drop': (('secondary_entry_path', b'handleDrop:zc,handlePaste:Bc}=Eet({'), ('secondary_entry_path', b'NZ as Use,'), ('entry_path', b'zFa as NZ,'))}

def require_routes(initial, primary):
    entries = {'entry_path': initial, 'secondary_entry_path': primary}
    for name, locations in ROUTES.items():
        for key, signature in locations:
            if entries[key].count(signature) != 1:
                raise ContractError('Disconnected actual route: ' + name + ' ' + signature.decode())

def require_feature_signatures(initial, primary):
    for entry, pairs in [(initial, p.PAIRS), (primary, p.SECONDARY_PAIRS)]:
        for name, values in pairs.items():
            if any((entry.count(fixed) != 1 for _, fixed in values)):
                raise ContractError('Feature wiring differs: ' + name)

def run_drop(initial, primary, node):
    functions = {name: _extract_function(initial.decode(), name) for name in ('LFa', 'tGs', 'TFa', 'EFa', 'zFa')}
    functions.update({name: _extract_function(primary.decode(), name) for name in ('Eet', 'vgt', 'I7', 'ygt')})
    script = '\n'.join(functions.values()) + "\nconst assert=(v,m)=>{if(!v)throw Error(m)},memo=()=>new Array(60).fill(Symbol.for('react.memo_cache_sentinel'));\nconst Det={c:memo},bgt={c:memo},p2={useState:v=>[v,()=>{}],useEffectEvent:v=>v,useEffect:()=>{}},L7=p2;\nconst Ix=LFa,Sne=tGs,Use=zFa,of=()=>false,Ae=f=>f.type?.startsWith('image/'),hso='Files',Node=class{},window={};\nconst file={name:'example.txt',size:8,type:'text/plain'},transfer={items:[{kind:'file',getAsFile:()=>file,webkitGetAsEntry:()=>null}],files:[file],types:['Files']};\nconst event=()=>({dataTransfer:transfer,preventDefault(){this.defaultPrevented=true},stopPropagation(){},currentTarget:{},target:{}});\nlet received=null,called=0;\nlet handlers=Eet({activeBrowserImageDragBrowserTabId:null,addFiles:(files,via)=>{received=files;assert(via==='drop','drop source')},addDraggedImage:()=>{throw Error('wrong image route')},directBrowserConversationId:null,dragCounterRef:{current:0},dropTargetPortalTarget:null,isDragActive:false,onAttachmentAdded:null,setIsDragActive:()=>{},setShowShiftOverlay:()=>{}});\nlet e=event();handlers.handleDrop(e);assert(e.defaultPrevented&&received[0]===file,'actual new-chat composer drop');\nlet h=vgt({disabled:false,dropTarget:null,onFilesDropped:files=>{called++;assert(files[0]===file,'drop identity')}});h.onDrop(event());assert(called===1,'enabled target');\nvgt({disabled:true,dropTarget:null,onFilesDropped:()=>called++}).onDrop(event());assert(called===1,'disabled target');\ntransfer.items[0].webkitGetAsEntry=()=>({isDirectory:true});h.onDrop(event());assert(called===1,'directory excluded');\nassert(!LFa({items:[],types:['text/plain']}),'text excluded');\nprocess.stdout.write(JSON.stringify({status:'passed',actual_composer_handler:true,file_identity_preserved:true,disabled_rejected:true,directory_excluded:true}));\n"
    cp = subprocess.run([node, '-'], input=_with_module_stubs(script, functions), text=True, capture_output=True, timeout=30)
    if cp.returncode:
        raise ContractError('26.917 file drop: ' + cp.stderr[-2000:])
    return json.loads(cp.stdout)

def run_protocol(protocol, node):
    functions = '\n'.join((_extract_function(protocol.decode(), name) for name in ('St', 'Ct', 'pt')))
    script = "const u=require('node:path'),n={Tl:s=>s.replace(/\\\\/g,'/')},nt='-',rt='fs',it='index.html',ot='/@fs';const Tt=()=>null;" + functions + "\nconst assert=(v,m)=>{if(!v)throw Error(m)},root='C:/fixture/resources/app.asar/webview';\nassert(u.resolve(pt('app://-/x',root))===u.resolve(root+'/../../x.js'),'fixed module');\nfor(const url of ['https://-/x','app://evil/x','app://-/../x','app://-/%2e%2e/x','app://-/%2e%2e%5cx','app://-/..%20/x','app://-/%ZZ'])assert(pt(url,root)===null,'unsafe URL '+url);\nfor(const url of ['app://-/x.js','app://-/x?query','app://-/assets/a.js'])assert(u.resolve(pt(url,root)).startsWith(u.resolve(root)+u.sep),'ordinary path confinement '+url);\nprocess.stdout.write(JSON.stringify({status:'passed',fixed_module:true,traversal_rejected:true,foreign_host_rejected:true,siblings_confined:true}));\n"
    cp = subprocess.run([node, '-'], input=script, text=True, capture_output=True, timeout=20)
    if cp.returncode:
        raise ContractError('26.917 resource route: ' + cp.stderr[-1800:])
    return json.loads(cp.stdout)

def run_semantics(initial, primary, node='node'):
    functions = {name: _extract_function(initial.decode(), name) for name in FUNCTIONS}
    scenarios = _scenario_source()
    script = '\n'.join(functions.values()) + '\n' + scenarios
    cp = subprocess.run([node, '-'], input=_with_module_stubs(script, functions), text=True, capture_output=True, timeout=30)
    if cp.returncode:
        raise ContractError('26.917 actual function test: ' + cp.stderr[-3000:])
    result = json.loads(cp.stdout)
    from frontend_row_contract_26917_9434 import run as run_row
    result['actual_row'] = run_row(initial, node)
    result['script_sha256'] = hashlib.sha256(script.encode()).hexdigest()
    result['executed'] = list(FUNCTIONS)
    return result

def validate(source_asar, portable_asar, node='node'):
    import hotfix_builder as b
    profile = p.PROFILE

    def read(path):
        hs, _, meta = b.read_asar(path)
        return {key: b.read_entry(path, hs, b.get_entry_meta(meta, profile[key]))[1] for key in ('entry_path', 'secondary_entry_path', 'main_entry_path', 'attestation_protocol_entry_path')}
    src = read(source_asar)
    out = read(portable_asar)
    if b.sha256_path(source_asar) != profile['asar_source_sha256']:
        raise ContractError('Official ASAR identity changed')
    for key, hashkey in [('entry_path', 'entry_source_sha256'), ('secondary_entry_path', 'secondary_entry_source_sha256'), ('main_entry_path', 'main_entry_source_sha256'), ('attestation_protocol_entry_path', 'attestation_protocol_source_sha256')]:
        if b.sha256_bytes(src[key]) != profile[hashkey]:
            raise ContractError('Official entry identity changed: ' + key)
    actual = run_semantics(out['entry_path'], out['secondary_entry_path'], node)
    require_feature_signatures(out['entry_path'], out['secondary_entry_path'])
    require_routes(out['entry_path'], out['secondary_entry_path'])
    actual['file_drop'] = run_drop(out['entry_path'], out['secondary_entry_path'], node)
    actual['protocol_security'] = run_protocol(out['attestation_protocol_entry_path'], node)
    from frontend_work_contract_26917_9434 import run as run_work, PICKER_PATH, PICKER_SHA256
    hs, _, header = b.read_asar(portable_asar)
    picker = b.read_entry(portable_asar, hs, b.get_entry_meta(header, PICKER_PATH))[1]
    if b.sha256_bytes(picker) != PICKER_SHA256:
        raise ContractError('Actual picker chunk changed')
    actual['composer_selector'] = run_work(out['entry_path'], out['secondary_entry_path'], picker, node)
    probe = _validate_renderer_probe(out['entry_path'], portable_asar, b, profile)
    inspected, _ = b.inspect_archive(source_asar)
    aliases = {'plan_pending_unread_indicator': ('plan_pending_detection', 'plan_pending_yellow_indicator'), 'attention_highlight_color_semantics': ('plan_pending_detection', 'plan_pending_yellow_indicator')}
    fnmap = {'priority_filter_recency_sorting': ['sF'], 'priority_filter_live_resort': ['sF'], 'priority_filter_pinned_recency_sorting': ['sF'], 'priority_filter_hold_membership': ['kls', 'Y2'], 'priority_click_hold': ['FUs'], 'priority_identity_migration': ['RJr'], 'priority_project_context_subtitle': ['tYr'], 'plan_pending_detection': ['Hmt', 'CVs', 'nRs', 'OCs', 'qZp'], 'plan_pending_yellow_indicator': ['L4', 'zbs'], 'plan_pending_unread_indicator': ['qZp', 'L4', 'zbs'], 'attention_highlight_color_semantics': ['qZp', 'L4', 'zbs'], 'project_sorting': ['cWr', 'sF'], 'active_priority_sort': ['EQr', 'DQr'], 'automation_priority_gate': ['Y2', 'kls'], 'pinned_priority_sync': ['RJr'], 'new_chat_file_drop': ['Eet', 'vgt', 'I7', 'ygt', 'LFa', 'tGs', 'TFa', 'EFa', 'zFa'], 'resume_history_on_demand': ['S1t'], 'paginated_tail_retention': ['Wlt'], 'idle_history_eviction': ['zgt'], 'remote_project_label': ['qZx', 'gYr', 'ZJr'], 'work_remote_project_picker': ['Z7', 'Agt', 'j$', 'rut', 'W_t', 'c_t', 'ogt', 'Tgt', 'jYr', 'qZx', 'kK', 'I', 'L', 'R', 'z']}
    contracts = {}
    for name in b.FEATURE_STATUSES:
        locations = []
        patched = False
        for dep in aliases.get(name, (name,)):
            for key, pairs in [('entry_path', p.PAIRS), ('secondary_entry_path', p.SECONDARY_PAIRS)]:
                for _, fixed in pairs.get(dep, ()):
                    locations.append((key, fixed))
                    patched = True
            locations.extend((('entry_path', sig) for sig in p.OFFICIAL_FEATURE_SIGNATURES.get(dep, ())))
            locations.extend(ROUTES.get(dep, ()))
        counts = [out[key].count(sig) for key, sig in locations]
        component = not locations and name in b.NON_RENDERER_ATTESTATION_FEATURES and (inspected['features'][name]['status'] == 'official_fixed')
        passed = bool(locations or component) and all((n == 1 for n in counts))
        if not passed:
            raise ContractError('Feature signature sr component gate failed: ' + name + ' ' + str(counts))
        paths = sorted({key for key, _ in locations})
        payload = b'\x00'.join((sig for _, sig in locations)) or json.dumps(inspected['features'][name], sort_keys=True).encode()
        nonrenderer = name in b.NON_RENDERER_ATTESTATION_FEATURES
        contracts[name] = {'status': 'patched_verified' if patched else 'native_verified', 'source_identity': {'status': 'passed', 'official_asar_sha256': profile['asar_source_sha256'], 'entry_paths': [profile[k] for k in paths], 'official_entry_sha256': {profile[k]: b.sha256_bytes(src[k]) for k in paths}, 'portable_entry_sha256': {profile[k]: b.sha256_bytes(out[k]) for k in paths}, 'component_gate': inspected['features'][name] if component else None}, 'semantic_execution': {'status': 'passed', 'method': 'actual_bundle_execution' if name in fnmap else 'exact_component_gate_and_non_target_hash', 'executed_functions': fnmap.get(name, [])}, 'route_wiring': {'status': 'passed', 'unique_signature_counts': counts, 'component_gate': component}, 'runtime_attestation': {'status': 'preverified_non_renderer' if nonrenderer else 'pending_live_renderer', 'attestation_version': '2.4.10', 'protocol': 'component_contract_v1' if nonrenderer else probe['protocol'], 'scope': 'main_process' if name in {'windows_watch_path_normalization', 'process_registry_resilience'} else 'guarded_interaction' if name == 'archived_heartbeat_terminal_guard' else 'renderer', 'artifact_id': probe['artifact_id'], 'content_logged': False}, 'evidence_sha256': b.sha256_bytes(payload)}
    result = {'schema_version': 2, 'validator_version': '2.4.10', 'status': 'bundle_qualified_only', 'source_asar_sha256': profile['asar_source_sha256'], 'portable_asar_sha256': b.sha256_path(portable_asar), 'frontend_entry_path': profile['entry_path'], 'frontend_entry_sha256': b.sha256_bytes(out['entry_path']), 'secondary_entry_path': profile['secondary_entry_path'], 'secondary_entry_sha256': b.sha256_bytes(out['secondary_entry_path']), 'feature_contracts': contracts, 'blocked_feature_ids': [], 'actual_javascript': actual, 'live_renderer_probe': probe, 'content_logged': False}
    result['summary_sha256'] = b.sha256_bytes(json.dumps(result, sort_keys=True, separators=(',', ':')).encode())
    return result
