"""Keep source preparation distinct from exact-candidate runtime qualification."""
from pathlib import Path
import hashlib,json

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def bindings(portable):
    portable=Path(portable)
    source=Path(__file__).resolve().parent.parent
    code={p.relative_to(source).as_posix():digest(p) for p in source.glob('*.py') if p.name.startswith(('frontend_','hotfix_','composer_selector_contract'))}
    code.update({p.relative_to(source).as_posix():digest(p) for p in (source/'codex_desktop_workflow').rglob('*') if p.is_file() and p.suffix in ('.py','.js','.cjs','.mjs','.bin','.ps1','.json') and not p.name.startswith('qualification-')})
    import electron_update_safety,desktop_adaptation_lab
    for module in (electron_update_safety,desktop_adaptation_lab):
        root=Path(module.__file__).resolve().parent
        code.update({'dependency/'+module.__name__+'/'+p.relative_to(root).as_posix():digest(p) for p in root.rglob('*.py')})
    files=('ChatGPT.exe','resources/app.asar','resources/codex.exe','resources/x.js','resources/u.cjs','codex-desktop-workflow-manifest.json','codex-desktop-workflow.json')
    return {'code':code,'candidate':{name:digest(portable/name) for name in files}}

def require_complete(value,manifest):
    if value.get('status')!='passed' or value.get('closed_log_readback')!='passed' or value.get('owned_cleanup',{}).get('owned_job_empty') is not True:
        raise ValueError('public_owned_runtime_not_complete')
    if manifest.get('package_version') in ('26.1013.4894.0','26.1016.6573.0','26.1016.8120.0'):
        if manifest['package_version']=='26.1016.8120.0':
            from .verification_8120 import release_policy
        elif manifest['package_version']=='26.1016.6573.0':
            from .verification_6573 import release_policy
        else:
            from .verification_4894 import release_policy
        if value.get('release_qualification')!=release_policy():raise ValueError('release_qualification_changed')
        required=set(manifest['frontend_runtime_attestation']['live_renderer_probe']['feature_ids'])
        runs=value.get('runtime',[])
        if len(runs)!=2 or {r.get('profile') for r in runs}!={'empty','synthetic_tasks'}:raise ValueError('installation_two_profile_matrix_missing')
        if len({r['attestation']['owner_run_id'] for r in runs})!=2:raise ValueError('public_run_identity_reused')
        for run in runs:
            proof=run.get('attestation',{})
            if run.get('observed_seconds',0)<60 or run.get('backend_match') is not True or run.get('close',{}).get('close_status')!='closed':raise ValueError('public_observation_or_backend_incomplete')
            if run.get('brokered_prompts',{}).get('status')!='none_for_owned_candidate':raise ValueError('public_external_broker_not_closed')
            if proof.get('status')!='passed' or set(proof.get('production_parser',{}).get('features',{}))!=required:raise ValueError('public_renderer_inventory_incomplete')
            if proof.get('process_id')!=run['pre_close']['main']['pid']:raise ValueError('public_main_identity_mismatch')
            if run['profile']=='synthetic_tasks' and run.get('native_cold_history',{}).get('status')!='passed':raise ValueError('native_cold_history_missing')
        if value.get('native_nonrenderer',{}).get('status')!='passed':raise ValueError('public_packaged_native_checks_missing')
        if manifest['package_version'] in ('26.1016.6573.0','26.1016.8120.0') and value.get('native_nonrenderer',{}).get('complete_row_pipeline',{}).get('status')!='passed':raise ValueError('public_complete_row_pipeline_missing')
        return
    required=set(manifest['frontend_runtime_attestation']['live_renderer_probe']['feature_ids'])
    runs=value.get('runtime',[])
    if len(runs)!=3 or {r.get('profile') for r in runs}!={'empty','synthetic_tasks','faithful_projects'}:raise ValueError('public_three_profile_matrix_missing')
    if len({r['attestation'].get('owner_run_id') for r in runs})!=3:raise ValueError('public_run_identity_reused')
    for run in runs:
        if run.get('brokered_prompts',{}).get('status')!='none_for_owned_candidate':raise ValueError('public_external_broker_not_closed')
        proof=run.get('attestation',{})
        if run.get('observed_seconds',0)<60 or run.get('backend_match') is not True or run.get('close',{}).get('close_status')!='closed':raise ValueError('public_observation_or_backend_incomplete')
        if proof.get('status')!='passed' or proof.get('feature_count')!=len(required) or set(proof.get('production_parser',{}).get('features',{}))!=required:raise ValueError('public_renderer_inventory_incomplete')
        sidebar=run.get('native_sidebar') or {}
        if sidebar.get('status')!='passed' or any(sidebar.get(name,{}).get('status')!='passed' for name in ('native_new_chat_lifecycle','mounted_drop','native_watch')):raise ValueError('public_native_focus_incomplete')
        if sidebar.get('native_six_lifecycle',{}).get('status')!='passed' or sidebar.get('native_six_lifecycle',{}).get('synthetic_sent_chats')!=6:raise ValueError('public_local_work_ssh_lifecycle_missing')
        if run['profile']!='empty' and (sidebar.get('native_cold_history',{}).get('status')!='passed' or len(sidebar.get('native_cold_history',{}).get('records',[]))!=2):raise ValueError('public_native_cold_restore_missing')
        main=run['pre_close']['main']
        if proof.get('process_id')!=main['pid']:raise ValueError('public_main_identity_mismatch')
    if value.get('native_nonrenderer',{}).get('archived_heartbeat_terminal_guard',{}).get('status')!='passed':raise ValueError('public_packaged_heartbeat_missing')
    if value.get('native_nonrenderer',{}).get('protocol_resource_route',{}).get('status')!='passed':raise ValueError('public_packaged_protocol_missing')

def seal(portable,value):
    manifest=json.loads((Path(portable)/'codex-desktop-workflow-manifest.json').read_text())
    require_complete(value,manifest)
    value['qualification_bindings']=bindings(portable)

def require(portable):
    portable=Path(portable)
    file=portable/'codex-desktop-workflow-verification.json'
    if not file.is_file():raise ValueError('public_runtime_qualification_required_before_launch')
    value=json.loads(file.read_text(encoding='utf8'))
    manifest=json.loads((portable/'codex-desktop-workflow-manifest.json').read_text())
    require_complete(value,manifest)
    if value.get('qualification_bindings')!=bindings(portable):raise ValueError('public_qualified_inputs_changed')
