from pathlib import Path
import json,re,subprocess
from frontend_feature_contracts import _extract_function, _with_module_stubs, ContractError

PICKER_PATH='webview/assets/composer-project-picker-content-21970821f4a5.js'
PICKER_SHA256='cdbabad8aa78f2584815da5ddfed151523c4a0f3ea02ab0a1728e148dbed8452'

def run(initial,primary,picker,node='node'):
    functions={n:_extract_function(primary.decode(),n) for n in ('Q7','a7e','z$','O0e','f9e','j7e','F5e','e7e')}
    functions.update({n:_extract_function(initial.decode(),n) for n in ('xti','qZx','$ka')})
    lazy='\n'.join(_extract_function(picker.decode(),n) for n in ('I','L','R','z'))
    body='\n'.join(functions.values())
    modules=sorted(set(re.findall(r'(?<![\w$.])([\w$]+)\.(?:c|jsx|jsxs|Fragment|useRef|useState)\b',body)))
    prelude=r'''
const assert=(v,m)=>{if(!v)throw Error(m)};
const memo=()=>new Array(300).fill(Symbol.for('react.memo_cache_sentinel'));
const jsx=(type,props,key)=>({type,props:props||{},key});
let search='',cloud=[],localEnabled=true,selected=null,selectedId=null,selectedKind='remote';
const intl={formatMessage:(m,v)=>m.defaultMessage.replace('{projectName}',v?.projectName??'')};
const xt=()=>intl,Z=()=>({isCapable:true,isLoading:false}),ple=()=>`allowed`;
const Dw=Symbol(),Xs=Symbol(),xse=Symbol(),ffe=Symbol(),Gie=Symbol(),yv=Symbol(),ug=Symbol(),hx=Symbol();
const store={get:()=>null,set:()=>{},query:{setData:()=>{}}};
const eE=()=>store;
const $=(atom)=>atom===Dw?{type:selectedKind,projectId:selectedId}:atom===Xs?[local]:atom===xse?[local,...remotes]:atom===ffe?[]:atom===Gie?localEnabled:atom===yv?{projects:cloud}:null;
const Bd=(context,descriptor)=>{assert(context===store,'selection uses the store object');selected={descriptor,route:$ka(descriptor)}};
const xge=(context,value)=>{assert(context===store,'cloud store');selected=value};
const Kn=value=>value,c='asset',OW={Item:'item',Action:'action'},I$='trigger',QPe='dialog',hv=(s,q)=>String(s).toLowerCase().includes(q.toLowerCase())?1:0;
const I5e={default:(a,f)=>a.sort((x,y)=>f(x)-f(y))};
const fb=Symbol(),Sun=Symbol(),Mr={REMOTE_PROJECTS:Symbol()};
const WC=()=>({data:raw,isLoading:false}),yf=atom=>atom===fb?{type:selectedKind,projectId:selectedId}:false;
const ids=['11111111-1111-4111-8111-111111111111','22222222-2222-4222-8222-222222222222','33333333-3333-4333-8333-333333333333','44444444-4444-4444-8444-444444444444'];
const names=['project-alpha','project-beta','project-gamma','project-delta'];
const raw=ids.map((id,i)=>({id,label:id,hostId:'remote-ssh-discovered:ExampleHost',remotePath:'/root/'+names[i]}));
const remotes=ids.map((id,i)=>({projectId:id,projectKind:'remote',hostId:raw[i].hostId,path:raw[i].remotePath,label:names[i],gitRepos:[]}));
const local={projectId:'local-1',projectKind:'local',label:'Local project',path:'C:/example',gitRepos:[]};
const original=JSON.stringify({raw,remotes});
const walk=(e,type)=>{if(!e||typeof e!=='object')return null;if(e.type===type)return e;for(const v of Object.values(e.props??e)){if(Array.isArray(v)){for(const a of v){const r=walk(a,type);if(r)return r}}else{const r=walk(v,type);if(r)return r}}return null};
'''
    prelude+='\n'.join(f'const {name}={{c:memo,jsx,jsxs:jsx,Fragment:"fragment",useRef:v=>({{current:v}}),useState:v=>[typeof v==="string"?search:v,()=>{{}}]}};' for name in modules)
    lazy_context='''
const oBe=(()=>{const B={c:memo},V={jsx,jsxs:jsx,Fragment:'fragment'},u=()=>intl,h=()=>({projects:cloud,isError:false,isLoading:false}),v=Symbol(),P=F5e,k=e7e,j='menu',O=OW,b={Message:'message'},n='intl-message',i='spinner',a='icon',S='project-icon',C='checked',m='detail',D='new-project',g='none',t='asset';
'''+lazy+'\nreturn I;})();\n'
    tests=r'''
const render=props=>{let outer=Q7(props),middle=outer.type===a7e?a7e(outer.props):outer;return {middle,out:z$(middle.props)}};
const results=[];
for(let index=0;index<ids.length;index++){
 selectedId=ids[index];search='';
 const rawSelection=xti();assert(rawSelection.selectedRemoteProject.label===names[index],'raw selected label');
 const fallback=f9e({activeProjectId:selectedId,projects:[],remoteConnections:[],selectedRemoteProject:rawSelection.selectedRemoteProject});
 assert(fallback.label===names[index]&&fallback.hostId===raw[index].hostId&&fallback.path===raw[index].remotePath,'work fallback identity');
 let {middle,out}=render({projectId:selectedId,menuOpen:true});
 assert(out.props.value===names[index]&&out.props['aria-label'].endsWith(names[index]),'visible label and accessible label');
 assert(out.props.tooltipContent==='Change project','tooltip');
 let menu=walk(out,oBe);assert(menu,'actual lazy content route');
 let content=oBe(menu.props),list=walk(content,e7e);assert(list.props.groups.length===5,'all local and remote options');
 search=names[index];({out}=render({projectId:selectedId,menuOpen:true}));content=oBe(walk(out,oBe).props);list=walk(content,e7e);
 assert(list.props.groups.length===1&&list.props.groups[0].projectId===selectedId,'human-name search');
 const item=walk(e7e(list.props),'item');assert(item,'real option rendering');item.props.onSelect();
 assert(selected.route.type==='remote'&&selected.route.projectId===selectedId,'selection routing');
 assert(selected.descriptor.hostId===raw[index].hostId&&selected.descriptor.path===raw[index].remotePath,'host and path preserved');
 results.push({label:out.props.value,aria_label:out.props['aria-label'],route:selected.route});
}
search='';localEnabled=false;selectedId=ids[2];let {middle,out}=render({});
assert(middle.props.localProjectOptions.projects.length===4&&out.props.value===names[2],'inherited remote without local capability');
let dialog=O0e();assert(dialog.props.localProjectOptions.projects.length===5,'dialog remote options');dialog.props.localProjectOptions.onSelectProject(remotes[0]);assert(selected.route.type==='remote','dialog kind preserved');
localEnabled=true;({out}=render({projectId:local.projectId}));assert(out.props.value==='Local project','local label');
let content=oBe(walk(out,oBe).props),list=walk(content,e7e);list.props.onSelectProject(local);assert(selected.route.type==='local','local routing');
cloud=[{gizmo:{id:'g-p-example',display:{name:'Cloud project'}}}];({out}=render({projectId:'g-p-example'}));assert(out.props.value==='Cloud project','cloud label');
out.props.onClearProject();assert(selected===null,'clear selection');
const explicit=Q7({projectId:'g-p-example',onProjectChange:()=>{}});assert(explicit.type===z$&&explicit.props.projectId==='g-p-example','explicit cloud branch preserved');
remotes[2]={...remotes[2],label:'Renamed SSH'};({out}=render({projectId:ids[2]}));assert(out.props.value==='Renamed SSH','rename rerender');remotes[2]={...remotes[2],label:names[2]};
selectedKind='local';assert(xti().selectedRemoteProject===null,'local selection does not acquire remote');
assert(JSON.stringify({raw,remotes})===original,'source descriptors unchanged');
process.stdout.write(JSON.stringify({status:'passed',results,visible_uuid_count:0,raw_hook:true,actual_wrapper:true,lazy_content:true,search:true,selection:true,local_and_cloud_preserved:true,source_descriptors_unchanged:true}));
'''
    script=prelude+'\n'+body+'\n'+lazy_context+tests
    cp=subprocess.run([node,'-'],input=_with_module_stubs(script,{**functions,'lazy':lazy}),text=True,capture_output=True,timeout=30)
    if cp.returncode:raise ContractError('26.915 Work picker: '+cp.stderr[-3000:])
    return json.loads(cp.stdout)
