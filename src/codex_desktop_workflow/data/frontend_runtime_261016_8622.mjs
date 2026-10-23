// Version-scoped, synthetic runtime regression. All application functions come
// from the packaged entry; no user catalog, thread, settings or network writes.
import * as initial from "app://-/assets/app-initial-ad16eaadf81f.js";
import * as shared from "app://-/assets/app-shared-2feb3d4c6fcc.js";

const A="2.11.0-a05dfd86ca50", M="[CF9]", R=crypto.randomUUID();
const names=[
  "priority_filter_recency_sorting","priority_filter_live_resort",
  "priority_filter_pinned_recency_sorting","priority_filter_hold_membership",
  "priority_click_hold","priority_identity_migration","priority_project_context_subtitle",
  "plan_pending_detection","plan_pending_yellow_indicator","plan_pending_unread_indicator",
  "attention_highlight_color_semantics","project_sorting","active_priority_sort",
  "automation_priority_gate","pinned_priority_sync","new_chat_file_drop",
  "resume_history_on_demand","paginated_tail_retention","idle_history_eviction",
  "remote_project_label","work_remote_project_picker","user_action_pending_orange",
  "portable_update_awareness"
];
const keys=["layout","map","merge","remoteName","pinned","persistPinned","subtitle",
  "updated","click","resumeComplete","scheduleGate","membership","normalize",
  "makeConversation","pendingAttention","pendingKind","Idle","scheduleAtom",
  "catalogAtom","recencyAtom","holdAtom","recency","pinSort","initIndicator",
  "initSort","initPrefs","initCatalog","initIdle","assignment","updateState",
  "updateComponent","initUpdate","bridge"];
const ok=(v,m)=>{if(!v)throw Error(m)};
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));

function publishTerminal(emit,status,extra) {
  if(!["passed","failed"].includes(status))throw Error("invalid terminal proof");
  // The native window can hide between module load and completion. Preserve
  // the actual result and republish it when that same renderer is visible.
  // The receiver still requires a visible primary window and the same run ID.
  const result=JSON.parse(JSON.stringify(extra));
  let disposed=false,timers=[];
  const clear=()=>{for(const id of timers)clearTimeout(id);timers=[]};
  const send=()=>{
    if(disposed||document.visibilityState!=="visible"||!document.querySelector("#root")?.children.length)return;
    emit("module_loaded");emit(status,result);
  };
  const refresh=()=>{
    if(disposed)return;clear();
    if(document.visibilityState!=="visible")return;
    send();for(const ms of [250,1000,3000])timers.push(setTimeout(send,ms));
  };
  const dispose=()=>{
    disposed=true;clear();document.removeEventListener("visibilitychange",refresh);
    window.removeEventListener("focus",refresh);window.removeEventListener("pagehide",dispose);
  };
  document.addEventListener("visibilitychange",refresh);window.addEventListener("focus",refresh);
  window.addEventListener("pagehide",dispose);refresh();
}

export async function r(bindings) {
  // Module evaluation occurs once per renderer. A fresh UUID is never reused
  // across windows or starts. Auxiliary windows cannot qualify the main UI.
  const emit=(status,extra={})=>bindings()[32].dispatchMessage("log-message",{
    level:status==="failed"?"error":"info",
    message:M+JSON.stringify({schema_version:7,validator_version:"2.11.0",
      artifact_id:A,run_id:R,status,content_logged:false,
      transport:"renderer_log_message_v1",...extra})
  });
  const features=Object.fromEntries(names.map(id=>[id,{passed:false,evidence:"unexecuted"}]));
  let stage="initialization";
  try {
    // Do not mount a second catalog or start backend RPC during bootstrap.
    for(let i=0;i<100&&!document.querySelector("#root")?.children.length;i++)await delay(100);
    ok(document.querySelector("#root")?.children.length,"primary route not mounted");
    let n=Object.fromEntries(keys.map((key,i)=>[key,bindings()[i]]));
    for(const key of ["initIndicator","initSort","initPrefs","initCatalog","initIdle","initUpdate"])
      n[key]();
    n=Object.fromEntries(keys.map((key,i)=>[key,bindings()[i]]));
    ok(keys.every(key=>n[key]!=null),"incomplete native bindings");
    emit("module_loaded");
    const pass=(ids,evidence)=>ids.forEach(id=>{features[id]={passed:true,evidence}});
    const sort=initial.Lun;
    stage="priority";
    const list=[{key:"older",recencyAt:2,attentionState:"waiting"},
      {key:"newer",recencyAt:9,attentionState:"unread"},
      {key:"tie",recencyAt:9,attentionState:"idle"}];
    ok(sort(list).map(x=>x.key).join()==="newer,tie,older","recency precedes attention");
    ok(list[0].key==="older","sort mutated input");
    list[0].recencyAt=12;
    ok(sort(list)[0].key==="older","live recency change ignored");
    ok(n.updated({recencyAt:5,updatedAt:90,createdAt:1},"updated_at")===5,
      "official recency producer survives storage-only resume updates");
    ok(n.updated({updatedAt:90,createdAt:1},"updated_at")===90,"cold fallback");
    ok(n.updated({recencyAt:5,updatedAt:9000,createdAt:1},"updated_at")===5,"reading must not promote a chat after cold restore");
    pass(["priority_filter_recency_sorting","priority_filter_live_resort"],
      "packaged_stable_recency_sort_and_cold_live_time_selector");
    let time=7,held=7,scheduled=false;
    const get=(atom,key)=>atom===n.catalogAtom?{byKey:new Map()}:
      atom===n.recencyAtom?time:atom===n.holdAtom?new Map([["held",held]]):
      atom===n.scheduleAtom?scheduled:null;
    const item={kind:"task",threadEntry:{kind:"local",conversationId:null,key:"held"},
      attentionState:"idle",isScheduled:false};
    ok(n.membership(get,item,"codex")===true,"read click hold missing");
    time=8;ok(n.membership(get,item,"codex")===false,"stale hold accepted");
    time=null;held=null;ok(n.membership(get,item,"codex")===false,"missing time accepted");
    time=held=7;
    scheduled=true;
    ok(n.scheduleGate(get,{...item,isScheduled:true},"codex")===false,"idle scheduled visible");
    ok(n.scheduleGate(get,{...item,isScheduled:true,attentionState:"active"},"codex")===true,
      "active scheduled hidden");
    pass(["priority_filter_hold_membership","automation_priority_gate"],
      "packaged_membership_hold_time_and_scheduled_attention_negatives");
    let read=0,unread=0;
    const ref={kind:"local",conversationId:"synthetic",hostId:"local"};
    const actions={markThreadAsRead:v=>{ok(v.conversationId==="synthetic","read identity");read++},
      markThreadAsUnread:v=>{ok(v.hostId==="local","unread host");unread++}};
    ok(n.click({get:()=>ref},"mark-thread-read","key",actions)&&read===1,"read route");
    ok(n.click({get:()=>ref},"mark-thread-unread","key",actions)&&unread===1,"unread route");
    ok(!n.click({get:()=>null},"mark-thread-read","key",actions),"missing reference accepted");
    pass(["priority_click_hold"],"packaged_read_unread_dispatch_identity_and_missing_reference");
    const refs=new Map([["local:a",{threadId:"a"}],["local:b",{threadId:"b"}],
      ["pending",{threadId:null,pendingThreadId:"pending",pinnedBeforeThreadId:"b"}]]);
    const order=n.pinned({threadKeys:["local:a","pending","local:b"],
      pinnedThreadIds:["b","a","stale"],referencesByThreadKey:refs});
    ok(order.join()==="pending,local:b,local:a","legacy pinned migration");
    ok(n.persistPinned(order,refs).join()==="b,a","pending identity persisted");
    pass(["priority_identity_migration","pinned_priority_sync"],
      "packaged_pending_materialized_pinned_identity_roundtrip");
    stage="layout";
    const entries=[{key:"p1",kind:"project",pinned:false,source:"codex"},
      {key:"p2",kind:"project",pinned:false,source:"codex"},
      {key:"c1",kind:"conversation",pinned:false,projectKey:"p1",attentionState:"unread",recencyAt:10,source:"codex"},
      {key:"c2",kind:"conversation",pinned:false,projectKey:"p2",attentionState:"idle",recencyAt:20,source:"codex"}];
    const opts={chatSortMode:"updated_at",mode:"project",pinnedOrder:[],
      pinnedSortMode:"manual",projectOrder:["p1","p2"],source:"codex"};
    ok(n.layout(entries,{...opts,projectSortMode:"updated_at"}).projectKeys.join()==="p2,p1",
      "project recency");
    ok(n.layout(entries,{...opts,projectSortMode:"priority"}).projectKeys.join()==="p2,p1",
      "priority project time order");
    ok(n.layout(entries,{...opts,projectSortMode:"manual"}).projectKeys.join()==="p1,p2",
      "project manual");
    const pinned=entries.map(e=>e.kind==="project"?{...e,pinned:true}:e);
    ok(n.layout(pinned,{...opts,projectSortMode:"updated_at",pinnedSortMode:"updated_at"})
      .pinnedKeys.slice(0,2).join()==="p2,p1","pinned project recency");
    const normalized=n.normalize({initialized:true,chatSortMode:"priority",
      projectSortMode:"priority"},null,false);
    ok(normalized.chatSortMode==="priority"&&normalized.projectSortMode==="priority",
      "priority preference rejected");
    ok(n.normalize({initialized:true,chatSortMode:"manual",manualSortVersion:0},null,false)
      .chatSortMode==="updated_at","legacy preference migration");
    pass(["project_sorting","active_priority_sort","priority_filter_pinned_recency_sorting"],
      "packaged_normal_pinned_layout_and_preference_migration");
    stage="remote";
    const uuid="11111111-1111-4111-8111-111111111111";
    const raw={id:uuid,hostId:"synthetic-host",label:uuid,remotePath:"/srv/project-alpha"};
    const saved=n.map([raw],[{hostId:raw.hostId,displayName:"Synthetic host"}],{});
    ok(saved[0].label==="project-alpha","saved remote label");
    const live={...saved[0],label:uuid,threadKeys:["synthetic-thread"]};
    const merged=n.merge(saved,[live],new Map())[0];
    const moved=n.merge(saved,[{...live,projectId:"changed",path:raw.remotePath+"/"}],new Map())[0];
    ok(merged.label==="project-alpha"&&moved.label==="project-alpha","late label merge");
    ok(moved.projectId===uuid&&moved.threadKeys[0]==="synthetic-thread","late route identity");
    ok(n.subtitle({chatLabel:"Chat",task:{kind:"remote",task:{}},
      projectLabel:merged.label,projectlessThreadIds:new Set()}).label==="project-alpha",
      "priority project context");
    const selected={...raw,label:n.remoteName(raw)};
    const assignment=n.assignment({isExistingThread:false,executionHostId:raw.hostId,
      activeLocalProjectId:null,existingAssignment:null,homeRemoteProject:null,
      selectedRemoteProject:selected});
    ok(assignment.projectId===uuid&&assignment.projectKind==="remote",
      "Work selected project routing");
    ok(n.assignment({isExistingThread:false,executionHostId:"other",
      activeLocalProjectId:null,existingAssignment:null,homeRemoteProject:null,
      selectedRemoteProject:selected})==null,"cross-host selection accepted");
    pass(["remote_project_label","priority_project_context_subtitle","work_remote_project_picker"],
      "packaged_saved_live_raw_remote_label_and_Work_assignment_identity");
    stage="attention";
    const base={mcpServerElicitationKind:null,pendingRequestType:null,requests:[],
      resumeState:"resumed",threadRuntimeStatus:{type:"idle"},userInputRequestId:null};
    ok(n.pendingAttention({...base,pendingRequestType:"userInput",userInputRequestId:"q"})
      ?.blocking===true,"native question parser");
    ok(n.pendingAttention({...base,pendingRequestType:"userInput",resumeState:"needs_resume",
      threadRuntimeStatus:{type:"active",activeFlags:[]}})==null,"answered cold question");
    const plan={id:"synthetic-plan",requests:[],turns:[{turnId:"plan",status:"completed",
      items:[{type:"planImplementation",isCompleted:false}]}]};
    ok(n.pendingKind(plan,()=>null)==="implementPlan","native pending plan parser");
    const host=document.createElement("div");
    host.dataset.hotfixRuntimeProbe="4894";
    Object.assign(host.style,{position:"fixed",left:"-10000px",top:"0"});
    document.body.append(host);
    const React=shared.FBt(), jsx=React.createElement;
    const root=shared.PNt().createRoot(host);
    const palette={};
    try {
      for(const [key,state,expected] of [
        ["yellow",{type:"idle",p:true,unread:true,i:true},"rgb(234, 179, 8)"],
        ["orange",{type:"loading",p:true,u:true},"rgb(249, 115, 22)"],
        ["red",{type:"idle",i:true,unread:true},null],
        ["blue",{type:"idle",unread:true},null]]) {
        root.render(jsx(initial.GZ,{statusState:state,size:"compact"}));
        await delay(50);
        const dot=host.querySelector("i");
        ok(dot,"native indicator mount "+key);
        palette[key]=getComputedStyle(dot).backgroundColor;
        ok(expected?palette[key]===expected:palette[key]!=="rgba(0, 0, 0, 0)","native color "+key);
      }
      ok(new Set(Object.values(palette)).size===4,"attention colors collapsed");
      root.render(jsx(initial.GZ,{statusState:{type:"idle"},size:"compact"}));
      await delay(50);ok(!host.querySelector("i"),"resolved indicator remained");
      pass(["plan_pending_detection","plan_pending_yellow_indicator","plan_pending_unread_indicator",
        "attention_highlight_color_semantics","user_action_pending_orange"],
        "packaged_pending_parsers_and_mounted_indicator_precedence_and_clear");
      stage="update";
      const status={schema_version:2,checked_at:new Date().toISOString(),
        published_version:"26.1017.3000.0",package:{identity:"OpenAI.Codex",architecture:"x64",
        status:"manifest_verified",version:"26.1017.2000.0"}};
      ok(n.updateState(status,"26.1016.8622.0")?.stage==="package_available","available package");
      ok(n.updateState({...status,package:null},"26.1016.8622.0")?.stage==="published",
        "announcement confused with installed build");
      ok(n.updateState({...status,checked_at:"invalid"},"26.1016.8622.0")==null,"invalid freshness");
      const actual=await shared.ist.appUpdates.checkForUpdateInformation();
      const expected=n.updateState(actual?.portableUpdateAwareness,"26.1016.8622.0");
      root.render(jsx(n.updateComponent,{variant:"sidebarFooter"}));
      await delay(800);
      const button=host.querySelector("button[data-codex-update-stage]");
      ok(expected?button?.dataset.codexUpdateStage===expected.stage:!button,"mounted update state");
      pass(["portable_update_awareness"],"packaged_update_classifier_and_real_bridge_mounted_component");
    } finally {root.unmount();host.remove()}
    stage="drop";
    const file=new File(["synthetic"],"fixture.txt",{type:"text/plain"});
    const transfer={items:[{kind:"file",getAsFile:()=>file,webkitGetAsEntry:()=>({isDirectory:false})}],
      files:[file],types:["Files"]};
    ok(initial.T3t(transfer)&&initial.E3t(transfer).files[0]===file,"native file drop");
    ok(!initial.T3t({items:[],files:[],types:[]}),"nonfile drop accepted");
    pass(["new_chat_file_drop"],"packaged_file_transfer_detection_and_classification");
    stage="history";
    ok(n.resumeComplete({resumeState:"resumed",turnsPagination:{hasLoadedOldest:true}}),
      "complete history");
    ok(!n.resumeComplete({resumeState:"resumed",turnsPagination:{hasLoadedOldest:false}}),
      "truncated history accepted");
    ok(!n.resumeComplete({resumeState:"needs_resume",turns:[]}),"unloaded history accepted");
    const conversation=n.makeConversation({thread:{id:"fixture",createdAt:1,updatedAt:2,
      recencyAt:3,model:"fixture-model",reasoningEffort:"high",parentThreadId:"parent",
      source:"cli",status:{type:"idle"},path:"/synthetic/fixture"},
      hostId:"local",conversationId:"fixture",turns:[],threadTitle:"Synthetic",
      resumeState:"needs_resume",latestCollaborationMode:{mode:"default",settings:{}}});
    ok(conversation.latestModel==="fixture-model"&&conversation.latestReasoningEffort==="high"&&
      conversation.parentThreadId==="parent"&&conversation.recencyAt===3000,"history metadata");
    let pages=0;
    const tasks=await initial.oEr({recentConversationsSortKey:"updated_at",sendRequest:async(method,args)=>{
      ok(method==="thread/list","unexpected history request");
      ok(args.cursor===(pages===0?null:"page-2"),"history cursor");
      pages++;return{data:[{id:"synthetic-"+pages}],nextCursor:pages===1?"page-2":null};
    }},{modelProviders:null,sourceKinds:[]});
    ok(pages===2&&tasks.length===2,"history tail lost");
    pass(["resume_history_on_demand","paginated_tail_retention"],
      "packaged_resume_state_constructor_and_actual_recursive_pagination");
    const rows=new Map(),roles=new Map(),active=new Set(["current"]),calls=[];
    const callbacks={};
    const events=Object.fromEntries(["addConversationStateCallback","addStreamRoleStateCallback",
      "addStreamFollowersChangedCallback","addNotificationCallback"].map(k=>[k,fn=>{callbacks[k]=fn;return()=>{}}]));
    const cache=new n.Idle({events,now:()=>20000000,logger:{debug(){},info(){},warning(){}},
      schedule:()=>()=>{},scheduleMicrotask:()=>{},parseUrl:()=>null,
      threadStore:{getConversation:id=>rows.get(id),isConversationActive:id=>active.has(id),
        updateConversationState:(id,fn)=>fn(rows.get(id)),removeConversationInterests(){}},
      streamState:{getStreamRole:id=>roles.get(id),ownsConversationHistoryStream:id=>roles.get(id)?.role==="owner",
        hasFollowersOrPendingFollowerReconnect:()=>false,removeConversation:id=>roles.delete(id)},
      requestClient:{sendRequest:async(method,args)=>{ok(method==="thread/unsubscribe","unexpected idle request");
        calls.push(args.threadId);return{status:"unsubscribed"}}},beforePassiveRelease:()=>{}});
    try {
      stage="first_send_lifecycle";
      for(const canonical of [false,true]) {
        const id="draft-"+canonical, draft={...conversation,id,qZN:id,requests:[],
          turns:[],rolloutPath:"",resumeState:"resumed",threadRuntimeStatus:{type:"idle"}};
        if(canonical) draft.turnHistory={kind:"canonical",history:{generation:0,isComplete:true,
          entitiesByKey:{},islands:[{entries:[],newerBoundary:{status:"exhausted"}}]}};
        rows.set(id,draft);roles.set(id,{role:"owner"});
        callbacks.addConversationStateCallback(id,draft);
        ok(draft.qZN===id&&cache.shouldKeepConversationLoaded(draft),"unsent draft lost protection");
        const optimistic={turnId:null,status:"inProgress",items:[]};
        if(canonical){draft.turnHistory.history.entitiesByKey.t=optimistic;
          draft.turnHistory.history.islands[0].entries=[{value:"t"}]}else draft.turns=[optimistic];
        callbacks.addConversationStateCallback(id,draft);
        ok(draft.qZN===id,"optimistic send prematurely materialized");
        optimistic.turnId="accepted-"+id;
        callbacks.addConversationStateCallback(id,draft);
        ok(!Object.hasOwn(draft,"qZN"),"accepted turn did not release draft guard");
        optimistic.status="completed";draft.rolloutPath="/synthetic/"+id;
        callbacks.addConversationStateCallback(id,draft);
        ok(draft.latestModel==="fixture-model"&&draft.latestReasoningEffort==="high",
          "first send changed task settings");
        rows.delete(id);roles.delete(id);cache.removeConversation(id);
      }
      stage="history";
      for(const id of ["current","running","pending","idle"]) {
        rows.set(id,{...conversation,id,resumeState:"resumed",rolloutPath:"/synthetic/"+id,
          requests:[],turns:id==="pending"?plan.turns:[{turnId:id,status:"completed",items:[]}],
          threadRuntimeStatus:{type:id==="running"?"active":"idle"},turnsPagination:{hasLoadedOldest:true}});
        roles.set(id,{role:"owner"});cache.inactiveOwnerConversationSinceById.set(id,0);
      }
      const candidates=cache.getInactiveOwnerConversationIdsToUnsubscribe(20000000);
      ok(candidates.join()==="idle","idle selection or active/pending protection");
      await cache.unsubscribeInactiveConversation("idle");
      ok(rows.get("idle").resumeState==="needs_resume"&&rows.get("idle").turns.length===0&&
        rows.get("idle").latestModel==="fixture-model"&&calls.join()==="idle","idle metadata preservation");
      pass(["idle_history_eviction"],"packaged_first_send_subscription_canonical_legacy_and_inactive_history");
    } finally {cache.dispose()}
    ok(names.every(id=>features[id].passed),"incomplete feature suite");
    publishTerminal(emit,"passed",{features,palette,scope:"packaged_synthetic_runtime_regression",
      native_function_bindings:true,actual_renderer:true,main_route_mounted:true,
      user_catalog_read:false,user_data_modified:false,external_requests_sent:false});
  } catch(error) {
    publishTerminal(emit,"failed",{failure_code:stage+":"+String(error?.message??error).slice(0,220),features});
  }
}

export function u(e,t){
 if(e?.schema_version!==2||typeof e.checked_at!==`string`)return null;
 const key=v=>typeof v===`string`&&/^\d{1,5}(?:\.\d{1,5}){3}$/.test(v)&&v.split(`.`).every(n=>Number(n)<=65535)?v.split(`.`).map(Number):null;
 const cmp=(a,b)=>{let x=key(a),y=key(b);if(!x||!y)return 0;for(let i=0;i<4;i++)if(x[i]!==y[i])return x[i]-y[i];return 0};
 if(!key(t))return null;
 const age=Date.now()-Date.parse(e.checked_at);
 if(!Number.isFinite(age)||age< -300000||age>86400000)return null;
 const fresh=age<=7200000;
 const announced=key(e.published_version)?e.published_version:null;
 const downloaded=e.package?.identity===`OpenAI.Codex`&&e.package?.architecture===`x64`&&e.package?.status===`manifest_verified`&&key(e.package.version)?e.package.version:null;
 const prepared=e.prepared?.status===`adaptation_prepared`&&e.prepared?.qualified===true&&/^[a-f0-9]{64}$/.test(e.prepared?.source_asar_sha256??``)&&/^[a-f0-9]{64}$/.test(e.prepared?.qualification_sha256??``)&&key(e.prepared?.version)?e.prepared.version:null;
 const zh=typeof document!==`undefined`&&/^zh(?:-|$)/i.test(document.documentElement?.lang||`en`);
 let stage,version,label;
 if(prepared&&cmp(prepared,t)>0){stage=`adaptation_ready`;version=prepared;label=(zh?`适配已就绪 · ${version}`:`Adaptation ready · ${version}`)}
 else if(downloaded&&fresh&&cmp(downloaded,t)>0){stage=`package_available`;version=downloaded;label=(zh?`新版原包可获取 · ${version}`:`Official package available · ${version}`)}
 else if(announced&&cmp(announced,t)>0){stage=`published`;version=announced;label=(zh?`官方已公布新版 · ${version}`:`Official update announced · ${version}`)}
 else return null;
 let detail=stage===`adaptation_ready`?(zh?`适配已通过验收；当前会话退出后，安全启动器会再次检查。`:`The adaptation has passed validation. The launcher will check it after this session exits.`):stage===`package_available`?(zh?`完整包内版本已核对；完成适配验收后才能启用。`:`The complete package version is verified. Adaptation and validation are still required.`):(zh?`已公布版本暂未确认为可启用适配版。`:`The announced version does not yet have a verified adaptation.`);
 if(announced&&cmp(announced,version)>0)detail+=(zh?` 官方另已公布 ${announced}，其状态尚未达到本项阶段。`:` A newer version, ${announced}, has also been announced.`);
 if(downloaded&&announced&&cmp(announced,downloaded)>0)detail+=(zh?` 下载入口当前包内版本为 ${downloaded}。`:` The download currently contains version ${downloaded}.`);
 if(!fresh)detail+=(zh?` 在线信息已超过两小时，需重新检查。`:` Online information is over two hours old and needs a refresh.`);
 return{stage,version,label,detail};
}
