// Synthetic store and hook boundary; every row, pending selector and indicator
// under test is extracted unchanged from the source-bound packaged application.
const assert=(value,label)=>{if(!value)throw Error(label)};
const memo=()=>new Array(320).fill(Symbol.for('react.memo_cache_sentinel'));
const parentMemo=memo(),rowMemo=memo(),wrapperMemo=memo(),genericMemo=memo();
const Sqc={c:()=>parentMemo},gHc={c:()=>rowMemo},sHc={c:()=>wrapperMemo},YVc={c:()=>genericMemo};
const jsx=(type,props)=>({type,props:props||{}}),d4={jsx,jsxs:jsx},n4=d4,cHc=d4,t4=d4,$2=d4;
const Cqc={useContext:()=>({previewNavigationState:null}),useState:v=>[v,()=>{}],useRef:()=>({current:null})};
const XVc={useId:()=>"fixture-row",useState:v=>[v,()=>{}]};
const store={get:()=>null},E=()=>store;
const Z=atom=>atom===kwn?{data:null}:false,Qv=()=>false;
const Wc=()=>({formatMessage:m=>m.defaultMessage}),uHc=()=>({archived:false,usesExternalArchiveHandling:false});
const OIn=()=>null,VRc=()=>null,RSo=()=>false,S3o=()=>false,ax=()=>null,hHc=({title,titleOverride})=>titleOverride??title;
const ZRc=()=>"local",WO=()=>null,dbo=()=>({}),Xyo=()=>true,ki=(...x)=>x.filter(Boolean).join(' ');
const rKi=x=>x,Ec=()=>null;
const Xb=e=>e.turns,ps=String;
let unread=false,loading=false,asyncPending=false,scalar=null,raw;
let JJi,YJi;
const UJi=Symbol('synthetic asynchronous request store');
const t=f=>f,n=()=>({default:()=>false}),Yl=(_,fn)=>fn;
const saved=new Map(),window={localStorage:{getItem:k=>saved.get(k)??null,setItem:(k,v)=>saved.set(k,v),removeItem:k=>saved.delete(k)}};
const select=(atom)=>atom===Pcr?raw:atom===UJi?asyncPending:null;
const Nc=(atom,key)=>atom===ak?{summary:{hasUnreadTurn:unread,threadSource:null},unreadMessageCount:0}:
 atom===DJi?{roomId:null,hasUnread:unread}:atom===Pcr?raw:atom===YJi?YJi(key,{get:select}):
 atom===AJi?(loading?'loading':'idle'):atom===Bkc?'Synthetic':atom===KE?{data:null}:
 atom===Q5i?'local':atom===gRc?false:atom===null?null:atom===scalar?null:null;
XJi();
const actual=new Set([mHc,oHc,MVc,Q2,qZDot]);
const walk=(node,pred)=>{
 if(!node||typeof node!=='object')return null;
 if(Array.isArray(node))return node.map(n=>walk(n,pred)).find(Boolean)||null;
 if(pred(node))return node;
 if(actual.has(node.type))return walk(node.type(node.props),pred);
 for(const key of ['children','trailingIconNodes','leadingIconNodes']){
  const result=walk(node.props?.[key],pred);if(result)return result;
 }
 return null;
};
function state(requests=[],turns=[{turnId:'fixture-turn',status:'completed',items:[]}],resumeState='resumed',threadRuntimeStatus={type:'idle'}){
 const conversation={requests,turns};raw={...conversation,pendingRequest:a7t(conversation,()=>null),resumeState,threadRuntimeStatus};
 return raw;
}
const states=[];
function run(label,pinned=false,active=false){
 const parent=bqc({conversationId:'synthetic',hostId:'local',isPinned:pinned,isActive:active,canPin:false,disableHoverCard:true,statusIndicatorReplacesMeta:true,metaContent:'meta'});
 const row=walk(parent,n=>n.type===mHc);assert(row,'parent reaches packaged row');
 assert(row.props.qZPinned===pinned,'real parent pin prop lost');
 const child=mHc(row.props),status=child?.props?.statusState;assert(status,'row constructs status');
 const dot=walk(child,n=>n.type==='i'&&n.props.style);
 const color=dot?.props.style.background??null;
 states.push({label,state:status,color});return {status,color};
}
state();assert(run('idle').color===null,'idle indicator');
const plan=()=>[{turnId:'fixture-turn',status:'completed',items:[{type:'planImplementation',isCompleted:false}]}];
state([],plan());assert(raw.pendingRequest?.kind==='implementPlan','native plan producer');
assert(run('read-plan').color==='#eab308','read plan yellow through full row');
unread=true;assert(run('pinned-plan',true).color==='#eab308','plan before pinned unread');
loading=true;assert(run('loading-plan',true).color==='#eab308','plan before loading');
state([{id:'question',method:'item/tool/requestUserInput',params:{turnId:'fixture-turn'}}],plan());
assert(raw.pendingRequest?.kind==='userInput','native question producer');
assert(run('question-before-plan',true).color==='#f97316','question orange before plan and spinner');
state([],plan());asyncPending=true;
assert(run('async-question',true).color==='#f97316','ongoing async question reaches real selector');
asyncPending=false;assert(run('async-resolved',true).color==='#eab308','async answer reveals remaining plan');
state([{id:'approval',method:'item/commandExecution/requestApproval',params:{turnId:'fixture-turn'}}],plan());
assert(run('approval',true).color==='#f97316','approval orange');
state([],[], 'needs_resume',{type:'active',activeFlags:['waitingOnUserInput']});
assert(run('cold-question',true).color==='#f97316','cold waiting question');
state();loading=false;assert(run('pinned-unread',true).color==='var(--color-text-danger)','pinned unread red');
assert(run('selected-unpinned',false,true).color==='var(--color-text-info)','selection is not pin');
unread=false;scalar='implementPlan';assert(run('scalar-rejected').color===null,'display scalar is not pending plan');
assert(Z4894Plan('set','synthetic','fixture-turn','Synthetic plan'),'cold plan persisted');
assert(run('cold-plan').color==='#eab308','persisted plan restored');
Z4894Plan('remove','synthetic','fixture-turn');assert(run('cleared').color===null,'clear removes indicator');
process.stdout.write(JSON.stringify({status:'passed',actual_parent:true,actual_row:true,actual_pending_selector:true,retained_memo:true,async_event_fallback:true,states}));
