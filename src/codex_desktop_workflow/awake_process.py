"""Run acceptance probes with awake-time deadlines and a shared renderer clock."""
from pathlib import Path
import json,os,subprocess,threading,time,uuid
from .awake_clock import seconds


class AwakeProcess:
    def __init__(self, command, *, env, root):
        self.root=Path(root)/('probe-'+uuid.uuid4().hex)
        self.root.mkdir(parents=True,exist_ok=False)
        self.command=command
        self.clock=self.root/'awake-clock.json'
        self.stop=threading.Event();self.clock_error=None;self.closed=False
        self.stdout=(self.root/'stdout.log').open('wb')
        self.stderr=(self.root/'stderr.log').open('wb')
        environment=dict(env);environment['CODEX_ACCEPTANCE_AWAKE_CLOCK']=str(self.clock)
        environment['CODEX_ACCEPTANCE_TIMER_MODULE']=str(Path(__file__).parent/'data/awake_timers.cjs')
        try:
            self._write_clock()
            self.process=subprocess.Popen(command,env=environment,stdout=self.stdout,stderr=self.stderr,creationflags=0x08000000)
        except BaseException:
            self.stdout.close();self.stderr.close();raise
        self.thread=threading.Thread(target=self._clock_loop,daemon=True)
        self.thread.start()

    def _write_clock(self):
        # Append complete samples; replacing a file currently read by Node can
        # be denied on Windows. Readers ignore an incomplete trailing record.
        with self.clock.open('ab', buffering=0) as stream:
            value=(json.dumps({'milliseconds':seconds()*1000})+'\n').encode('utf8')
            if stream.write(value)!=len(value):
                raise OSError('Incomplete acceptance clock write')

    def _clock_loop(self):
        while not self.stop.wait(.25):
            try:self._write_clock()
            except BaseException as error:self.clock_error=error;return

    @property
    def returncode(self):return self.process.returncode

    def poll(self):
        if self.clock_error:
            self.process.terminate()
            self.process.wait(timeout=10)
            self._close()
            raise RuntimeError('acceptance_awake_clock_unavailable') from self.clock_error
        return self.process.poll()

    def terminate(self):self.process.terminate()
    def kill(self):self.process.kill()

    def wait(self,timeout):
        deadline=seconds()+timeout
        while self.process.poll() is None:
            self.poll()
            if seconds()>=deadline:raise subprocess.TimeoutExpired(self.command,timeout)
            time.sleep(.1)
        self._close()
        return self.returncode

    def _close(self):
        self.stop.set();self.thread.join(timeout=2)
        if not self.closed:
            self.stdout.close();self.stderr.close();self.closed=True

    def communicate(self,timeout):
        self.wait(timeout)
        return (self.root/'stdout.log').read_bytes(),(self.root/'stderr.log').read_bytes()


def run(command, *, env, root, timeout):
    process=AwakeProcess(command,env=env,root=root)
    try:
        stdout,stderr=process.communicate(timeout)
        return subprocess.CompletedProcess(command,process.returncode,stdout.decode('utf8',errors='replace'),stderr.decode('utf8',errors='replace'))
    finally:
        if process.process.poll() is None:process.terminate()
        process.wait(10)
