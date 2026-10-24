"""Installer smoke gate; authenticated feature acceptance belongs to the release record.

This gate never copies login files. It checks the installed bytes, fresh renderer
contracts and native synthetic history under both an empty and populated home.
"""
import hashlib,json,os,time,tomllib
from pathlib import Path
from . import awake_clock,backend,history
from .isolated_run import IsolatedRun
from .renderer_proof import parse_owned_logs
from .brokered_processes import pending_elevations
from .native_history_fixture import generate,Client
from .native_checks_8120 import verify as native_checks
from .native_row_8120 import verify as native_row

def _configure_fixture_sandbox(home):
    """Keep the disposable smoke test from requesting machine-wide setup.

    This is the upstream supported restricted-token mode, confined to the
    newly created test home. Never replace an existing Windows configuration.
    """
    home=Path(home)
    config=home/'config.toml'
    if home.is_symlink() or config.is_symlink():
        raise ValueError('fixture_configuration_link_not_allowed')
    raw=config.read_bytes() if config.exists() else b''
    if 'windows' in tomllib.loads(raw.decode('utf8')):
        raise ValueError('unexpected_fixture_windows_sandbox_configuration')
    with config.open('r+b' if config.exists() else 'xb') as stream:
        if raw and stream.read()!=raw:raise ValueError('fixture_configuration_changed')
        stream.write(b'\n[windows]\nsandbox="unelevated"\n')
    return {'scope':'disposable_home_only','windows_sandbox':'unelevated'}

def release_policy():
    path=Path(__file__).parent/'policies/qualification-26.1016.8120.0.json'
    if not path.is_file():raise ValueError('8120_public_release_acceptance_not_complete')
    value=json.loads(path.read_text(encoding='utf8'))
    if value.get('status')!='passed' or value.get('desktop_version')!='26.1016.8120.0':
        raise ValueError('8120_public_release_acceptance_not_complete')
    from .release_sources import validate
    return validate(path,value)

def verify(source,portable,runs_root,observe_seconds,launches):
    from . import workflow as w
    import hotfix_builder as b,frontend_feature_contracts
    release=release_policy()
    inspected=w.inspect(source)
    if inspected.get('status')!='passed' or inspected.get('supported_version')!='26.1016.8120.0':raise ValueError('8120_source_not_verified')
    portable=portable.resolve();runs_root=runs_root.resolve();runs_root.mkdir(parents=True,exist_ok=True)
    support=w.SUPPORTED_PACKAGES['26.1016.8120.0'];manifest=portable/'codex-desktop-workflow-manifest.json'
    public=json.loads((portable/'codex-desktop-workflow.json').read_text());mode=public['backend_mode']
    policy=Path(public['backend_manifest']) if mode=='compat' else support.backend_policy
    selected=backend.validate_manifest(policy)['patched']['sha256'] if mode=='compat' else support.backend_sha256
    if mode not in ('official','compat') or w._sha256(portable/'resources/codex.exe')!=selected:raise ValueError('backend_identity_mismatch')
    if mode=='compat' and public['backend_manifest_sha256']!=w._sha256(policy):raise ValueError('backend_manifest_changed')
    bound,binding=w._bind_verification_source(manifest,Path(inspected['app_directory'])/'resources/app.asar',runs_root,support.asar_sha256)
    bundle=b.verify_manifest(bound,w._sha256(policy),policy)
    contracts=frontend_feature_contracts.validate(Path(inspected['app_directory'])/'resources/app.asar',portable/'resources/app.asar')
    native=native_checks(portable,Path(inspected['app_directory'])/'resources/app.asar')
    native['complete_row_pipeline']=native_row(portable)
    result={'status':'running','verification_scope':'installation_integrity_and_isolated_runtime','release_qualification':release,'bundle':bundle,'contracts':contracts,'native_nonrenderer':native,'source_binding':binding,'runtime':[]}
    for index in range(2):
        home=runs_root/('install-home-'+os.urandom(8).hex());home.mkdir()
        profile='synthetic_tasks' if index else 'empty'
        fixture=generate(home,portable/'resources/codex.exe',400) if index else None
        sandbox=_configure_fixture_sandbox(home)
        history.inspect(home)
        if pending_elevations(portable)['status']!='none_for_owned_candidate':raise ValueError('owned_candidate_elevation_pending')
        run=IsolatedRun.start(portable/'ChatGPT.exe',runs_root,environment=w._portable_environment(portable,home),debug_port=w._available_loopback_port(),isolate_shell_folders=True)
        item={'profile':profile,'run_directory':str(run.run_directory),'codex_home':str(home),'status':'running','synthetic_threads':400 if index else 0,'authentication_copied':False,'fixture_sandbox':sandbox}
        error=None
        try:
            deadline=awake_clock.seconds()+240;proof=None
            while awake_clock.seconds()<deadline:
                state=run.status('codex.exe')
                if state['status'] not in ('running','running_without_backend'):raise ValueError('candidate_exited_before_proof')
                proof=parse_owned_logs(manifest,run.run_directory,state['main'])
                if proof['status']=='passed':break
                time.sleep(1)
            if not proof or proof['status']!='passed':raise ValueError('fresh_renderer_proof_missing')
            item['attestation']=proof;start=awake_clock.seconds()
            while awake_clock.seconds()-start<observe_seconds:
                if run.status('codex.exe')['status']!='running':raise ValueError('candidate_exited_during_observation')
                time.sleep(2)
            item['observed_seconds']=awake_clock.seconds()-start
            state=run.status('codex.exe');item['pre_close']=state;item['backend_match']=w._current_app_server_match(state,portable,selected)
            if not item['backend_match']:raise ValueError('current_app_server_mismatch')
        except BaseException as exc:error=exc;item['error']=str(exc)
        finally:
            item['close']=w._normal_codex_stop(run,30);item['brokered_prompts']=pending_elevations(portable)
            item['status']='passed' if error is None and item['close'].get('close_status')=='closed' and item['brokered_prompts']['status']=='none_for_owned_candidate' else 'failed'
            result['runtime'].append(item)
            (run.run_directory/'installation-verification.json').write_text(json.dumps(item,indent=2))
        if item['status']!='passed':raise ValueError('8120_installation_runtime_failed:'+str(run.run_directory)) from error
        if fixture:
            client=Client(portable/'resources/codex.exe',home,home/'synthetic-workspaces')
            try:
                for tid in (fixture['ids'][0],fixture['ids'][-1]):
                    response=client.call('thread/read',{'threadId':tid,'includeTurns':True})
                    if 'error' in response or len(response['result']['thread']['turns'])!=1:raise ValueError('native_cold_history_read_failed')
            finally:client.close()
            for name,entry in fixture['files'].items():
                if w._sha256(home/name)!=entry['sha256']:raise ValueError('synthetic_history_bytes_changed')
            item['native_cold_history']={'status':'passed','threads':400,'first_last_read':True,'all_history_bytes_unchanged':True}
    result['status']='passed';return result
