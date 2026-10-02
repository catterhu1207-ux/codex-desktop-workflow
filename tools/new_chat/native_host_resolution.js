async function(workspace){
 const setTimeout=(callback,ms,...args)=>globalThis.__qualifiedAwakeDelay(ms).then(()=>callback(...args));
 const manager=this,ok=(v,m)=>{if(!v)throw Error(m)};
 const initial=await import('app://-/assets/app-initial-9e0f03d3c485.js');
 const shared=await import('app://-/assets/app-shared-19f7cd6bb8b6.js');
 ok(typeof initial.kat==='function','Packaged host resolver unavailable');
 const inputs={hasDesktopRuntime:false,isBrowserRuntime:false,hasDeveloperInstructions:false,everydayWork:false,usesDesktopMcp:false,sidebarSectionToolsEnabled:false,projectId:null,instructionOverrides:null,persistentModelPolicy:null};
 const request={cwd:workspace,workspaceRoots:[workspace],workspaceKind:'project',collaborationMode:{mode:'default',settings:{model:'fixture-model',reasoning_effort:'medium',developer_instructions:null}},serviceTier:null,defaultFeatureOverrides:{},config:{model_provider:'custom'},permissionsConfig:{sandboxPolicy:{type:'readOnly'},approvalPolicy:'never',approvalsReviewer:null,activePermissionProfile:null,runtimeWorkspaceRoots:[workspace]}};
 const created=await manager.threadCreation.createConversation(request,async()=>inputs);let id=created.conversationId;
 const row=manager.threadStore.getConversation(id);ok(row.qZN===id,'Native new-chat identity guard missing');
 const calls=[];let indexed=false,cloudMode='placement-error',historicalLocalFailure=false;
 const local={getHostId:()=>manager.getHostId(),readThread:async(threadId,options)=>{calls.push({host:'local',threadId});if(historicalLocalFailure)throw Object.assign(Error('thread not loaded: '+threadId),{code:-32600});return manager.readThread(threadId,options)}};
 const cloud={getHostId:()=> 'durable',readThread:async(threadId)=>{calls.push({host:'durable',threadId});if(cloudMode==='valid-cloud')return{thread:{id:threadId}};throw Object.assign(Error('Client specified an invalid argument: post-cutover thread ID '+threadId+' has unsupported placement format version 3'),{code:-32602,data:{grpcStatusCode:3}})}};
 const scope={get(atom){if(atom===shared.$_t)return indexed;if(atom===shared.avt)return{entriesByConversationId:new Map([[id,{hostId:'local'}]]),entriesByKey:new Map()};if(atom===shared.sA)return[local,cloud];if(atom===shared.kPt)return'connected';throw Error('Unexpected native host selector')}};
 const resolve=()=>initial.kat({scope,preferredHostId:'local',threadId:id,requestOptions:{priority:'interactive'}});
 const fresh=await resolve();ok(fresh.hostId==='local'&&fresh.thread.id===id,'Fresh native local identity resolution failed');
 ok(calls.length===1&&calls[0].host==='local','Fresh local chat reached cloud fallback');
 const freshCalls=calls.splice(0);
 id=(await manager.threadCreation.createConversation(request,async()=>inputs)).conversationId;
 delete manager.threadStore.getConversation(id).qZN;await manager.inactiveThreadUnsubscriber.unsubscribeInactiveConversation(id);
 const released=manager.threadStore.getConversation(id);ok(released.resumeState==='needs_resume','Old idle release not exercised '+JSON.stringify({resumeState:released.resumeState,marker:released.qZN,turns:released.turns?.length,keep:manager.inactiveThreadUnsubscriber.shouldKeepConversationLoaded(released)}));
 historicalLocalFailure=true;
 let failed=null;try{await resolve()}catch(error){failed=String(error)}
 ok(failed&&calls.some(c=>c.host==='durable'),'Native fallback did not reproduce cloud lookup after local miss');
 ok(calls.every(c=>c.threadId===id),'Host resolver rewrote thread identity');
 const fallbackCalls=calls.splice(0);
 indexed=true;let knownFailure=null;try{await resolve()}catch(error){knownFailure=String(error)}
 ok(knownFailure&&!calls.some(c=>c.host==='durable'),'Known local identity crossed to cloud');
 const knownLocalCalls=calls.splice(0);
 indexed=false;cloudMode='valid-cloud';const realCloud=await resolve();ok(realCloud.hostId==='durable','Legitimate cloud routing was blocked');
 return{status:'passed',actual_packaged_host_resolver:true,actual_native_creation_and_backend:true,historical_local_read_failure_replayed:true,cloud_service_simulated:true,identifier_unchanged:true,fresh_local_did_not_query_cloud:true,historical_local_failure_reaches_cloud_fallback:true,known_local_never_crosses_to_cloud:true,valid_cloud_preserved:true,fresh_calls:freshCalls,old_release_calls:fallbackCalls,known_local_calls:knownLocalCalls,old_fallback_error:failed,server_placement_algorithm_not_modified:true};
}
