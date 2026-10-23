"""Reject altered copies of actual, closed, isolated renderer evidence."""
from pathlib import Path
import ast, copy, inspect, json, os, subprocess, sys
from codex_desktop_workflow import renderer_proof


def main():
    portable=Path(sys.argv[1]).resolve();report=json.loads(Path(sys.argv[2]).read_bytes());root=Path(sys.argv[3]).resolve()
    if root.exists():
        assert root.is_dir() and not root.is_symlink() and not any(root.iterdir()), 'Read back prior proof results before retrying'
    else:root.mkdir(parents=True,exist_ok=False)
    run=report['runtime'][0];directory=Path(run['run_directory']);record=json.loads((directory/'run.json').read_bytes());pid=record['main']['pid']
    manifest=portable/'codex-desktop-workflow-manifest.json'
    manifest_data=json.loads(manifest.read_text(encoding='utf8'))
    expected_artifact=manifest_data['frontend_runtime_attestation']['live_renderer_probe']['artifact_id']
    assert report['owned_cleanup']['owned_job_empty'] is True
    assert renderer_proof.parse_owned_logs(manifest,directory,record['main'],readonly=True)['status']=='passed'
    tree=ast.parse(inspect.getsource(renderer_proof.parse_owned_logs))
    script=next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='script' for t in n.targets))
    pairs={}
    for line in (directory/'stdout.log').read_text(encoding='utf8').splitlines():
        if '[CF9]' not in line:continue
        prefix,tail=line.split('[CF9]',1)
        try:value,end=json.JSONDecoder().raw_decode(tail)
        except ValueError:continue
        if value.get('artifact_id')!=expected_artifact or 'rendererWindowAppearance=primary' not in tail[end:] or 'rendererWindowVisible=true' not in tail[end:]:continue
        pairs.setdefault(value['run_id'],[]).append((prefix,value,tail[end:]))
    # Visibility recovery can legitimately republish the same completed run.
    # Keep one actual module/terminal pair without fabricating either record.
    values=None
    for rows in pairs.values():
        module=next((r for r in rows if r[1].get('status')=='module_loaded'),None)
        terminal=next((r for r in rows if 'features' in r[1]),None)
        if module and terminal:
            values=[module,terminal];break
    if values is None:raise RuntimeError('closed_native_proof_pair_missing')
    def alter(key,value):
        rows=copy.deepcopy(values)
        for row in rows:row[1][key]=value
        return rows
    cases={'valid':values,'wrong_artifact':alter('artifact_id','2.7.9-84fe697418b2'),'wrong_schema':alter('schema_version',5),'wrong_validator':alter('validator_version','0.0.0'),'wrong_transport':alter('transport','console'),'wrong_pid':values,'stale_log':values,'missing_module':[r for r in values if 'features' in r[1]]}
    changed=copy.deepcopy(values)
    changed[-1][1]['run_id']='00000000-0000-4000-8000-000000000000';cases['mixed_run']=changed
    changed=copy.deepcopy(values)
    payload=next(r[1] for r in changed if 'features' in r[1]);payload['features'].pop(next(iter(payload['features'])));cases['missing_feature']=changed
    fields=('native_function_bindings','actual_renderer','main_route_mounted','palette') if manifest_data['package_version'] in ('26.1013.4894.0','26.1016.6573.0','26.1016.8120.0','26.1016.8622.0') else ('native_async_questions','persistent_update')
    for field in fields:
        changed=copy.deepcopy(values);next(r[1] for r in changed if 'features' in r[1])[field]=None;cases['missing_'+field]=changed
    parser={'26.1016.8622.0':'renderer_attestation_261016_8622.ps1','26.1016.8120.0':'renderer_attestation_261016_8120.ps1','26.1016.6573.0':'renderer_attestation_261016_6573.ps1','26.1013.4894.0':'renderer_attestation_261013_4894.ps1','26.1007.9446.0':'renderer_attestation_261007_9446.ps1'}.get(manifest_data['package_version'],'renderer_attestation_26928_4866.ps1')
    base_env=os.environ.copy();base_env.update(PROOF_PARSER=str(Path(renderer_proof.__file__).parent/'data'/parser),PROOF_MANIFEST=str(manifest),PROOF_PID=str(pid),PROOF_START=record['started_at'])
    results={}
    host=Path(os.environ.get('WINDIR',r'C:\Windows'))/'System32/WindowsPowerShell/v1.0/powershell.exe'
    for name,rows in cases.items():
        folder=root/name;folder.mkdir();file=folder/f'codex-desktop-isolated-{pid+1 if name=="wrong_pid" else pid}-t0-stdout.log'
        file.write_text('\n'.join(prefix+'[CF9]'+json.dumps(value,separators=(',',':'))+suffix for prefix,value,suffix in rows)+'\n',encoding='utf8')
        if name=='stale_log':
            env=dict(os.environ,STALE_LOG=str(file));subprocess.run([str(host),'-NoProfile','-NonInteractive','-Command',"(Get-Item -LiteralPath $env:STALE_LOG).CreationTimeUtc=[datetime]'2000-01-01'; (Get-Item -LiteralPath $env:STALE_LOG).LastWriteTimeUtc=[datetime]'2000-01-01'"],env=env,check=True,creationflags=0x08000000)
        env=dict(base_env,PROOF_LOGS=str(folder));cp=subprocess.run([str(host),'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-Command',script],env=env,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=30,creationflags=0x08000000)
        if cp.returncode:raise RuntimeError('production_parser_execution_failed:'+name+':'+cp.stderr[-1500:])
        result=json.loads(cp.stdout or 'null')
        accepted=bool(result and result.get('status')=='passed')
        if accepted!=(name=='valid'):raise RuntimeError('production_parser_rejection_failed:'+name)
        results[name]={'expected_accept':name=='valid','observed_status':result.get('status') if result else 'no_matching_proof','parser_exit_code':cp.returncode,'matched':True}
    output={'status':'passed','actual_closed_log_source':str(directory),'cases':results,'real_account_data_used':False}
    (root/'result.json').write_text(json.dumps(output,indent=2),encoding='utf8');print(json.dumps({'status':'passed','cases':len(results)}))


if __name__=='__main__':main()
