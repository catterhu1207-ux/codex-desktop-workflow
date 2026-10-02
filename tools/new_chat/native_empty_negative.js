async function(workspace){
 const setTimeout=(callback,ms,...args)=>globalThis.__qualifiedAwakeDelay(ms).then(()=>callback(...args));
 const manager=this,ok=(v,m)=>{if(!v)throw Error(m)};
 const inputs={hasDesktopRuntime:false,isBrowserRuntime:false,hasDeveloperInstructions:false,everydayWork:false,usesDesktopMcp:false,sidebarSectionToolsEnabled:false,projectId:null,instructionOverrides:null,persistentModelPolicy:null};
 const request={cwd:workspace,workspaceRoots:[workspace],workspaceKind:'project',collaborationMode:{mode:'default',settings:{model:'fixture-model',reasoning_effort:'medium',developer_instructions:null}},serviceTier:null,defaultFeatureOverrides:{},config:{model_provider:'custom'},permissionsConfig:{sandboxPolicy:{type:'readOnly'},approvalPolicy:'never',approvalsReviewer:null,activePermissionProfile:null,runtimeWorkspaceRoots:[workspace]}};
 globalThis.__nativeLifecycleStage='actual-empty-guard-negative';
 const created=await manager.threadCreation.createConversation(request,async()=>inputs),id=created.conversationId;
 const row=manager.threadStore.getConversation(id);
 ok(row?.qZN===id,'Actual native creation guard missing');
 ok(manager.inactiveThreadUnsubscriber.shouldKeepConversationLoaded(row),'Actual native guard not retained');
 delete row.qZN;
 ok(!manager.inactiveThreadUnsubscriber.shouldKeepConversationLoaded(row),'Removed guard did not restore old release behavior');
 await manager.inactiveThreadUnsubscriber.unsubscribeInactiveConversation(id);
 ok(manager.threadStore.getConversation(id)?.resumeState==='needs_resume','Actual idle release did not invalidate in-memory history');
 let rejected=null;
 try{await manager.requestClient.sendRequest('thread/resume',{threadId:id,historyMode:'paginated'})}catch(error){rejected=String(error)}
 ok(rejected&&/no rollout found|missing source rollout/i.test(rejected),'Actual old premature resume did not reproduce: '+rejected);
 return{status:'passed',actual_manager:true,actual_creation:true,actual_idle_cache:true,actual_thread_unsubscribe:true,guard_removed_negative_reproduced:true,actual_candidate_backend:true,error:rejected,id,current_database_modified:false};
}
