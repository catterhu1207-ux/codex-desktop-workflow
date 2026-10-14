"""Exact 9446 SSH functions, extracted from the actual packaged entries."""
from pathlib import Path
import json,subprocess

def functions_from(raw,names,node='node'):
    tool=Path(__file__).parent/'codex_desktop_workflow/data/native_fragments_261007_9446.cjs'
    cp=subprocess.run([node,str(tool)],input=json.dumps({'source':raw.decode() if isinstance(raw,bytes) else raw,'names':list(names)}),capture_output=True,text=True,encoding='utf8',timeout=45,creationflags=0x08000000)
    if cp.returncode:raise RuntimeError('Exact native extraction failed: '+cp.stderr[-1500:])
    return json.loads(cp.stdout)

def execute_merge(entry,shared,projects,node='node'):
    f=functions_from(entry,['qZx','Tcr','Ocr','ecr','ocr','acr','ccr','scr','Lcr','ilr','II','bcr','Ecr','Dcr','MI'],node)
    f.update(functions_from(shared,['RM','LM','pxt','GM','UM','zM','BM','XL','ZL','_xt','yxt','bxt'],node))
    scenario="\nconst wa=GM,Dm=RM,dd=ZL,ok=(v,m)=>{if(!v)throw Error(m)};\nconst projects=__PROJECTS__;\nconst saved=Tcr(projects,projects.map(e=>({hostId:e.hostId,displayName:e.hostDisplayName??'Synthetic SSH'})),{});\nok(saved.length===projects.length&&saved.length>0,'Saved descriptor count');\nconst live=saved.map(e=>({...e,label:e.projectId,threadKeys:['thread:'+e.projectId]})),tasks=new Map(live.map(e=>[e.threadKeys[0],{task:{at:5}}]));\nconst merged=ocr(saved,live,tasks),picker=projects.map(e=>({...e,label:qZx(e)}));\nconst moved=ocr(saved,[{...live[0],projectId:'synthetic-changed-id',groupId:'synthetic-changed-id'}],tasks)[0];\nok(moved.projectId===saved[0].projectId&&moved.threadKeys[0]===live[0].threadKeys[0],'Host/path identity fallback');\nfor(const changed of [{...live[0],projectId:'other',hostId:'wrong-host'},{...live[0],projectId:'other',path:'/wrong-path'}])ok(ocr(saved,[changed],tasks)[0].threadKeys.length===0,'Cross-host/path merge');\nfor(const e of picker){const route=ilr({isExistingThread:false,executionHostId:e.hostId,selectedRemoteProject:e});ok(route.projectId===e.id&&route.hostId===e.hostId,'Work picker identity');ok(ilr({isExistingThread:false,executionHostId:'wrong-host',selectedRemoteProject:e})===undefined,'Work wrong host');}\nprocess.stdout.write(JSON.stringify({saved,merged,picker,moved,host_path_negatives:true,work_route_negatives:true,actual_packaged_functions:true}));\n".replace('__PROJECTS__',json.dumps(projects))
    cp=subprocess.run([node,'-'],input='\n'.join(f.values())+'\n'+scenario,capture_output=True,text=True,encoding='utf8',timeout=45,creationflags=0x08000000)
    if cp.returncode:raise RuntimeError('Actual SSH function check failed: '+cp.stderr[-1800:])
    return json.loads(cp.stdout)

def require_routes(entry,primary,shared):
    import hotfix_profile_261007_9446 as p
    for raw,groups,features in [(entry,p.PAIRS,['remote_project_label']),(primary,p.SECONDARY_PAIRS,['work_remote_project_picker']),(shared,p.SHARED_PAIRS,['renderer_shared_exports'])]:
        for name in features:
            for _,fixed in groups.get(name,()):
                if raw.count(fixed)!=1:raise RuntimeError('SSH exact route changed: '+name)
    for symbol,raw in [('function Tcr(',entry),('function ocr(',entry),('function Rcr(',entry),('function ilr(',entry),('function _L(',entry)]:
        if raw.count(symbol.encode())!=1:raise RuntimeError('Native SSH owner changed: '+symbol)
