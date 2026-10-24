// Only state and hook boundaries are synthetic. Functions under test are read
// from their actual initial/primary module, including the real parent consumer.
const assert=(value,label)=>{if(!value)throw Error(label)};
const memo=()=>new Array(360).fill(Symbol.for('react.memo_cache_sentinel'));
const parentMemo=memo(),rowMemo=memo(),wrapperMemo=memo(),genericMemo=memo();
const HX={c:()=>parentMemo},zJn={c:()=>rowMemo},MJn={c:()=>wrapperMemo},pX={c:()=>genericMemo};
const jsx=(type,props)=>({type,props:props||{}}),UX={jsx,jsxs:jsx},xX=UX,yX=UX,hX=UX,K8=UX;
const BZn={useContext:()=>({previewNavigationState:null}),useState:v=>[v,()=>{}],useRef:()=>({current:null})};
const mX={useId:()=>"fixture-row",useState:v=>[v,()=>{}]};
const store={get:()=>null},Jd=()=>store;
const X=atom=>atom===Che?{data:null}:false,Mp=()=>false;
const Eu=()=>({formatMessage:m=>m.defaultMessage}),NJn=()=>({archived:false,usesExternalArchiveHandling:false});
const D3e=()=>false,INe=()=>false,bce=()=>null,RJn=({title,titleOverride})=>titleOverride??title;
const FKn=()=>"local",rb=()=>({}),r6e=()=>true,ac=(...x)=>x.filter(Boolean).join(' ');
const gxt=x=>x,Tf=()=>null,Qw=e=>e.turns,Jo=String;
let unread=false,loading=false,asyncPending=false,scalar=null,raw;
let fAi,pAi;
let h2e;
const sAi=Symbol('synthetic asynchronous request store');
const N1n=Symbol('canonical request state'),qZRequestState=N1n;
const t=f=>f,n=()=>({default:()=>false}),H=(_,fn)=>fn;
const qZInitRequestState=()=>{};
const saved=new Map(),window={localStorage:{getItem:k=>saved.get(k)??null,setItem:(k,v)=>saved.set(k,v),removeItem:k=>saved.delete(k)}};
const select=(atom)=>atom===N1n?raw:atom===sAi?(asyncPending?'synthetic-question':null):null;
const Z=(atom,key)=>atom==null?null:atom===zb?{summary:{hasUnreadTurn:unread,threadSource:null},unreadMessageCount:0}:
 atom===eRe?{roomId:null,hasUnread:unread}:atom===N1n?raw:atom===h2e?pAi(key,{get:select}):
 atom===QKe?(loading?'loading':'idle'):atom===efe?'Synthetic':atom===om||atom===jX?{data:null}:
 atom===U$e?'local':atom===xKn?false:atom===null?null:null;
mAi();
const b_=$ts;
h2e=pAi;
const actual=new Set([LJn,vX,cJn,$ts,qZDot]);
const walk=(node,pred)=>{
 if(!node||typeof node!=='object')return null;
 if(Array.isArray(node))return node.map(n=>walk(n,pred)).find(Boolean)||null;
 if(pred(node))return node;
 if(actual.has(node.type))return walk(node.type(node.props),pred);
 for(const key of ['children','trailingIconNodes','leadingIconNodes']){const r=walk(node.props?.[key],pred);if(r)return r}
 return null;
};
function state(requests=[],turns=[{turnId:'fixture-turn',status:'completed',items:[]}],resumeState='resumed',threadRuntimeStatus={type:'idle'}){
 const conversation={requests,turns};raw={...conversation,pendingRequest:J9t(conversation,()=>null),resumeState,threadRuntimeStatus};return raw;
}
const states=[];
function run(label,pinned=false,active=false){
 const parent=RZn({conversationId:'synthetic',hostId:'local',isPinned:pinned,isActive:active,canPin:false,disableHoverCard:true,statusIndicatorReplacesMeta:true,metaContent:'meta'});
 const row=walk(parent,n=>n.type===LJn);assert(row,'parent reaches packaged row');
 assert(row.props.isPinned===pinned,'real parent pin prop lost');
 const child=LJn(row.props),status=child?.props?.statusState;assert(status,'row constructs status');
 const dot=walk(child,n=>n.type==='i'&&n.props.style);const color=dot?.props.style.background??null;
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
state([],[],'needs_resume',{type:'active',activeFlags:['waitingOnUserInput']});
assert(run('cold-question',true).color==='#f97316','cold waiting question');
state();loading=false;assert(run('pinned-unread',true).color==='var(--color-text-danger)','pinned unread red');
assert(run('selected-unpinned',false,true).color==='var(--color-text-info)','selection is not pin');
unread=false;scalar='implementPlan';assert(run('scalar-rejected').color===null,'display scalar is not pending plan');
assert(Z4894Plan('set','synthetic','fixture-turn','Synthetic plan'),'cold plan persisted');
assert(run('cold-plan').color==='#eab308','persisted plan restored');
Z4894Plan('remove','synthetic','fixture-turn');assert(run('cleared').color===null,'clear removes indicator');
process.stdout.write(JSON.stringify({status:'passed',actual_parent:true,actual_row:true,actual_pending_selector:true,retained_memo:true,async_event_fallback:true,states}));
