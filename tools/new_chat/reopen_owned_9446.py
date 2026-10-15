"""Own cold-reopen helpers, including qualified Windows IME descendants."""
from pathlib import Path
import json,os,subprocess,sys,time
from codex_desktop_workflow.owned_verification import SpaceJob,owned_process_images,qualified_auxiliary
from codex_desktop_workflow.brokered_processes import pending_elevations
from codex_desktop_workflow.awake_clock import seconds

def main():
    app,runs,previous=map(Path,sys.argv[1:4])
    before=pending_elevations(app)
    assert before['status']=='none_for_owned_candidate'
    script=Path(__file__).with_name('reopen_9446.py')
    bootstrap="import sys,runpy; assert sys.stdin.buffer.readline()==b'release-cold-reopen\\n'; sys.argv="+repr([str(script),str(app),str(runs),str(previous)])+";runpy.run_path("+repr(str(script))+",run_name='__main__')"
    job=SpaceJob();worker=None
    try:
        worker=subprocess.Popen([sys.executable,'-B','-c',bootstrap],stdin=subprocess.PIPE,creationflags=0x08000000)
        job.assign(worker);worker.stdin.write(b'release-cold-reopen\n');worker.stdin.close()
        deadline=seconds()+600
        while worker.poll() is None:
            if seconds()>=deadline:raise RuntimeError('native_cold_reopen_worker_awake_timeout')
            time.sleep(.25)
        if worker.returncode:raise RuntimeError('native_cold_reopen_worker_failed')
        pending=owned_process_images(job)
        for row in pending:
            if not qualified_auxiliary(row['image']):raise RuntimeError('unexpected_owned_cold_reopen_descendant')
        if pending:job.stop_and_wait()
        if job.pids():raise RuntimeError('cold_reopen_owned_group_not_empty')
        after=pending_elevations(app)
        assert after['status']=='none_for_owned_candidate'
        file=runs/'native-six-cold-reopen-result.json';value=json.loads(file.read_text())
        assert value['status']=='passed' and value['close']['close_status']=='closed'
        from codex_desktop_workflow.renderer_proof import parse_owned_logs
        proof=parse_owned_logs(app/'codex-desktop-workflow-manifest.json',Path(value['run_directory']),value['backend_identity']['main'])
        assert proof['status']=='passed'
        value.update(owned_cleanup={'owned_job_empty':True,'auxiliary_processes':pending},brokered_prompts=after,closed_log_readback='passed',proof=proof)
        file.write_text(json.dumps(value,indent=2))
    finally:
        job.close()
        if worker is not None and worker.poll() is None:worker.terminate();worker.wait(timeout=15)

if __name__=='__main__':main()
