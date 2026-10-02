async function(workspace){
 const setTimeout=(callback,ms,...args)=>globalThis.__qualifiedAwakeDelay(ms).then(()=>callback(...args));
 const original=this,ok=(v,m)=>{if(!v)throw Error(m)},host='ssh-isolated-windows-service',calls=[];
 // Only the external SSH service is bound to the already isolated real app-server.
 // The frontend uses its native manager, native host branch and unchanged IDs.
 const transport=new Proxy(original.requestClient,{get(target,key){if(key==='hostId')return host;if(key==='dispose')return()=>{};if(key==='sendRequest')return async(method,params,...rest)=>{calls.push({host,method,threadId:params?.threadId??null,cwd:params?.cwd??null});return target.sendRequest(method,params,...rest)};const value=Reflect.get(target,key,target);return typeof value==='function'?value.bind(target):value}});
 const params={...original,hostId:host,transport,threadExecution:null,coordination:original.streamState.params.transport,threadProjectAssignments:original.threadWorkspaceStorage.threadProjectAssignments,savedReadState:original.readState,pendingThreadArchives:new Set()};
 const remote=new original.constructor(params),inputs={hasDesktopRuntime:false,isBrowserRuntime:false,hasDeveloperInstructions:false,everydayWork:false,usesDesktopMcp:false,sidebarSectionToolsEnabled:false,projectId:null,instructionOverrides:null,persistentModelPolicy:null};
 const methods=['thread/started','thread/status/changed','thread/name/updated','turn/started','turn/completed','item/started','item/completed','item/agentMessage/delta','thread/tokenUsage/updated'];
 const unlisten=original.addNotificationCallback(methods,(event)=>remote.onNotification(event.method,event.params));
 const records=[];
 try{
  ok(remote.getHostId()===host&&remote.requestClient.hostId===host,'Native SSH transport/manager identity mismatch');
  for(let index=4;index<6;index++){
   const request={cwd:workspace,workspaceRoots:[workspace],workspaceKind:'project',input:[{type:'text',text:'Synthetic native facade first send '+index,text_elements:[]}],attachments:[],commentAttachments:[],collaborationMode:{mode:'default',settings:{model:'fixture-model',reasoning_effort:'medium',developer_instructions:null}},serviceTier:null,config:{model_provider:'custom'},permissionsConfig:{sandboxPolicy:{type:'readOnly'},approvalPolicy:'never',approvalsReviewer:null,activePermissionProfile:null,runtimeWorkspaceRoots:[workspace]}};
   const result=await remote.startConversation(request,{readThreadCreationInputs:async()=>inputs});
   ok(result.status==='created'&&result.firstTurn.status==='accepted','Native SSH first send not accepted '+JSON.stringify(result));
   const id=result.conversationId;ok(remote.threadStore.getConversation(id)?.id===id,'Native SSH row identity lost');
   const read=await remote.readThread(id,{includeTurns:true});ok(read.thread.id===id&&read.thread.cwd===workspace,'SSH read changed identity or path');
   records.push({id,index,host,first_turn_status:result.firstTurn.status,request_path_preserved:true,entry:'native_SSH_manager'});
  }
  ok(calls.filter(c=>c.method==='thread/start').length>=2&&calls.filter(c=>c.method==='turn/start').length>=2,'SSH backend invocation path missing');
  return{status:'passed',actual_packaged_remote_manager:true,actual_candidate_backend:true,ssh_service_simulated:true,encrypted_ssh_transport_tested:false,host_identity:host,records,calls};
 }finally{unlisten();if(typeof remote[Symbol.dispose]==='function')remote[Symbol.dispose]()}
}
