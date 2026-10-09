"""Cold native UI restoration of six previously sent synthetic chats."""
from pathlib import Path
import hashlib,json,os,shutil,sqlite3,subprocess,time,uuid
from codex_desktop_workflow import workflow
from codex_desktop_workflow.awake_process import run as run_awake
from codex_desktop_workflow.awake_clock import seconds
from codex_desktop_workflow.isolated_run import IsolatedRun


def qualify(app, runs_root, previous):
    app,runs_root=app.resolve(),runs_root.resolve()
    source=Path(previous['home']).resolve()
    if previous.get('status')!='passed' or not source.is_relative_to(runs_root):
        raise ValueError('qualified_synthetic_source_required')
    sent=previous['ui']['sent']
    if len(sent)!=6:raise ValueError('six_synthetic_sent_chats_required')
    home=runs_root/('cold-home-'+uuid.uuid4().hex);home.mkdir()
    shutil.copy2(source/'config.toml',home/'config.toml')
    with sqlite3.connect((source/'state_5.sqlite').as_uri()+'?mode=ro',uri=True) as read,sqlite3.connect(home/'state_5.sqlite') as write:
        read.backup(write)
        ids=[row['id'] for row in sent]
        write.execute('DELETE FROM threads WHERE id NOT IN ('+','.join('?' for _ in ids)+')',ids)
        records=write.execute('SELECT id,rollout_path,first_user_message FROM threads').fetchall()
        if len(records)!=6:raise ValueError('synthetic_source_rows_missing')
        for identity,raw,first in records:
            if raw.startswith('\\\\?\\'):
                if len(raw)<7 or not raw[4].isalpha() or raw[5:7]!=':\\':
                    raise ValueError('unexpected_extended_rollout_path')
                raw=raw[4:]
            original=Path(raw).resolve()
            if not original.is_relative_to(source) or original.is_symlink() or not first.startswith('Synthetic native facade first send '):
                raise ValueError('non_synthetic_or_redirected_source')
            copied=home/original.relative_to(source);copied.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(original,copied)
            if hashlib.sha256(original.read_bytes()).digest()!=hashlib.sha256(copied.read_bytes()).digest():
                raise ValueError('synthetic_copy_readback_failed')
            write.execute('UPDATE threads SET rollout_path=? WHERE id=?',(str(copied),identity))
        write.commit()
    port=workflow._available_loopback_port()
    run=IsolatedRun.start(app/'ChatGPT.exe',runs_root,environment=workflow._portable_environment(app,home),debug_port=port,isolate_shell_folders=True)
    report={'status':'failed','run_directory':str(run.run_directory),'source_home':str(source),'synthetic_only':True}
    try:
        spec=run.run_directory/'native-reopen-spec.json'
        spec.write_text(json.dumps({'workspace':str(source/'workspace'),'sent':sent}),encoding='utf8')
        env=os.environ.copy();env.update(ISOLATED_DEBUG_PORT=str(port),NATIVE_REOPEN_SPEC=str(spec))
        cp=run_awake(['node',str(Path(__file__).with_name('native_reopen.cjs'))],env=env,root=run.run_directory,timeout=180)
        (run.run_directory/'native-reopen-command.json').write_text(json.dumps({'returncode':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr},indent=2),encoding='utf8')
        if cp.returncode:raise RuntimeError(cp.stderr[-2400:])
        result=json.loads(cp.stdout)
        if result.get('status')!='passed' or len(result.get('records',[]))!=6 or result.get('ssh_reopen',{}).get('status')!='passed':
            raise RuntimeError('native_cold_reopen_incomplete')
        deadline=seconds()+30;matched=False
        while seconds()<deadline:
            state=run.status('codex.exe')
            matched=workflow._current_app_server_match(state,app,previous['backend_sha256'])
            if matched:break
            time.sleep(1)
        if not matched:raise RuntimeError('cold_reopen_backend_identity_mismatch')
        report.update(status='passed',ui=result,backend_identity=state,backend_sha256=previous['backend_sha256'])
        return report
    except BaseException as error:
        report['error']=str(error);raise
    finally:
        report['close']=workflow._normal_codex_stop(run,30)
        if report['close'].get('close_status')!='closed':report['status']='failed'
        (home/'native-cold-reopen-result.json').write_text(json.dumps(report,indent=2),encoding='utf8')
