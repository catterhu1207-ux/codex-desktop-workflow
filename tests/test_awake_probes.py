from pathlib import Path
import json,os,shutil,subprocess,sys,tempfile,time,unittest
from codex_desktop_workflow import awake_process
from unittest.mock import patch


class AwakeProbes(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node') and os.name=='nt','Windows and Node required')
    def test_concurrent_node_reads_and_python_clock_updates(self):
        with tempfile.TemporaryDirectory() as raw:
            code="const {now}=require(process.env.CODEX_ACCEPTANCE_TIMER_MODULE);const end=now()+1200;let count=0;const id=setInterval(()=>{count++;if(now()>=end){clearInterval(id);console.log(count)}},1)"
            result=awake_process.run(['node','-e',code],env=os.environ.copy(),root=Path(raw),timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertGreater(int(result.stdout),100)

    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_incomplete_trailing_sample_does_not_replace_complete_sample(self):
        with tempfile.TemporaryDirectory() as raw:
            clock=Path(raw)/'clock.json';clock.write_text('{"milliseconds":1000}\n{"milliseconds":')
            module=Path(awake_process.__file__).parent/'data/awake_timers.cjs'
            env=os.environ.copy();env['CODEX_ACCEPTANCE_AWAKE_CLOCK']=str(clock)
            result=subprocess.run(['node','-e','console.log(require('+json.dumps(str(module))+').now())'],env=env,capture_output=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout.strip(),b'1000')

    def test_clock_appends_complete_samples_without_replacing_readers(self):
        with tempfile.TemporaryDirectory() as raw:
            probe=object.__new__(awake_process.AwakeProcess)
            probe.clock=Path(raw)/'clock.json'
            probe._write_clock();before=probe.clock.read_bytes()
            with probe.clock.open('rb') as reader:
                probe._write_clock()
                after=reader.read()
            self.assertTrue(after.startswith(before))
            values=[json.loads(line)['milliseconds'] for line in after.splitlines()]
            self.assertEqual(len(values),2)
            self.assertGreaterEqual(values[1],values[0])
            with patch.object(Path,'open',side_effect=PermissionError('write unavailable')):
                with self.assertRaises(PermissionError):probe._write_clock()

    @unittest.skipUnless(shutil.which('node'), 'Node required')
    def test_wall_time_does_not_expire_a_paused_awake_clock(self):
        with tempfile.TemporaryDirectory() as raw:
            clock=Path(raw)/'clock.json';clock.write_text(json.dumps({'milliseconds':1000})+'\n')
            module=Path(awake_process.__file__).parent/'data/awake_timers.cjs'
            env=os.environ.copy();env['CODEX_ACCEPTANCE_AWAKE_CLOCK']=str(clock)
            code="const {setTimeout}=require("+json.dumps(str(module))+");setTimeout(()=>{process.stdout.write('elapsed');},100)"
            child=subprocess.Popen(['node','-e',code],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                time.sleep(.6)
                self.assertIsNone(child.poll(), 'Wall time must not expire an unchanged awake clock')
                with clock.open('a') as stream:stream.write(json.dumps({'milliseconds':1101})+'\n')
                stdout,stderr=child.communicate(timeout=5)
                self.assertEqual(child.returncode,0,stderr)
                self.assertEqual(stdout,b'elapsed')
            finally:
                if child.poll() is None:child.kill();child.wait(timeout=5)

    @unittest.skipUnless(os.name=='nt','Windows acceptance process')
    def test_large_probe_output_does_not_block_process_completion(self):
        with tempfile.TemporaryDirectory() as raw:
            result=awake_process.run([sys.executable,'-c',"print('x'*100000)"],env=os.environ.copy(),root=Path(raw),timeout=10)
            self.assertEqual(result.returncode,0)
            self.assertEqual(len(result.stdout.strip()),100000)

    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_invalid_awake_clock_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            clock=Path(raw)/'clock.json';clock.write_text('{"milliseconds":"invalid"}\n')
            module=Path(awake_process.__file__).parent/'data/awake_timers.cjs'
            env=os.environ.copy();env['CODEX_ACCEPTANCE_AWAKE_CLOCK']=str(clock)
            result=subprocess.run(['node','-e','require('+json.dumps(str(module))+').now()'],env=env,capture_output=True,timeout=5)
            self.assertNotEqual(result.returncode,0)
            self.assertIn(b'Invalid acceptance awake clock',result.stderr)


if __name__=='__main__':unittest.main()
