from pathlib import Path
import json
import os
import queue
import sqlite3
import subprocess
import threading
import uuid


def prepare(home: Path, backend: Path):
    # Input is exclusively the generated synthetic fixture, never a user home.
    if not (home / 'synthetic-fixture.json').is_file():
        raise ValueError('Only an explicitly generated synthetic fixture is supported')
    env={**os.environ,'CODEX_HOME':str(home),'CODEX_SQLITE_HOME':str(home)}
    for k in list(env):
        if k.endswith('_API_KEY') or k.endswith('_TOKEN'):env.pop(k,None)
    p=subprocess.Popen([str(backend),'app-server'],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding='utf8',creationflags=0x08000000)
    replies=queue.Queue()
    threading.Thread(target=lambda:[replies.put(json.loads(line)) for line in p.stdout if line.strip()],daemon=True).start()
    counter=0
    def call(method,params):
        nonlocal counter
        counter+=1
        p.stdin.write(json.dumps({'id':counter,'method':method,'params':params})+'\n');p.stdin.flush()
        while True:
            value=replies.get(timeout=30)
            if value.get('id')==counter:
                if 'error' in value:raise RuntimeError((method,value['error']))
                return value['result']
    try:
        call('initialize',{'clientInfo':{'name':'synthetic-recency-fixture','version':'1'},'capabilities':{'experimentalApi':True}})
        p.stdin.write('{"method":"initialized","params":{}}\n');p.stdin.flush()
        existing=call('project/list',{'limit':100})['data']
        by_root={item['roots'][0]['path']:item for item in existing if item['roots']}
        with sqlite3.connect(home/'state_5.sqlite') as db:
            tasks=db.execute('select id,cwd from threads').fetchall()
        projects={}
        for cwd in sorted({cwd for _,cwd in tasks}):
            project=by_root.get(cwd)
            if project is None:
                project=call('project/create',{'name':Path(cwd).name,'roots':[{'path':cwd}],'idempotencyKey':str(uuid.uuid4())})['project']
            projects[cwd]=project
        for tid,cwd in tasks:
            call('thread/metadata/update',{'threadId':tid,'projectId':projects[cwd]['id']})
        p.stdin.close()
        if p.wait(timeout=30)!=0:raise RuntimeError('fixture app-server failed to exit')
    except BaseException:
        if p.poll() is None:
            p.stdin.close()
            p.wait(timeout=30)
        raise
    state_path=home/'.codex-global-state.json'
    state=json.loads(state_path.read_text())
    state['electron-saved-workspace-roots']=list(projects)
    state['local-projects']={v['id']:{'id':v['id'],'name':v['name'],'rootPaths':[k],'createdAt':v['createdAt']*1000,'updatedAt':v['updatedAt']*1000} for k,v in projects.items()}
    state_path.write_text(json.dumps(state),encoding='utf8')
    return {'projects':len(projects),'tasks':len(tasks)}

if __name__=='__main__':
    import sys
    print(json.dumps(prepare(Path(sys.argv[1]),Path(sys.argv[2]))))
