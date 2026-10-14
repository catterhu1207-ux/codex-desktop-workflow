"""Generate histories through the candidate backend and a local Responses service."""
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import hashlib, json, os, queue, sqlite3, subprocess, threading, time
from .awake_clock import seconds

def message(q, deadline):
    while seconds() < deadline:
        try:return q.get(timeout=min(.25, max(.01,deadline-seconds())))
        except queue.Empty:pass
    raise TimeoutError('synthetic backend response deadline')

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length',0)))
        item={'type':'message','role':'assistant','id':'fixture-message','content':[{'type':'output_text','text':'Synthetic completed.'}]}
        events=[{'type':'response.created','response':{'id':'fixture-response'}},{'type':'response.output_item.done','item':item},{'type':'response.completed','response':{'id':'fixture-response','usage':{'input_tokens':0,'output_tokens':0,'total_tokens':0}}}]
        data=''.join('event: '+v['type']+'\ndata: '+json.dumps(v)+'\n\n' for v in events).encode()
        self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)

class Client:
    def __init__(self,binary,home,workspace):
        env=dict(os.environ,CODEX_HOME=str(home),CODEX_SQLITE_HOME=str(home))
        for key in list(env):
            if key.endswith('_API_KEY'):env.pop(key)
        self.log=(home/'synthetic-backend-stderr.log').open('w',encoding='utf8')
        self.process=subprocess.Popen([str(binary),'app-server'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,cwd=workspace,env=env,text=True,encoding='utf8',creationflags=subprocess.CREATE_NO_WINDOW)
        self.q=queue.Queue();self.id=0;self.notifications=[]
        threading.Thread(target=self._read,daemon=True).start()
        initialized=self.call('initialize',{'clientInfo':{'name':'synthetic-release-acceptance','version':'1'},'capabilities':{'experimentalApi':True}})
        if 'error' in initialized:raise ValueError(initialized)
        self.process.stdin.write(json.dumps({'method':'initialized','params':{}})+'\n');self.process.stdin.flush()
    def _read(self):
        for line in self.process.stdout:
            if line.strip():self.q.put(json.loads(line))
    def call(self,method,params):
        self.id+=1
        self.process.stdin.write(json.dumps({'id':self.id,'method':method,'params':params})+'\n');self.process.stdin.flush()
        deadline=seconds()+45
        while True:
            result=message(self.q,deadline)
            if result.get('id')==self.id:return result
            self.notifications.append(result)
    def close(self):
        self.process.stdin.close();deadline=seconds()+15
        while self.process.poll() is None and seconds()<deadline:time.sleep(.1)
        if self.process.poll() is None:self.process.terminate();self.process.wait(timeout=10)
        self.log.close()

def generate(home:Path,binary:Path,count:int=400):
    home=home.resolve()
    if (home/'state_5.sqlite').exists() or (home/'sessions').exists():raise ValueError('native_history_target_must_be_fresh')
    workspace=home/'synthetic-workspaces';workspace.mkdir()
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    config=home/'config.toml'
    if config.exists():raise ValueError('synthetic_config_must_not_replace_existing')
    config.write_text(f'model_provider="fixture"\nmodel="fixture-model"\nmodel_reasoning_effort="medium"\n[model_providers.fixture]\nname="Synthetic loopback"\nbase_url="http://127.0.0.1:{server.server_port}/v1"\nwire_api="responses"\nrequires_openai_auth=false\n',encoding='utf8')
    c=Client(binary,home,workspace);ids=[];reads=[]
    try:
        for index in range(count):
            cwd=workspace/str(index%12);cwd.mkdir(exist_ok=True)
            started=c.call('thread/start',{'cwd':str(cwd),'model':'fixture-model','modelProvider':'fixture','approvalPolicy':'never','sandbox':'read-only','persistExtendedHistory':True,'historyMode':'paginated'})
            if 'error'in started:raise ValueError(started)
            tid=started['result']['thread']['id'];ids.append(tid);c.notifications=[]
            sent=c.call('turn/start',{'threadId':tid,'input':[{'type':'text','text':f'Synthetic startup task {index}','textElements':[]}]})
            if 'error'in sent:raise ValueError(sent)
            deadline=seconds()+45
            completed=next((n for n in c.notifications if n.get('method')=='turn/completed' and n.get('params',{}).get('threadId')==tid),None)
            while completed is None:
                n=message(c.q,deadline)
                if n.get('method')=='turn/completed' and n.get('params',{}).get('threadId')==tid:completed=n
            if completed['params']['turn']['status']!='completed':raise ValueError('synthetic turn failed')
        for tid in (ids[0],ids[-1]):
            read=c.call('thread/read',{'threadId':tid,'includeTurns':True})
            if 'error'in read or len(read['result']['thread']['turns'])!=1:raise ValueError('native first/last history read failed')
            reads.append({'id':tid,'turn_count':1,'identity_match':read['result']['thread']['id']==tid})
    finally:c.close();server.shutdown();server.server_close()
    inventory={}
    with closing(sqlite3.connect((home/'state_5.sqlite').as_uri()+'?mode=ro',uri=True)) as db:
        rows=db.execute('select id,rollout_path,preview,model,history_mode from threads').fetchall()
        if len(rows)!=count or {r[0] for r in rows}!=set(ids):raise ValueError('native catalog identity mismatch')
        for tid,raw,preview,model,mode in rows:
            path=Path(raw).resolve()
            if not path.is_relative_to(home) or not preview.startswith('Synthetic startup task ') or model!='fixture-model' or mode!='paginated':raise ValueError('native history metadata mismatch')
            inventory[path.relative_to(home).as_posix()]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':path.stat().st_size}
    if not (home/'thread_history_1.sqlite').is_file():raise ValueError('native pagination database missing')
    report={'status':'native_synthetic_history_prepared','count':count,'all_created_and_sent_by_actual_backend':True,'backend_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'native_history_index_retained':True,'ids':ids,'first_last_live_checks':reads,'files':inventory,'user_data_copied':False}
    (home/'qualified-synthetic-files.json').write_text(json.dumps(inventory,indent=2),encoding='utf8')
    (home/'native-history-fixture.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    return report
