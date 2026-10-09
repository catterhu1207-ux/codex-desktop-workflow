"""Identity-owned Windows process group for isolated release verification."""
import ctypes
from ctypes import wintypes
import time
import subprocess
import sys
import json
import os
from pathlib import Path
from . import awake_clock
class OwnedWorkerJob:
    def __init__(self):
        if os.name != "nt":
            raise RuntimeError("Background qualification supervision requires Windows")

        class BasicLimits(ctypes.Structure):
            _fields_ = [
                ("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                ("flags", wintypes.DWORD), ("minimum_working_set", ctypes.c_size_t),
                ("maximum_working_set", ctypes.c_size_t), ("active_process_limit", wintypes.DWORD),
                ("affinity", ctypes.c_size_t), ("priority_class", wintypes.DWORD),
                ("scheduling_class", wintypes.DWORD),
            ]

        class IoCounters(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in (
                "read_operations", "write_operations", "other_operations",
                "read_bytes", "write_bytes", "other_bytes",
            )]

        class ExtendedLimits(ctypes.Structure):
            _fields_ = [
                ("basic", BasicLimits), ("io", IoCounters),
                ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
                ("peak_process_memory", ctypes.c_size_t), ("peak_job_memory", ctypes.c_size_t),
            ]

        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.kernel.CreateJobObjectW.restype = wintypes.HANDLE
        self.kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.kernel.SetInformationJobObject.restype = wintypes.BOOL
        self.kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.kernel.AssignProcessToJobObject.restype = wintypes.BOOL
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel.CloseHandle.restype = wintypes.BOOL
        self.handle = self.kernel.CreateJobObjectW(None, None)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = ExtendedLimits()
        limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.kernel.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def assign(self, worker):
        if not self.kernel.AssignProcessToJobObject(self.handle, int(worker._handle)):
            raise ctypes.WinError(ctypes.get_last_error())

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None

class SpaceJob(OwnedWorkerJob):
    def __init__(self):
        super().__init__()
        self.kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.kernel.TerminateJobObject.restype = wintypes.BOOL
        self.kernel.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                                         ctypes.c_void_p, wintypes.DWORD,
                                                         ctypes.c_void_p]
        self.kernel.QueryInformationJobObject.restype = wintypes.BOOL

    def pids(self):
        capacity = 64
        while capacity <= 65536:
            buf = ctypes.create_string_buffer(8 + capacity * ctypes.sizeof(ctypes.c_size_t))
            ok = self.kernel.QueryInformationJobObject(self.handle, 3, buf, len(buf), None)
            if ok:
                count = ctypes.c_uint32.from_buffer(buf, 4).value
                arr = (ctypes.c_size_t * count).from_buffer(buf, 8)
                return list(arr)
            error = ctypes.get_last_error()
            if error != 234:
                raise ctypes.WinError(error)
            capacity *= 2
        raise RuntimeError('owned job process inventory exceeded limit')

    def stop_and_wait(self):
        before = self.pids()
        if not self.kernel.TerminateJobObject(self.handle, 75):
            raise ctypes.WinError(ctypes.get_last_error())
        deadline = time.monotonic() + 15
        while self.pids():
            if time.monotonic() >= deadline:
                raise RuntimeError('owned job descendants did not terminate')
            time.sleep(0.05)
        return before

TOKEN=b'release-public-verification-worker\n'

def _owned_process_image(job,pid):
    kernel=job.kernel
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
    kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.QueryFullProcessImageNameW.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)]
    kernel.IsProcessInJob.argtypes=[wintypes.HANDLE,wintypes.HANDLE,ctypes.POINTER(wintypes.BOOL)]
    kernel.IsProcessInJob.restype=wintypes.BOOL
    handle=kernel.OpenProcess(0x1000,False,pid)
    try:
        if not handle:raise OSError('owned_process_handle_unavailable')
        belongs=wintypes.BOOL()
        if not kernel.IsProcessInJob(handle,job.handle,ctypes.byref(belongs)) or not belongs.value:
            raise OSError('process_is_not_in_owned_job')
        buffer=ctypes.create_unicode_buffer(32768);size=wintypes.DWORD(len(buffer))
        if not kernel.QueryFullProcessImageNameW(handle,0,buffer,ctypes.byref(size)):
            raise OSError('owned_process_image_unavailable')
        return buffer.value
    finally:
        if handle:kernel.CloseHandle(handle)


def owned_process_images(job):
    result=[]
    for pid in job.pids():
        try:image=_owned_process_image(job,pid)
        except OSError as error:
            # Natural exit between enumeration and OpenProcess is permissible
            # only after a fresh job query confirms this PID is no longer owned.
            if pid not in job.pids():continue
            raise RuntimeError('owned_process_identity_unavailable') from error
        result.append({'pid':pid,'image':image})
    return result

def qualified_auxiliary(image):
    path=Path(image).resolve()
    if path.name.lower() in {'git.exe','git-remote-https.exe','conhost.exe'}:
        return True
    root=os.environ.get('ProgramFiles(x86)')
    if not root or path.name.lower()!='sgtool.exe' or not path.is_relative_to((Path(root)/'SogouInput').resolve()):
        return False
    # Some Windows IMEs start an auxiliary process inside the test window's job.
    # Qualify its installed location and publisher before treating it as cleanup.
    env=os.environ.copy();env['OWNED_AUXILIARY_IMAGE']=str(path)
    script="$ErrorActionPreference='Stop'; Import-Module (Join-Path $PSHOME 'Modules/Microsoft.PowerShell.Security/Microsoft.PowerShell.Security.psd1'); $s=Get-AuthenticodeSignature -LiteralPath $env:OWNED_AUXILIARY_IMAGE; @{status=[string]$s.Status;subject=[string]$s.SignerCertificate.Subject}|ConvertTo-Json -Compress"
    command=['powershell.exe','-NoProfile','-NonInteractive','-Command',script]
    wrapper="import subprocess,sys; assert sys.stdin.buffer.readline()==b'release-signature-worker\\n'; p=subprocess.run("+repr(command)+",capture_output=True,timeout=15,creationflags=0x08000000);sys.stdout.buffer.write(p.stdout);sys.stderr.buffer.write(p.stderr);sys.exit(p.returncode)"
    signature_job=SpaceJob();worker=None
    try:
        worker=subprocess.Popen([sys.executable,'-c',wrapper],env=env,stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000)
        signature_job.assign(worker)
        stdout,stderr=worker.communicate(b'release-signature-worker\n',timeout=25)
        code=worker.returncode
        if signature_job.pids():signature_job.stop_and_wait()
    finally:
        signature_job.close()
        if worker is not None and worker.poll() is None:worker.terminate();worker.wait(timeout=10)
    try:value=json.loads(stdout)
    except ValueError:return False
    return code==0 and value.get('status')=='Valid' and value.get('subject','').startswith('CN="Beijing Sogou Technology Development Co., Ltd.",')

def verify_owned(source, portable, runs_root, observe_seconds, launches):
    root=Path(runs_root).resolve()
    root.mkdir(parents=True,exist_ok=True)
    owner=root/('owner-'+os.urandom(8).hex())
    owner.mkdir()
    arguments={'source':str(source.resolve()),'portable':str(portable.resolve()),
               'runs_root':str(root),'observe_seconds':observe_seconds,'launches':launches}
    request=owner/'request.json';request.write_text(json.dumps(arguments),encoding='utf8')
    result=owner/'result.json';job=SpaceJob();worker=None
    env=os.environ.copy()
    env['PYTHONPATH']=str(Path(__file__).resolve().parent.parent)+os.pathsep+env.get('PYTHONPATH','')
    try:
        with (owner/'stdout.log').open('wb') as stdout,(owner/'stderr.log').open('wb') as stderr:
            worker=subprocess.Popen([sys.executable,'-X','utf8','-m',__name__,str(request)],
                env=env,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,creationflags=0x08000000)
            job.assign(worker)
            worker.stdin.write(TOKEN);worker.stdin.close()
            deadline=awake_clock.seconds()+max(3,launches)*420+180
            while worker.poll() is None:
                if awake_clock.seconds()>=deadline:raise RuntimeError('owned_verification_awake_budget_exceeded')
                time.sleep(.25)
        if worker.returncode:
            raise RuntimeError('owned_verification_failed: '+(owner/'stderr.log').read_text(encoding='utf8',errors='replace')[-2400:])
        pending=[]
        for row in owned_process_images(job):
            pid,image=row['pid'],row['image']
            if not qualified_auxiliary(image):
                raise RuntimeError('unexpected_owned_process_after_normal_close: '+Path(image).name)
            pending.append({'pid':pid,'image':image})
        if pending:job.stop_and_wait()
        if job.pids():raise RuntimeError('owned_descendants_remain')
        value=json.loads(result.read_text(encoding='utf8'))
        value['owned_cleanup']={'owned_job_empty':True,'auxiliary_processes':pending}
        # Read the complete logs after natural exit, including late failures.
        from .renderer_proof import parse_owned_logs
        if value.get('bundle',{}).get('package_version') == '26.1002.7124.0':
            manifest=portable/'codex-desktop-workflow-manifest.json'
            for run in value['runtime']:
                proof=parse_owned_logs(manifest,Path(run['run_directory']),run['pre_close']['main'])
                if proof.get('status')!='passed':raise RuntimeError('final_closed_renderer_proof_rejected')
                run['attestation']=proof
            value['closed_log_readback']='passed'
        result.write_text(json.dumps(value,indent=2),encoding='utf8')
        (portable/'codex-desktop-workflow-verification.json').write_text(json.dumps(value,indent=2),encoding='utf8')
        return value
    finally:
        job.close()
        if worker is not None and worker.poll() is None:worker.terminate();worker.wait(timeout=15)

if __name__=='__main__':
    if sys.stdin.buffer.readline()!=TOKEN:raise RuntimeError('worker_not_released')
    from .workflow import _verify_isolated
    request=Path(sys.argv[1]);args=json.loads(request.read_text(encoding='utf8'))
    for key in ('source','portable','runs_root'):args[key]=Path(args[key])
    value=_verify_isolated(**args)
    (request.parent/'result.json').write_text(json.dumps(value,indent=2),encoding='utf8')
