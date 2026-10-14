from pathlib import Path
import sys,os,json,sqlite3,hashlib,threading,uuid,subprocess,queue,time,ctypes
from http.server import ThreadingHTTPServer
R=Path(os.environ['CODEX_ACCEPTANCE_OUTPUT']).resolve()
from codex_desktop_workflow.native_history_fixture import Client,Handler,message
from codex_desktop_workflow.awake_clock import seconds
from codex_desktop_workflow.owned_verification import SpaceJob,owned_process_images
cleanup_records=[]
class OwnedClient(Client):
    def __init__(self,binary,home,workspace):
        self.job=SpaceJob();self.log=(home/'synthetic-backend-stderr.log').open('a',encoding='utf8')
        env=dict(os.environ,CODEX_HOME=str(home),CODEX_SQLITE_HOME=str(home))
        for key in list(env):
            if key.endswith('_API_KEY') or key.endswith('_TOKEN'):env.pop(key)
        try:
            self.process=subprocess.Popen([str(binary),'app-server'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,cwd=workspace,env=env,text=True,encoding='utf8',creationflags=subprocess.CREATE_NO_WINDOW|0x4)
            self.job.assign(self.process)
            native=ctypes.WinDLL('ntdll');native.NtResumeProcess.argtypes=[ctypes.c_void_p];native.NtResumeProcess.restype=ctypes.c_long
            if native.NtResumeProcess(int(self.process._handle))!=0:raise RuntimeError('Owned backend resume failed')
            self.q=queue.Queue();self.id=0;self.notifications=[]
            threading.Thread(target=self._read,daemon=True).start()
            initialized=self.call('initialize',{'clientInfo':{'name':'synthetic-missing-history-acceptance','version':'1'},'capabilities':{'experimentalApi':True}})
            if 'error' in initialized:raise RuntimeError(initialized)
            self.process.stdin.write(json.dumps({'method':'initialized','params':{}})+'\n');self.process.stdin.flush()
        except BaseException:
            self.job.stop_and_wait();self.job.close();self.log.close();raise
    def close(self):
        try:
            super().close()
            deadline=seconds()+2
            while self.job.pids() and seconds()<deadline:time.sleep(.05)
            residual=owned_process_images(self.job) if self.job.pids() else []
            stopped=self.job.stop_and_wait() if residual else []
            for _ in range(3):
                assert not self.job.pids(),'Owned descendants survived closure';time.sleep(.1)
            cleanup_records.append({'backend_normal_close':True,'residual_owned_children':residual,'owned_children_stopped':stopped,'owned_job_empty':True,'current_application_unaffected':True})
        finally:self.job.close()
Client=OwnedClient
binary=Path(sys.argv[1]).resolve()
root=R/('missing-source-'+uuid.uuid4().hex);root.mkdir(parents=True,exist_ok=False)
home=root/'home';home.mkdir(exist_ok=True);workspace=home/'workspace';workspace.mkdir(exist_ok=True)
if (home/'state_5.sqlite').exists():
    with sqlite3.connect((home/'state_5.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        assert db.execute('select count(*) from threads').fetchone()[0]==0,'Reconcile previous writes before replay'
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
(home/'config.toml').write_text(f'model_provider="fixture"\nmodel="fixture-model"\n[model_providers.fixture]\nname="Isolated"\nbase_url="http://127.0.0.1:{server.server_port}/v1"\nwire_api="responses"\nrequires_openai_auth=false\n')
c=Client(binary,home,workspace)
try:
    started=c.call('thread/start',{'cwd':str(workspace),'model':'fixture-model','modelProvider':'fixture','approvalPolicy':'never','sandbox':'read-only','persistExtendedHistory':True,'historyMode':'legacy'})
    if 'error' in started:raise RuntimeError(started)
    tid=started['result']['thread']['id'];c.notifications=[]
    sent=c.call('turn/start',{'threadId':tid,'input':[{'type':'text','text':'Synthetic saved legacy history negative','textElements':[]}]})
    if 'error' in sent:raise RuntimeError(sent)
    deadline=seconds()+45
    completed=next((n for n in c.notifications if n.get('method')=='turn/completed' and n.get('params',{}).get('threadId')==tid),None)
    while completed is None:
        n=message(c.q,deadline)
        if n.get('method')=='turn/completed' and n.get('params',{}).get('threadId')==tid:completed=n
    assert completed['params']['turn']['status']=='completed'
    before=c.call('thread/read',{'threadId':tid,'includeTurns':True});assert before['result']['thread']['turns']
finally:c.close();server.shutdown();server.server_close()
with sqlite3.connect((home/'state_5.sqlite').as_uri()+'?mode=ro',uri=True) as db:
    path,mode=db.execute('select rollout_path,history_mode from threads where id=?',(tid,)).fetchone()
source=Path(path).resolve();assert source.is_relative_to(home) and source.is_file()
original=hashlib.sha256(source.read_bytes()).hexdigest();held=source.with_suffix(source.suffix+'.held');assert not held.exists()
source.rename(held)
results={}
try:
    c=Client(binary,home,workspace)
    try:
        for method,params in [('thread/read',{'threadId':tid,'includeTurns':True}),('thread/resume',{'threadId':tid})]:
            results[method]=c.call(method,params)
    finally:c.close()
finally:
    held.rename(source)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==original
read=results['thread/read'].get('error',{});resume=results['thread/resume'].get('error',{})
passed=(read.get('code')==-32600 and read.get('message','').startswith('thread not loaded: ') and resume.get('code')==-32600 and 'failed to resolve rollout path' in resume.get('message','') and 'file does not exist' in resume.get('message',''))
receipt={'status':'passed' if passed else 'failed','backend_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'saved_thread_created_and_sent':True,'history_mode':mode,'user_data_copied':False,'original_synthetic_rollout_restored':True,'results':results,'owned_backend_cleanup':cleanup_records}
(root/'result.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
if not passed:raise RuntimeError('Materialized missing saved-source refusal not proven')
