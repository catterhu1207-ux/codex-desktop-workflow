"""Exercise the exact 6573 packaged functions with synthetic inputs."""
from pathlib import Path
import hashlib
import hotfix_builder as b
import hotfix_integration_261016_6573 as p
from .native_checks_4894 import extract,execute,PROTOCOL

def verify(portable,official_source):
    archive=Path(portable)/'resources/app.asar';source=Path(official_source)
    if b.sha256_path(archive)!=p.TARGET_ASAR_SHA256 or b.sha256_path(source)!=p.base.SOURCE_ASAR_SHA256:
        raise ValueError('6573 candidate/source identity mismatch')
    size,_,header=b.read_asar(archive);ss,_,sh=b.read_asar(source)
    def read(name):return b.read_entry(archive,size,b.get_entry_meta(header,name))[1].decode()
    def original(name):return b.read_entry(source,ss,b.get_entry_meta(sh,name))[1].decode()
    initial=read(p.PROFILE['entry_path']);shared=read(p.PROFILE['shared_entry_path'])
    route='getOpenFileWatchPath(e,t,n){let r=Fi(e,t);return gc(r)?n===`local`&&os()===`win32`?Ka(r):r:null}'
    if initial.count(route)!=1 or original(p.PROFILE['entry_path']).count(route)!=1 or shared!=original(p.PROFILE['shared_entry_path']):
        raise ValueError('Packaged watch binding changed')
    helpers=extract(shared,['XU','rW','q2','tW','ent','J2','QU','$U','eW','Y2','nW','CQ'])
    watch=execute('\n'.join(helpers.values())+'\n'+WATCH)
    main=read(p.PROFILE['main_entry_path']);fn=extract(main,['vl'])['vl']
    if fn!=extract(original(p.PROFILE['main_entry_path']),['vl'])['vl']:
        raise ValueError('Official heartbeat guard changed')
    heartbeat=execute(fn+'\n'+HEARTBEAT)
    entries=dict(b.walk_entries(header['files']))
    names=[name for name in entries if name.startswith('.vite/build/') and name.endswith('.js')]
    legacy=('osPid','processRegistry','process-registry','processes.json');inventory={}
    for name in names:
        text=read(name)
        if any(token in text for token in legacy):raise ValueError('Legacy registry path returned: '+name)
        inventory[name]=hashlib.sha256(text.encode()).hexdigest()
    protocol=read(p.PROFILE['attestation_protocol_entry_path'])
    parts=extract(protocol,['L','K','q','J','E','D','O','A'])
    src=read('.vite/build/src-CSKkIr_z.js')
    if 'Object.defineProperty(exports,"xi",{enumerable:!0,get:function(){return z}})' not in src:
        raise ValueError('Slash normalization export changed')
    normalizer=extract(src,['z'],True)['z']
    route_test=execute("const a=require('node:path');\n"+normalizer+"\nconst n={xi:z};\n"+'\n'.join(parts.values())+'\n'+PROTOCOL)
    return {'status':'passed','candidate_sha256':p.TARGET_ASAR_SHA256,
      'windows_watch_path_normalization':watch,'archived_heartbeat_terminal_guard':heartbeat,
      'process_registry_resilience':{'status':'passed','legacy_registry_absent':True,'main_module_count':len(names),'main_module_sha256':inventory},
      'protocol_resource_route':route_test}

WATCH="\nconst rnt=/^[A-Za-z]:[\\\\/]/,int=/^\\/[A-Za-z]:[\\\\/]/,\n      ant=/^\\\\\\\\[^\\\\]+\\\\[^\\\\]+/,ont=/^\\/\\/[^/]+\\/[^/]+/;\nconst navigator={platform:'Win32'};\nconst assert=(value,label)=>{if(!value)throw Error(label)};\nconst watch=(cwd,target,host)=>{let r=J2(cwd,target);\n return Y2(r)?host==='local'&&CQ()==='win32'?nW(r):r:null};\nconst cwd=String.raw`C:\\fixture`;\nassert(watch(cwd,'file.txt','local')==='C:/fixture/file.txt','relative Windows path');\nassert(watch(cwd,String.raw`C:\\fixture\\file.txt`,'local')==='C:/fixture/file.txt','absolute Windows path');\nassert(watch(cwd,'file.txt','remote')==='/C:/fixture/file.txt','remote host path preserved');\nassert(watch(String.raw`\\\\server\\share`,'file.txt','local')==='//server/share/file.txt','UNC path preserved');\nassert(watch('','relative.txt','local')===null,'unrooted path rejected');\nprocess.stdout.write(JSON.stringify({status:'passed',windows_local_relative:true,\n absolute_drive:true,remote_host_preserved:true,unc_preserved:true,unrooted_rejected:true}));\n"
HEARTBEAT="\nconst assert=(x,m)=>{if(!x)throw Error(m)};\nlet current={id:'synthetic-automation',kind:'heartbeat',status:'ACTIVE',targetThreadId:'synthetic-thread'};\nlet writes=[],deletes=[],notifications=0,code='thread_archived',triggers=0,hosted=[],model='fixture',skips=0;\nconst tl=()=>({nextScheduledRunAt:2}),el=()=>2,Dl=()=>null,\n El=()=>({settings:{model}}),hl=async()=>true,Ol=async()=>null,\n dl=()=>({nextRunAt:2,nextRunNominalAt:2}),nl=async()=>({}),\n bl=async options=>{hosted.push(options.hostedAutomationsEnabled);throw {code}},\n l={Yt:e=>e.code},Zc=()=>({warning:()=>{},debug:()=>{}}),\n a={Kn:()=>skips++,Vn:()=>{},On:()=>current,Jn:e=>{writes.push(e);return e}};\nconst base={statsig:{},automation:{...current,rrule:'fixture'},now:1,\n appServerConnection:{readThread:async()=>({cwd:'/synthetic'}),\n  notifyAutomationRunTriggered:()=>triggers++,notifyAutomationRunsUpdated:()=>notifications++},\n signal:{},assertCurrent:()=>{},heartbeatThreadRendererStates:new Map(),\n heartbeatThreadCollaborationModes:new Map(),heartbeatThreadPermissions:new Map(),\n updateCanonicalAutomation:()=>{},isHostedAutomationAppAvailable:async()=>true};\n(async()=>{\n await vl({...base,deleteArchivedHeartbeat:async id=>{deletes.push(id);return 'deleted'}});\n assert(deletes.length===1&&deletes[0]===current.id&&notifications===1&&!writes.length,'archived heartbeat must delete once');\n assert(hosted.length===1&&hosted[0]===true,'official hosted flag must reach the turn');\n deletes=[];notifications=0;writes=[];\n await vl(base);\n assert(writes.length===1&&writes[0].status==='PAUSED'&&notifications===1&&!deletes.length,'missing canonical delete must pause once');\n const changedStates=[{...current,status:'PAUSED'},{...current,targetThreadId:'other'},{...current,kind:'cron'},null];\n for(const changed of changedStates){\n  current=changed;writes=[];deletes=[];notifications=0;\n  await vl({...base,deleteArchivedHeartbeat:async id=>{deletes.push(id);return 'deleted'}});\n  assert(!writes.length&&!deletes.length&&!notifications,'changed canonical automation must remain untouched');\n }\n current={...base.automation};code='unrelated_failure';\n let preserved=false;try{await vl(base)}catch(e){preserved=e.code===code}\n assert(preserved,'unrelated failure must propagate');\n const before=triggers;model='';await vl(base);\n assert(skips===1&&triggers===before,'missing model must defer without starting a turn');\n process.stdout.write(JSON.stringify({status:'passed',delete_once:true,pause_fallback:true,\n concurrent_state_preserved:true,unrelated_error_preserved:true,hosted_flag_preserved:true,missing_model_deferred:true,triggers}));\n})().catch(e=>{process.stderr.write(String(e.stack||e));process.exitCode=1});\n"
