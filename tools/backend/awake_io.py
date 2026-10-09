"""Awake-time waits for isolated synthetic backend acceptance."""
from pathlib import Path
import os
import queue
import subprocess
import time
import uuid
from codex_desktop_workflow.awake_clock import seconds
from codex_desktop_workflow.owned_verification import SpaceJob,owned_process_images,qualified_auxiliary


def owned_popen(*args,**kwargs):
    process=subprocess.Popen(*args,**kwargs)
    job=SpaceJob()
    try:job.assign(process)
    except BaseException:
        job.close();process.terminate();process.wait(timeout=10);raise
    process._acceptance_owned_job=job
    return process


def message(messages, deadline):
    while seconds() < deadline:
        try:
            return messages.get(timeout=.1)
        except queue.Empty:
            pass
    raise TimeoutError('Backend message awake budget exceeded')


def wait(process, timeout):
    deadline=seconds()+timeout
    while process.poll() is None:
        if seconds() >= deadline:
            raise subprocess.TimeoutExpired(process.args,timeout)
        time.sleep(.1)
    job=getattr(process,'_acceptance_owned_job',None)
    if job is not None:
        try:
            auxiliary=owned_process_images(job)
            git_root=(Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Git').resolve()
            for row in auxiliary:
                image=Path(row['image']).resolve()
                if image.name.lower()!='conhost.exe' and not image.is_relative_to(git_root):
                    raise RuntimeError('unexpected_backend_acceptance_descendant')
                if not qualified_auxiliary(row['image']):raise RuntimeError('unqualified_backend_acceptance_descendant')
            if auxiliary:job.stop_and_wait()
            process.owned_cleanup={'owned_job_empty':not job.pids(),'auxiliary_processes':auxiliary}
        finally:job.close();process._acceptance_owned_job=None
    return process.returncode


def run(command, *, cwd, env, timeout):
    root=Path(env['CODEX_ACCEPTANCE_OUTPUT'])/('capture-'+uuid.uuid4().hex)
    root.mkdir()
    with (root/'stdout').open('w+b') as out,(root/'stderr').open('w+b') as err:
        process=owned_popen(command,cwd=cwd,env=env,stdout=out,stderr=err,creationflags=0x08000000)
        try:
            wait(process,timeout)
            out.seek(0);err.seek(0)
            return subprocess.CompletedProcess(command,process.returncode,out.read().decode('utf8',errors='replace'),err.read().decode('utf8',errors='replace'))
        finally:
            if process.poll() is None:
                process.terminate()
                wait(process,10)
