(async function(project){
 const shared=await import('app://-/assets/app-shared-30671c57ec82.js'),initial=await import('app://-/assets/app-initial-102e45562729.js'),picker=await import('app://-/assets/composer-project-picker-content-39e0ac169231.js');
 const React=shared.PCn(),jsx=React.createElement,ok=(v,m)=>{if(!v)throw Error(m)},wait=ms=>globalThis.__qualifiedAwakeDelay(ms);shared.ofn();
 ok(typeof initial.Cln==='function'&&initial.Cln.name==='Rcr','Exact native remote-selection hook export');
 ok(typeof initial.fln==='function'&&initial.fln.name==='ilr','Exact native Work route export');
 let selected=null,depth=-1;
 for(const element of document.querySelectorAll('*')){const key=Object.keys(element).find(k=>k.startsWith('__reactFiber$'));if(!key)continue;let d=0;for(let p=element[key];p;p=p.return)d++;if(d>depth){depth=d;selected=element[key]}}
 ok(selected,'Native root context unavailable');
 const nativeProviders=new Map();let top=selected;while(top.return)top=top.return;
 const visit=f=>{if(!f)return;const type=typeof f.type==='function'?f.type:f.type?.type;if(typeof type==='function'&&['GNc','$Mc','Isc'].includes(type.name)){const old=nativeProviders.get(type.name);if(old&&old!==type)throw Error('Ambiguous native provider '+type.name);nativeProviders.set(type.name,type)}visit(f.child);visit(f.sibling)};visit(top);
 for(const name of ['GNc','$Mc','Isc'])ok(nativeProviders.has(name),'Actual native provider missing '+name);
 ok(typeof shared.MMt==='function','Actual native global-state request export');
 const remoteKey=shared.Hin.REMOTE_PROJECTS,selectedKey=shared.Hin.SELECTED_PROJECT;
 ok(remoteKey==='remote-projects'&&typeof selectedKey==='string','Exact native query keys differ');
 const previousRemote=(await shared.MMt('get-global-state',{params:{key:remoteKey}})).value;
 const previousSelected=(await shared.MMt('get-global-state',{params:{key:selectedKey}})).value;
 const rawDescriptor={id:project.projectId,hostId:project.hostId,label:project.projectId,remotePath:project.path};
 ok(typeof shared.kMt==='function','Actual native persisted-setting mutation export missing');
 const contexts=new Map();for(let f=selected;f;f=f.return){let type=f.type,context=type?._context??(type?.$$typeof===Symbol.for('react.context')?type:null);if(context&&f.memoizedProps&&'value'in f.memoizedProps&&!contexts.has(context))contexts.set(context,f.memoizedProps.value)}
 contexts.set(shared.yX,{accountId:'synthetic-work-picker',authMethod:'chatgpt',isAuthenticated:true,isLoggedIn:true});
 const observer=contexts.get(shared.lT)??shared.oT(),ownsObserver=!contexts.has(shared.lT);contexts.set(shared.lT,observer);
 const host=document.createElement('div');host.dataset.qualifiedNativeWorkPicker='';Object.assign(host.style,{position:'fixed',left:'0',top:'0',width:'500px',height:'600px',zIndex:'2147483000'});document.body.append(host);
 const errors=[],selectedRoutes=[];let setSearch=null,mounts=0,nativeStore=null,remoteSelection=null,parentServerVersion=null,parentInstalledVersion=null;
 const root=shared.Dgn().createRoot(host,{onUncaughtError:e=>errors.push(String(e.stack||e)),onCaughtError:e=>errors.push(String(e.stack||e))});
 function Probe(){nativeStore=shared.Fan(shared.H0t);remoteSelection=initial.Cln();const [search,updateSearch]=React.useState('');setSearch=updateSearch;React.useLayoutEffect(()=>{if(parentServerVersion!=null)shared.oF(nativeStore,{hostId:'local',appServerVersion:parentServerVersion,installedCodexVersion:parentInstalledVersion??parentServerVersion});mounts++},[]);return jsx(picker.ComposerProjectPickerContent,{cloudProjectsEnabled:false,workCloudOnly:false,isPending:false,workspaceProjectOptions:{projects:[project],onSelectProject:value=>{initial.csn(nativeStore,value);selectedRoutes.push({selected:value,route:initial.fln({isExistingThread:false,executionHostId:project.hostId,activeLocalProjectId:null,existingAssignment:null,homeRemoteProject:null,selectedRemoteProject:{id:value.projectId,hostId:value.hostId,label:value.label,remotePath:value.path}})})}},projectId:remoteSelection.selectedRemoteProjectId,searchQuery:search,onSearchQueryChange:updateSearch,onCreateProject:undefined,onProjectChange:()=>{},onSelectProject:()=>{},onSelectWorkspaceProject:()=>{},onClose:()=>{}})}
 let tree=jsx(nativeProviders.get('GNc'),null,jsx(nativeProviders.get('$Mc'),null,jsx(shared.Van,{scope:shared.H0t},jsx(nativeProviders.get('Isc'),null,jsx(Probe)))));
 const freshTree=tree;
 function ParentSnapshot(){const parentStore=shared.Fan(shared.H0t),parent=parentStore.get(shared.qZA,'local');parentServerVersion=parent.requestClient.getAppServerVersion();return freshTree}
 tree=jsx(ParentSnapshot);
 tree=jsx(shared.afn,{locale:'en'},tree);
 for(const [context,value]of contexts)tree=jsx(context.Provider,{value},tree);
 try{
  root.render(tree);for(let i=0;i<25&&!mounts&&!errors.length;i++)await wait(100);
  await wait(400);ok(!errors.length,'Native picker mount failed '+errors.join('|'));ok(mounts>0,'Native picker did not mount');
  await shared.kMt(nativeStore,remoteKey,[rawDescriptor],{throwOnFailure:true});
  const remoteSnapshot=nativeStore.query.snapshot(shared.EMt,remoteKey);
  await remoteSnapshot.invalidate();
  for(let i=0;i<30&&!remoteSelection?.remoteProjects?.length;i++)await wait(100);
  ok(remoteSelection?.remoteProjects?.[0]?.label===project.label,'Actual raw remote query did not normalize UUID label: '+JSON.stringify({selection:remoteSelection,wire:(await shared.MMt('get-global-state',{params:{key:remoteKey}})).value,native_snapshot:remoteSnapshot.getData()}));
  const text=host.textContent;ok(text.includes(project.label)&&text.includes(project.hostDisplayName),'Native picker human title/helper text missing: '+text);
  ok(!text.includes(project.projectId),'UUID displayed instead of human project name');
  const searches=[];for(const search of [project.label,project.hostDisplayName,project.path,'not-a-project','']){setSearch(search);await wait(150);ok(!errors.length,'Native search failed');const visible=host.textContent.includes(project.label);ok(visible===(search!=='not-a-project'),'Native search result '+search);searches.push({search,visible})}
  const clickable=[...host.querySelectorAll('button,[role="option"],[role="menuitem"]')].filter(e=>e.textContent.includes(project.label)).sort((a,b)=>a.textContent.length-b.textContent.length)[0];
  ok(clickable,'Actual native project selection control absent');clickable.click();await wait(200);
  ok(selectedRoutes.length===1,'Native project click did not select exactly once');const selection=selectedRoutes[0];
  ok(selection.selected.projectId===project.projectId&&selection.selected.hostId===project.hostId&&selection.selected.path===project.path,'Native picker changed SSH identity');
  ok(selection.route?.projectKind==='remote'&&selection.route.projectId===project.projectId&&selection.route.hostId===project.hostId,'Actual Work assignment route differs');
  for(let i=0;i<30&&remoteSelection?.selectedRemoteProjectId!==project.projectId;i++)await wait(100);
  ok(remoteSelection?.selectedRemoteProject?.label===project.label&&remoteSelection.selectedRemoteProjectId===project.projectId&&remoteSelection.selectedRemoteProject.hostId===project.hostId&&remoteSelection.selectedRemoteProject.remotePath===project.path,'Actual native selection setter/hook identity or human name differs: '+JSON.stringify(remoteSelection));
  const manager=nativeStore.get(shared.qZA,'local'),managerMethods=new Set();
  const lifecycle=await (async function(manager,cwd){
 const ok=(v,m)=>{if(!v)throw Error(m)},wait=ms=>globalThis.__qualifiedAwakeDelay(ms);
 const mode={mode:'default',settings:{model:'fixture-model',reasoning_effort:'medium',developer_instructions:null}};
 const created=await manager.startConversation({input:[],cwd,workspaceRoots:[cwd],initialTitle:'Synthetic native lifecycle acceptance',collaborationMode:mode,useAppServerPermissionDefault:true},{readThreadCreationInputs:async()=>({hasDesktopRuntime:true,isBrowserRuntime:false,instructionOverrides:null,projectId:null,readDynamicTools:async()=>[]})});
 ok(created.status==='created'&&created.firstTurn?.status==='not-requested','Native empty creation failed '+JSON.stringify(created));
 const id=created.conversationId,empty=manager.getConversation(id);
 ok(empty&&empty.qZN===id&&empty.turns.length===0,'Native unsent lifecycle marker/body differs');
 await manager.hydratePinnedThreads([id]);await manager.hydrateBackgroundThreads([id]);
 const afterRestore=manager.getConversation(id);ok(afterRestore?.qZN===id&&afterRestore.turns.length===0,'Native pinned/background restore lost empty draft');
 const activeLease=manager.retainActiveConversation(id);ok(activeLease&&typeof activeLease[Symbol.dispose]==='function','Actual native active owner lease');
 try{
 const messageId=crypto.randomUUID(),text='Synthetic native first-send acceptance';
 const sent=await manager.startTurn(id,{request:{threadId:id,clientUserMessageId:messageId,input:[{type:'text',text,textElements:[]}],cwd,collaborationMode:mode,model:null,effort:'medium',multiAgentMode:'explicitRequestOnly'},context:{useAppServerPermissionDefault:true,attachments:[],restoreMessage:{id:messageId,text,createdAt:Date.now(),cwd,context:{prompt:text,addedFiles:[],ideContext:null,imageAttachments:[],fileAttachments:[],workspaceRoots:[cwd],collaborationMode:mode}}}});
 ok(sent?.turn?.id,'Native first send was not accepted '+JSON.stringify(sent));
 let completeTurns=[];for(let i=0;i<160;i++){completeTurns=await manager.getCompleteConversationTurns(id);if(completeTurns.some(turn=>turn.turnId===sent.turn.id&&turn.status==='completed'))break;await wait(100)}
 const completed=manager.getConversation(id);ok(completed?.threadRuntimeStatus?.type==='idle','Native completion notification did not settle');
 ok(completeTurns.some(turn=>turn.turnId===sent.turn.id&&turn.status==='completed'),'Native canonical first send did not complete');
 ok(completeTurns.some(turn=>(turn.items??[]).some(item=>item.type==='userMessage')&&(turn.items??[]).some(item=>item.type==='agentMessage')),'Native canonical first-send content missing');
 ok(completed.qZN==null,'Native new-thread marker was not cleared after first send');
 const paged=await manager.sendRequest('thread/turns/list',{threadId:id,limit:20,cursor:null});ok(paged.data?.length===1,'First-send native paginated history differs');
 const read=await manager.sendRequest('thread/read',{threadId:id,includeTurns:false});ok(read.thread.id===id,'Native read identity differs');
 return{status:'passed',conversation_id:id,actual_native_start_conversation:true,actual_native_first_send:true,actual_pinned_and_background_restore:true,new_unsent_protected:true,new_marker_cleared_after_first_send:true,actual_paginated_read:true,model:'fixture-model',native_turns:completeTurns.map(t=>({turnId:t.turnId,status:t.status})),canonical_native_history_consumer:true,native_model:{latestModel:completed.latestModel,latestReasoningEffort:completed.latestReasoningEffort},synthetic_loopback_only:true};
 }finally{activeLease[Symbol.dispose]()}
}
)(manager,project.localCwd);
  const mountedDrop=await (async function(){
 const shared=await import('app://-/assets/app-shared-30671c57ec82.js'),primary=await import('app://-/assets/app-primary-cd52df2361eb.js');
 shared.ofn();primary.vt();
 const React=shared.PCn(),jsx=React.createElement,ok=(v,m)=>{if(!v)throw Error(m)},wait=ms=>globalThis.__qualifiedAwakeDelay(ms);
 ok(primary.gt.name==='r7','Native drop component export changed');
 const host=document.createElement('div');host.dataset.qualifiedDrop='';document.body.append(host);
 const errors=[],received=[],root=shared.Dgn().createRoot(host,{onUncaughtError:e=>errors.push(String(e)),onCaughtError:e=>errors.push(String(e))});
 const render=async disabled=>{root.render(jsx(shared.afn,{locale:'en'},jsx(primary.gt,{disabled,onFilesDropped:files=>received.push(files.map(f=>({name:f.name,size:f.size}))),children:jsx('span',null,'Synthetic attachment target')})));await wait(150);ok(!errors.length,'Native drop mount error '+errors.join('|'))};
 const dispatch=(type,transfer,target=host.firstElementChild)=>{const e=new DragEvent(type,{bubbles:true,cancelable:true,dataTransfer:transfer});target.dispatchEvent(e);return e};
 try{
  await render(false);
  const file=new File(['synthetic attachment'],'fixture.txt',{type:'text/plain'}),transfer=new DataTransfer();transfer.items.add(file);
  const drag=dispatch('dragenter',transfer);await wait(100);ok(drag.defaultPrevented,'Native drag-enter did not prevent default');
  const drop=dispatch('drop',transfer);await wait(100);ok(drop.defaultPrevented&&received.length===1&&received[0][0].name==='fixture.txt','Native drop did not route file once');
  await render(true);const disabled=dispatch('drop',transfer);await wait(100);ok(disabled.defaultPrevented&&received.length===1,'Disabled drop routed an attachment');
  await render(false);const plain=new DataTransfer();plain.setData('text/plain','synthetic text');const text=dispatch('drop',plain);await wait(100);ok(!text.defaultPrevented&&received.length===1,'Non-file drop was accepted');
  const nested=document.createElement('div');nested.dataset.chatgptFileDropTarget='';host.firstElementChild.append(nested);dispatch('drop',transfer,nested);await wait(100);ok(received.length===1,'Nested drop target duplicated file attachment');nested.remove();
  return{status:'passed',actual_native_component:'r7',actual_native_hook:'WFt',actual_dom_drag_events:true,enabled_file_route:true,disabled_and_nonfile_rejected:true,nested_target_not_duplicated:true,synthetic_attachment_only:true,synthetic_drag_cursor_not_qualified:true};
 }finally{root.unmount();host.remove()}
}
)();
  const nativeWatch=await (async function(manager,cwd){
 const fs=manager.filesystem,watch=manager.openFileWatches,ok=(v,m)=>{if(!v)throw Error(m)};
 ok(fs&&typeof fs.getOpenFileWatchPath==='function','Native filesystem watch path provider missing');
 ok(watch&&typeof watch.getWatchPath==='function','Native watcher binding missing');
 const id=lifecycle.conversation_id;
 const cases=[];
 for(const path of ['fixture.txt',cwd+'/fixture.txt',cwd.replaceAll('/','\\')+'\\fixture.txt','https://invalid.example/fixture.txt']){
  let direct=null,error=null;
  try{direct=fs.getOpenFileWatchPath(cwd,path,'local')}catch(e){error=String(e)}
  cases.push({input:path,direct,error});
 }
 const normal=watch.getWatchPath(id,'fixture.txt'),expected=cwd.replaceAll('\\','/')+'/fixture.txt';
 ok(cases.slice(0,3).every(c=>c.error==null&&c.direct===expected)&&normal===expected,'Native Windows path normalization/binding differs');
 const owner='qualified-isolated-watch-owner',path='qualified-watch-fixture.txt',requests=[],client=manager.requestClient,original=client.sendRequest;
 client.sendRequest=function(method,params,...rest){if(method==='fs/watch'||method==='fs/unwatch')requests.push({method,params});return original.call(this,method,params,...rest)};
 try{
  watch.setOpenFileTabFiles(id,[{path,hostId:'local'}],owner);
  const record=[...watch.watchesByKey.values()].find(e=>e.target.path===cwd.replaceAll('\\','/')+'/'+path);
  ok(record,'Actual watch registration did not normalize the Windows path');
  await record.startPromise;ok(record.isStarted,'Actual backend did not start the watch');
  const started=requests.find(e=>e.method==='fs/watch'&&e.params.watchId===record.watchId);ok(started?.params.path===record.target.path,'Actual fs/watch call used a different path');
  watch.removeOwner(owner);
  const stopped=requests.find(e=>e.method==='fs/unwatch'&&e.params.watchId===record.watchId);ok(stopped&&!watch.watchesByWatchId.has(record.watchId),'Actual watch cleanup did not call fs/unwatch');
  return{status:'passed',actual_native_filesystem_provider:true,actual_native_watch_binding:true,actual_cwd:manager.getConversationCwd(id),binding_path:normal,cases:cases.slice(0,3),actual_backend_watch_started:true,actual_backend_unwatch_sent:true,requests};
 }finally{watch.removeOwner(owner);client.sendRequest=original}
}
)(manager,project.localCwd);
  const six=await(async()=>{
   const records=[{id:lifecycle.conversation_id,entry:'local',model:'fixture-model',canonical_complete:true}],forwarded=[];
   const workProject=(await manager.sendRequest('project/create',{name:'Synthetic native Work',roots:[{path:project.localCwd}],metadata:{purpose:'isolated-runtime-qualification'},idempotencyKey:crypto.randomUUID()})).project;
   ok(workProject?.id,'Actual backend Work project was not created');
   const workRoute=initial.fln({isExistingThread:false,executionHostId:'local',activeLocalProjectId:workProject.id,existingAssignment:null});
   ok(workRoute?.projectId===workProject.id,'Actual Work creation route lost project identity');
   async function create(target,index,entry,projectId){
    const mode={mode:'default',settings:{model:'fixture-model',reasoning_effort:'medium',developer_instructions:null}};
    const inputs={hasDesktopRuntime:entry!=='ssh',isBrowserRuntime:false,instructionOverrides:null,projectId:projectId??null,readDynamicTools:async()=>[]};
    const made=await target.startConversation({input:[{type:'text',text:'Synthetic native facade first send '+index,textElements:[]}],cwd:project.localCwd,workspaceRoots:[project.localCwd],workspaceKind:'project',collaborationMode:mode,config:{model_provider:'fixture'},initialTitle:'Synthetic '+entry+' lifecycle',skipAutoTitleGeneration:true,useAppServerPermissionDefault:true},{readThreadCreationInputs:async()=>inputs});
    ok(made?.status==='created'&&made.firstTurn?.status==='accepted','Native '+entry+' first send did not acknowledge: '+JSON.stringify(made));
    const id=made.conversationId,lease=target.retainActiveConversation(id);
    try{
     let turns=[];for(let attempt=0;attempt<160;attempt++){turns=await target.getCompleteConversationTurns(id);if(turns.some(t=>t.status==='completed'&&JSON.stringify(t).includes('Synthetic native facade first send '+index)))break;await wait(100)}
     ok(turns.some(t=>t.status==='completed'&&JSON.stringify(t).includes('Synthetic native facade first send '+index)),'Native '+entry+' canonical completion/content missing');
     const read=await target.readThread(id,{includeTurns:false});ok(read.thread.id===id&&read.thread.cwd===project.localCwd,'Native '+entry+' read changed identity or cwd');
     const model=target.getConversation(id)?.latestModel;ok(model==='fixture-model','Native '+entry+' model differs');
     return{id,index,entry,project_id:projectId??null,model,canonical_complete:true};
    }finally{lease?.[Symbol.dispose]?.()}
   }
   records.push(await create(manager,1,'local',null));
   for(const index of [2,3])records.push(await create(manager,index,'work',workProject.id));
   const host='ssh-isolated-windows-service';
   const transport=new Proxy(manager.requestClient,{get(target,key){if(key==='hostId')return host;if(key==='dispose')return()=>{};if(key==='sendRequest')return async(method,params,...rest)=>{forwarded.push({host,method,threadId:params?.threadId??null,cwd:params?.cwd??null});return target.sendRequest(method,params,...rest)};const value=Reflect.get(target,key,target);return typeof value==='function'?value.bind(target):value}});
   const remote=new manager.constructor({...manager,hostId:host,transport,threadExecution:manager.threadExecution,coordination:manager.streamState.params.transport,threadProjectAssignments:manager.threadWorkspaceStorage.threadProjectAssignments,savedReadState:manager.readState});
   const methods=['thread/started','thread/status/changed','thread/name/updated','turn/started','turn/completed','item/started','item/completed','item/agentMessage/delta','thread/tokenUsage/updated'];
   const forwardingErrors=[];
   const unlisten=manager.addNotificationCallback(methods,event=>{try{remote.onNotification(event.method,event.params)}catch(error){forwardingErrors.push({method:event.method,error:String(error)})}});
   try{ok(remote.getHostId()===host&&remote.requestClient.hostId===host,'Native SSH manager/transport host identity differs');for(const index of [4,5])records.push(await create(remote,index,'ssh',null))}
   finally{unlisten();remote[Symbol.dispose]?.()}
   ok(forwardingErrors.length===0,'Native SSH notification forwarding failed: '+JSON.stringify(forwardingErrors));
   ok(records.length===6&&new Set(records.map(r=>r.id)).size===6,'Six native lifecycle identities not unique');
   ok(forwarded.filter(c=>c.method==='thread/start').length===2&&forwarded.filter(c=>c.method==='turn/start').length===2,'Actual SSH branch did not call candidate backend twice');
   return{status:'passed',synthetic_sent_chats:6,records,actual_native_class:true,actual_native_work_route:true,actual_candidate_backend:true,ssh_service_simulated:true,encrypted_ssh_transport_tested:false,forwarded};
  })();
  const cold=[];
  for(const entry of project.existingThreads??[]){
   await manager.resumeConversation({conversationId:entry.id,model:null,reasoningEffort:null,workspaceRoots:[project.localCwd],collaborationMode:null});
   let row,turns=[];
   for(let attempt=0;attempt<100;attempt++){row=manager.getConversation(entry.id);turns=await manager.getCompleteConversationTurns(entry.id);if(row?.latestModel==='fixture-model'&&JSON.stringify(turns).includes('Synthetic startup task '+entry.index))break;await wait(100)}
   ok(row?.id===entry.id&&row.latestModel==='fixture-model','Cold native model/identity differs from saved task');
   ok(JSON.stringify(turns).includes('Synthetic startup task '+entry.index)&&turns.some(t=>t.status==='completed'),'Canonical cold history did not return sent user content');
   cold.push({id:entry.id,model:row.latestModel,canonical_history:true,sent_content_verified:true});
  }
  for(let value=manager;value&&value!==Object.prototype;value=Object.getPrototypeOf(value))for(const [name,descriptor]of Object.entries(Object.getOwnPropertyDescriptors(value)))if(typeof descriptor.value==='function')managerMethods.add(name);
  return{status:'passed',actual_native_picker:true,actual_native_work_assignment:true,actual_native_remote_query_hook:true,actual_native_selection_setter:true,raw_remote_uuid_normalized:true,native_searches:searches,human_title_and_helper:true,visible_uuid_count:0,selected_route_identity:true,callback_count:1,scope_isolated:true,synthetic_external_project_data:true,native_new_chat_lifecycle:lifecycle,native_six_lifecycle:six,mounted_drop:mountedDrop,native_watch:nativeWatch,native_cold_history:{status:project.existingThreads?.length?'passed':'not_applicable_empty',records:cold,global_default_changed:!!project.existingThreads?.length},manager_methods:[...managerMethods],uncaught_errors:errors};
 }finally{if(nativeStore){await shared.kMt(nativeStore,remoteKey,previousRemote??null,{throwOnFailure:true});await shared.kMt(nativeStore,selectedKey,previousSelected??null,{throwOnFailure:true})}root.unmount();host.remove();if(ownsObserver)observer.disconnect()}
}
)
