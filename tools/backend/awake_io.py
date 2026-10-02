"""Awake-time waits for isolated synthetic backend acceptance."""
from pathlib import Path
import os
import queue
import subprocess
import time
import uuid
from codex_desktop_workflow.awake_clock import seconds


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
    return process.returncode


def run(command, *, cwd, env, timeout):
    root=Path(env['CODEX_ACCEPTANCE_OUTPUT'])/('capture-'+uuid.uuid4().hex)
    root.mkdir()
    with (root/'stdout').open('w+b') as out,(root/'stderr').open('w+b') as err:
        process=subprocess.Popen(command,cwd=cwd,env=env,stdout=out,stderr=err,creationflags=0x08000000)
        try:
            wait(process,timeout)
            out.seek(0);err.seek(0)
            return subprocess.CompletedProcess(command,process.returncode,out.read().decode('utf8',errors='replace'),err.read().decode('utf8',errors='replace'))
        finally:
            if process.poll() is None:
                process.terminate()
                wait(process,10)
