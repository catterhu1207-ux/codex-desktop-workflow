(async function(spec){
 const shared=await import('app://-/assets/app-shared-30671c57ec82.js');
 const React=shared.PCn(),jsx=React.createElement,ok=(v,m)=>{if(!v)throw Error(m)},wait=ms=>globalThis.__qualifiedAwakeDelay(ms);
 let selected=null,depth=-1;
 for(const element of document.querySelectorAll('*')){const key=Object.keys(element).find(k=>k.startsWith('__reactFiber$'));if(!key)continue;let d=0;for(let f=element[key];f;f=f.return)d++;if(d>depth){selected=element[key];depth=d}}
 ok(selected,'Actual primary scope unavailable');
 const contexts=new Map();for(let f=selected;f;f=f.return){const type=f.type,c=type?._context??(type?.$$typeof===Symbol.for('react.context')?type:null);if(c&&f.memoizedProps&&'value'in f.memoizedProps&&!contexts.has(c))contexts.set(c,f.memoizedProps.value)}
 const host=document.createElement('div');host.dataset.qualifiedNativeReopen='';document.body.append(host);
 const errors=[];let store=null,mounted=0;
 const root=shared.Dgn().createRoot(host,{onUncaughtError:e=>errors.push(String(e)),onCaughtError:e=>errors.push(String(e))});
 function Probe(){store=shared.Fan(shared.H0t);React.useLayoutEffect(()=>{mounted++},[]);return jsx('div',{'data-native-reopen-probe':''})}
 let tree=jsx(Probe);for(const[c,value]of contexts)tree=jsx(c.Provider,{value},tree);
 let remote,unlisten;
 try{
  root.render(tree);for(let i=0;i<30&&!mounted&&!errors.length;i++)await wait(100);
  ok(store&&mounted&&!errors.length,'Actual reopened native scope failed: '+errors.join('|'));
  const manager=store.get(shared.qZA,'local'),records=[],hostId='ssh-isolated-windows-service';
  const transport=new Proxy(manager.requestClient,{get(target,key){if(key==='hostId')return hostId;if(key==='dispose')return()=>{};const value=Reflect.get(target,key,target);return typeof value==='function'?value.bind(target):value}});
  const serviceBindings=[];
  const settings=new Proxy(manager.settings,{get(target,key){
   if(key==='readDeveloperInstructions')return async(input,...rest)=>{ok(input.hostId===hostId,'Unexpected developer-instruction service host');serviceBindings.push({operation:key,requested_host:hostId,service_host:'local',thread_id:input.threadId});return target.readDeveloperInstructions({...input,hostId:'local'},...rest)};
   if(key==='readCatalogEntry')return async(requested,id)=>{ok(requested===hostId,'Unexpected catalog service host');serviceBindings.push({operation:key,requested_host:hostId,service_host:'local',thread_id:id});const row=await target.readCatalogEntry('local',id);return row==null?row:{...row,hostId}};
   const value=Reflect.get(target,key,target);return typeof value==='function'?value.bind(target):value;
  }});
  remote=new manager.constructor({...manager,hostId,transport,settings,threadExecution:manager.threadExecution,coordination:manager.streamState.params.transport,threadProjectAssignments:manager.threadWorkspaceStorage.threadProjectAssignments,savedReadState:manager.readState});
  unlisten=manager.addNotificationCallback(['thread/started','thread/status/changed','turn/started','turn/completed','item/started','item/completed','item/agentMessage/delta'],event=>remote.onNotification(event.method,event.params));
  for(const entry of spec.sent){
   const target=entry.entry==='ssh'?remote:manager;
   const restored=await target.resumeConversation({conversationId:entry.id,model:null,reasoningEffort:null,workspaceRoots:[spec.workspace],collaborationMode:null});
   const lease=target.retainActiveConversation(entry.id);
   try{
    let row,turns=[];const expected=entry.index==null?'Synthetic native first-send acceptance':'Synthetic native facade first send '+entry.index;
    for(let i=0;i<100;i++){row=target.getConversation(entry.id);turns=await target.getCompleteConversationTurns(entry.id);if(row?.latestModel==='fixture-model'&&JSON.stringify(turns).includes(expected))break;await wait(100)}
    ok(row?.id===entry.id&&row.latestModel==='fixture-model','Actual cold model or identity differs: '+JSON.stringify({entry,restored,row:row?{id:row.id,model:row.latestModel}:null}));
    ok(JSON.stringify(turns).includes(expected)&&turns.some(t=>t.status==='completed'),'Actual canonical cold history lacks sent content');
    const paged=await target.sendRequest('thread/turns/list',{threadId:entry.id,cursor:null,limit:20});ok(paged.data?.length>=1,'Cold native pagination empty');
    const read=await target.readThread(entry.id,{includeTurns:false});ok(read.thread.id===entry.id&&read.thread.cwd===spec.workspace,'Cold native route identity changed');
    if(entry.entry==='work')ok(read.thread.projectId===entry.project_id,'Cold Work project identity changed');
    records.push({id:entry.id,entry:entry.entry,index:entry.index??null,model:row.latestModel,canonical_history:true,sent_content_verified:true,project_id:read.thread.projectId??null,host_id:target.getHostId()});
   }finally{lease?.[Symbol.dispose]?.()}
  }
  ok(records.length===6&&new Set(records.map(r=>r.id)).size===6,'Six cold records required');
  ok(errors.length===0,'Native reopen exception');
  return{status:'passed',actual_native_scope:true,actual_native_resume:true,actual_canonical_history:true,global_model_changed:true,records,serviceBindings,synthetic_only:true,ssh_service_simulated:true,encrypted_ssh_transport_tested:false};
 }finally{unlisten?.();remote?.[Symbol.dispose]?.();root.unmount();host.remove()}
})
