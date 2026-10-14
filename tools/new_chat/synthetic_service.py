from http.server import BaseHTTPRequestHandler
from pathlib import Path
import json,os,queue,subprocess,threading,time
from codex_desktop_workflow.awake_clock import seconds
from codex_desktop_workflow.owned_verification import SpaceJob,owned_process_images,qualified_auxiliary

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length',0)))
        item={'type':'message','role':'assistant','id':'fixture-message','content':[{'type':'output_text','text':'Synthetic completed.'}]}
        events=[{'type':'response.created','response':{'id':'fixture-response'}}, {'type':'response.output_item.done','item':item}, {'type':'response.completed','response':{'id':'fixture-response','usage':{'input_tokens':0,'output_tokens':0,'total_tokens':0}}}]
        data=''.join('event: '+v['type']+'\ndata: '+json.dumps(v)+'\n\n' for v in events).encode()
        self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)

class Client:
    def __init__(self,binary,home,workspace):
        env=os.environ.copy();env.update(CODEX_HOME=str(home),CODEX_SQLITE_HOME=str(home))
        for key in tuple(env):
            if key.endswith('_API_KEY'):env.pop(key)
        self.errorlog=(home/'stderr.log').open('w',encoding='utf8')
        self.p=subprocess.Popen([str(binary),'app-server'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.errorlog,cwd=workspace,env=env,text=True,encoding='utf8',creationflags=subprocess.CREATE_NO_WINDOW)
        self.job=SpaceJob();self.job.assign(self.p)
        self.q=queue.Queue();self.id=0;self.notifications=[]
        threading.Thread(target=lambda:[self.q.put(json.loads(line)) for line in self.p.stdout if line.strip()],daemon=True).start()
        response=self.call('initialize',{'clientInfo':{'name':'synthetic-isolation','version':'1'},'capabilities':{'experimentalApi':True}})
        if 'error' in response:raise RuntimeError(response)
        self.p.stdin.write(json.dumps({'method':'initialized','params':{}})+'\n');self.p.stdin.flush()
    def call(self,method,params):
        self.id+=1;request_id=self.id
        self.p.stdin.write(json.dumps({'id':request_id,'method':method,'params':params})+'\n');self.p.stdin.flush()
        deadline=seconds()+45
        while seconds()<deadline:
            try:message=self.q.get(timeout=min(.25,max(.1,deadline-seconds())))
            except queue.Empty:continue
            if message.get('id')==request_id:return message
            self.notifications.append(message)
        raise TimeoutError(method)
    def finish_turn(self):
        if any(n.get('method')=='turn/completed' for n in self.notifications):return
        deadline=seconds()+45
        while seconds()<deadline:
            try:msg=self.q.get(timeout=min(.25,max(.1,deadline-seconds())))
            except queue.Empty:continue
            if msg.get('method')=='turn/completed':return
        raise TimeoutError('turn/completed')
    def close(self):
        self.p.stdin.close()
        try:self.p.wait(timeout=15)
        except subprocess.TimeoutExpired:
            self.p.terminate();self.p.wait(timeout=10)
        try:
            auxiliary=owned_process_images(self.job)
            git_root=Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Git'
            for row in auxiliary:
                image=Path(row['image']).resolve()
                if image.name.lower()!='conhost.exe' and not image.is_relative_to(git_root.resolve()):
                    raise RuntimeError('unexpected_synthetic_backend_descendant')
                if not qualified_auxiliary(row['image']):raise RuntimeError('unqualified_synthetic_backend_descendant')
            if auxiliary:self.job.stop_and_wait()
            self.owned_cleanup={'owned_job_empty':not self.job.pids(),'auxiliary_processes':auxiliary}
        finally:
            self.job.close();self.errorlog.close()
