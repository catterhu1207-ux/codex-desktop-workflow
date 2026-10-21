"""Run version-bound packaged functions on synthetic state, without private receipts."""
from pathlib import Path
import hashlib,json,subprocess,re
import hotfix_builder as b
import hotfix_integration_261013_4894 as p

def extract(source,names,functions_only=False):
    tool=Path(__file__).parent/'data/native_fragments_261013_4894.cjs'
    cp=subprocess.run(['node',str(tool)],input=json.dumps({'source':source,'names':names,'functionDeclarationsOnly':functions_only}),capture_output=True,text=True,encoding='utf8',timeout=30,creationflags=0x08000000)
    if cp.returncode:raise RuntimeError(cp.stderr[-1000:])
    return json.loads(cp.stdout)

def execute(script):
    cp=subprocess.run(['node','-'],input=script,capture_output=True,text=True,encoding='utf8',timeout=35,creationflags=0x08000000)
    if cp.returncode:raise RuntimeError(cp.stderr[-1000:])
    value=json.loads(cp.stdout);assert value['status']=='passed';value['script_sha256']=hashlib.sha256(script.encode()).hexdigest();return value

def verify(portable,official_source):
    archive=Path(portable)/'resources/app.asar';source=Path(official_source)
    if b.sha256_path(archive)!=p.TARGET_ASAR_SHA256 or b.sha256_path(source)!=p.base.SOURCE_ASAR_SHA256:raise ValueError('4894 candidate/source identity mismatch')
    size,_,header=b.read_asar(archive);ss,_,sh=b.read_asar(source)
    def read(name):return b.read_entry(archive,size,b.get_entry_meta(header,name))[1].decode()
    def old(name):return b.read_entry(source,ss,b.get_entry_meta(sh,name))[1].decode()
    initial=read(p.PROFILE['entry_path']);shared=read(p.PROFILE['shared_entry_path'])
    route='getOpenFileWatchPath(e,t,n){let r=Va(e,t);return sa(r)?n===`local`&&Ya()===`win32`?Fee(r):r:null}'
    if initial.count(route)!=1 or old(p.PROFILE['entry_path']).count(route)!=1 or shared!=old(p.PROFILE['shared_entry_path']):raise ValueError('Packaged watch binding changed')
    helpers=extract(shared,['RY','WY','K2','Z6e','$6e','q2','BY','VY','HY','J2','UY','g$'])
    watch=execute('\n'.join(helpers.values())+'\n'+WATCH)
    main=read(p.PROFILE['main_entry_path']);fn=extract(main,['pl'])['pl']
    if fn!=extract(old(p.PROFILE['main_entry_path']),['pl'])['pl']:raise ValueError('Official heartbeat guard changed')
    heartbeat=execute(fn+'\n'+HEARTBEAT)
    entries=dict(b.walk_entries(header['files']));names=[name for name in entries if name.startswith('.vite/build/') and name.endswith('.js')]
    legacy=('osPid','processRegistry','process-registry','processes.json');inventory={}
    for name in names:
        text=read(name)
        if any(token in text for token in legacy):raise ValueError('Legacy registry path returned: '+name)
        inventory[name]=hashlib.sha256(text.encode()).hexdigest()
    protocol=read(p.PROFILE['attestation_protocol_entry_path']);parts=extract(protocol,['L','K','q','J','E','D','O','A'])
    src=read('.vite/build/src-Dtwb7yKT.js')
    if 'Object.defineProperty(exports,"bi",{enumerable:!0,get:function(){return R}})' not in src:raise ValueError('Slash normalization export changed')
    normalizer=extract(src,['R'],True)['R']
    route_test=execute("const a=require('node:path');\n"+normalizer+"\nconst n={bi:R};\n"+'\n'.join(parts.values())+'\n'+PROTOCOL)
    return {'status':'passed','candidate_sha256':p.TARGET_ASAR_SHA256,'windows_watch_path_normalization':watch,'archived_heartbeat_terminal_guard':heartbeat,'process_registry_resilience':{'status':'passed','legacy_registry_absent':True,'main_module_count':len(names),'main_module_sha256':inventory},'protocol_resource_route':route_test}

WATCH="\nconst n8e=/^[A-Za-z]:[\\\\/]/,r8e=/^\\/[A-Za-z]:[\\\\/]/,\n      i8e=/^\\\\\\\\[^\\\\]+\\\\[^\\\\]+/,a8e=/^\\/\\/[^/]+\\/[^/]+/;\nconst navigator={platform:'Win32'};\nconst assert=(value,label)=>{if(!value)throw Error(label)};\nconst watch=(cwd,target,host)=>{let r=q2(cwd,target);\n return J2(r)?host==='local'&&g$()==='win32'?UY(r):r:null};\nconst cwd=String.raw`C:\\fixture`;\nassert(watch(cwd,'file.txt','local')==='C:/fixture/file.txt','relative Windows path');\nassert(watch(cwd,String.raw`C:\\fixture\\file.txt`,'local')==='C:/fixture/file.txt','absolute Windows path');\nassert(watch(cwd,'file.txt','remote')==='/C:/fixture/file.txt','remote host path preserved');\nassert(watch(String.raw`\\\\server\\share`,'file.txt','local')==='//server/share/file.txt','UNC path preserved');\nassert(watch('','relative.txt','local')===null,'unrooted path rejected');\nprocess.stdout.write(JSON.stringify({status:'passed',windows_local_relative:true,\n absolute_drive:true,remote_host_preserved:true,unc_preserved:true,unrooted_rejected:true}));\n"
HEARTBEAT="\nconst assert=(x,m)=>{if(!x)throw Error(m)};\nlet current={id:'synthetic-automation',kind:'heartbeat',status:'ACTIVE',targetThreadId:'synthetic-thread'};\nlet writes=[],deletes=[],notifications=0,code='thread_archived',triggers=0;\nconst Yc=()=>({nextScheduledRunAt:2}),Jc=()=>2,Sl=()=>null,Xc=()=>({}),xl=()=>({}),\n      ul=async()=>true,Cl=async()=>null,ol=()=>({nextRunAt:2,nextRunNominalAt:2}),\n      Zc=async()=>({}),hl=async()=>{throw {code}},l={Yt:e=>e.code},\n      Gc=()=>({warning:()=>{},debug:()=>{}}),\n      a={Jn:()=>{},Un:()=>{},An:()=>current,Xn:e=>{writes.push(e);return e}};\nconst base={statsig:{},automation:{...current,rrule:'fixture'},now:1,\n appServerConnection:{readThread:async()=>({cwd:'/synthetic'}),\n  notifyAutomationRunTriggered:()=>triggers++,notifyAutomationRunsUpdated:()=>notifications++},\n signal:{},assertCurrent:()=>{},heartbeatThreadRendererStates:new Map(),\n heartbeatThreadCollaborationModes:new Map(),heartbeatThreadPermissions:new Map(),\n updateCanonicalAutomation:()=>{},isHostedAutomationAppAvailable:async()=>true};\n(async()=>{\n await pl({...base,deleteArchivedHeartbeat:async id=>{deletes.push(id);return 'deleted'}});\n assert(deletes.length===1&&deletes[0]===current.id&&notifications===1&&!writes.length,\n        'archived heartbeat must delete once');\n deletes=[];notifications=0;writes=[];\n await pl(base);\n assert(writes.length===1&&writes[0].status==='PAUSED'&&notifications===1&&!deletes.length,\n        'missing canonical delete must pause once');\n for(const changed of [{...current,status:'PAUSED'},\n                       {...current,targetThreadId:'other'},\n                       {...current,kind:'cron'},null]){\n  current=changed;writes=[];deletes=[];notifications=0;\n  await pl({...base,deleteArchivedHeartbeat:async id=>{deletes.push(id);return 'deleted'}});\n  assert(!writes.length&&!deletes.length&&!notifications,\n         'changed canonical automation must remain untouched');\n }\n current={...base.automation};code='unrelated_failure';\n let preserved=false;\n try{await pl(base)}catch(e){preserved=e.code===code}\n assert(preserved,'unrelated failure must propagate');\n process.stdout.write(JSON.stringify({status:'passed',delete_once:true,pause_fallback:true,\n  concurrent_state_preserved:true,unrelated_error_preserved:true,triggers}));\n})().catch(e=>{process.stderr.write(String(e.stack||e));process.exitCode=1});\n"
PROTOCOL="const assert=require('node:assert/strict'),root='C:/synthetic/app/resources/app.asar/webview';\nassert.equal(L('app://-/x',root),root+'/../../x.js');\nassert.equal(a.relative(root,L('app://-/index.html',root)),'index.html');\nassert.equal(a.relative(root,L('app://-/assets/module.js',root)),a.join('assets','module.js'));\nconst invalid=['app://-/../x.js','app://-/%2e%2e/x.js','app://-/assets/%2e%2e/x.js','app://-/assets/%5c..%5cx.js','app://-/assets/.. ./x.js','app://other/x','https://-/x','file:///x','app://-/@fs/C:/private/x.js'];\nfor(const url of invalid)assert.equal(L(url,root),null,url);\nfor(const url of ['app://-/x?extra=1','app://-/x#extra','app://-/%78','app://-/x.js'])assert.notEqual(L(url,root),root+'/../../x.js',url);\nconsole.log(JSON.stringify({status:'passed',actual_packaged_resolver:true,ordinary_resources:true,negative_cases:13}));"
