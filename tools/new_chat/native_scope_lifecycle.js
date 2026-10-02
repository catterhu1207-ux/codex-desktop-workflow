async function(workspace){
 const setTimeout=(callback,ms,...args)=>globalThis.__qualifiedAwakeDelay(ms).then(()=>callback(...args));
 const n=this,shared=n.shared,React=shared.mdn(),jsx=React.createElement,ok=(v,m)=>{if(!v)throw Error(m)};
 let selected=null,depth=-1;
 for(const element of document.querySelectorAll('*')){const key=Object.keys(element).find(k=>k.startsWith('__reactFiber$'));if(!key)continue;let f=element[key],d=0;for(let p=f;p;p=p.return)d++;if(d>depth){depth=d;selected=f}}
 ok(selected,'Native root fiber unavailable');
 const contexts=new Map();
 for(let f=selected;f;f=f.return){const type=f.type,context=type?._context??(type?.$$typeof===Symbol.for('react.context')?type:null);if(context&&f.memoizedProps&&'value'in f.memoizedProps&&!contexts.has(context))contexts.set(context,f.memoizedProps.value)}
 contexts.set(shared.bG,{accountId:'synthetic-lifecycle-account',authMethod:'chatgpt',isAuthenticated:true,isLoggedIn:true});
 const host=document.createElement('div');host.dataset.qualifiedNativeLifecycle='';document.body.append(host);
 const errors=[];let store=null,mounted=0;
 const root=shared.scn().createRoot(host,{onUncaughtError:e=>errors.push(String(e)),onCaughtError:e=>errors.push(String(e))});
 function Probe(){store=n.scopeHook(n.scope);React.useLayoutEffect(()=>{mounted++},[]);return jsx('div',{'data-native-scope-probe':''})}
 let tree=jsx(Probe);for(const [context,value] of contexts)tree=jsx(context.Provider,{value},tree);
 try{
  root.render(tree);for(let i=0;i<30&&!mounted&&!errors.length;i++)await new Promise(r=>setTimeout(r,100));
  ok(store&&mounted&&!errors.length,'Native scope mount: '+errors.join('|'));
  const manager=shared.sJt(store,'local');
  globalThis.__qualifiedNativeManager=manager;globalThis.__nativeLifecycleStage='native-rpc-start';
  ok(typeof manager.startConversation==='function','Native UI manager RPC unavailable');
  const inputs={hasDesktopRuntime:false,isBrowserRuntime:false,hasDeveloperInstructions:false,everydayWork:false,usesDesktopMcp:false,sidebarSectionToolsEnabled:false,projectId:null,instructionOverrides:null,persistentModelPolicy:null};
  const created=[],release=[],settled=[],started=[];
  for(let index=0;index<3;index++){
   const gate=new Promise(resolve=>release[index]=resolve);
   const request={cwd:workspace,workspaceRoots:[workspace],workspaceKind:'project',input:[{type:'text',text:'Synthetic native facade first send '+index,text_elements:[]}],attachments:[],commentAttachments:[],collaborationMode:{mode:'default',settings:{model:'fixture-model',reasoning_effort:'medium',developer_instructions:null}},serviceTier:null,config:{model_provider:'custom'},permissionsConfig:{sandboxPolicy:{type:'readOnly'},approvalPolicy:'never',approvalsReviewer:null,activePermissionProfile:null,runtimeWorkspaceRoots:[workspace]}};
   const result=manager.startConversation(request,{readThreadCreationInputs:async()=>inputs,afterConversationCreated:async id=>{created[index]={id};await gate},onSettled:async value=>settled[index]=value});
   result.catch(()=>{});started[index]=result;
  }
  const deadline=globalThis.__qualifiedAwakeNow()+60000;
  while(created.filter(Boolean).length!==3&&globalThis.__qualifiedAwakeNow()<deadline){ok(!errors.length,'Native scope errors');await new Promise(resolve=>setTimeout(resolve,100))}
  ok(created.filter(Boolean).length===3,'Native UI callback did not create all three chats');
  globalThis.__nativeLifecycleStage='native-rpc-before-first-turn';
  await new Promise(resolve=>setTimeout(resolve,16000));
  const sent=[];
  for(const index of [2,1,0]){
   globalThis.__nativeLifecycleStage='native-rpc-first-send-'+index;
   release[index]();const result=await started[index];
   ok(result.status==='created'&&result.conversationId===created[index].id,'Native first-send identity or status');
   ok(result.firstTurn&& !['failed','outcome-unknown','skipped'].includes(result.firstTurn.status),'Native first send was not confirmed');
   sent.push({id:result.conversationId,index,first_turn_status:result.firstTurn.status});
  }
  globalThis.__nativeLifecycleStage='native-rpc-passed';
  const initial=await import('app://-/assets/app-initial-9e0f03d3c485.js');
  let workReads=0;const originalWork=store.get(shared.VTt);
  const workScope=new Proxy(store,{get(target,key){if(key==='get')return(atom,...args)=>atom===shared.VTt?(workReads++,true):target.get(atom,...args);const value=Reflect.get(target,key,target);return typeof value==='function'?value.bind(target):value}});
  const workRequest={cwd:workspace,workspaceRoots:[workspace],workspaceKind:'project',input:[{type:'text',text:'Synthetic native facade first send 3',text_elements:[]}],attachments:[],commentAttachments:[],collaborationMode:{mode:'default',settings:{model:'fixture-model',reasoning_effort:'medium',developer_instructions:null}},serviceTier:null,config:{model_provider:'custom'},permissionsConfig:{sandboxPolicy:{type:'readOnly'},approvalPolicy:'never',approvalsReviewer:null,activePermissionProfile:null,runtimeWorkspaceRoots:[workspace]}};
  globalThis.__nativeLifecycleStage='native-work-first-send';
  const work=await initial.QBt(workScope,'local',workRequest,{dynamicTools:[]});
  ok(workReads>0&&work.status==='created'&&work.firstTurn.status==='accepted','Actual Work wrapper did not send first message');
  ok(store.get(shared.VTt)===originalWork,'Work fixture changed native persistent mode');
  sent.push({id:work.conversationId,index:3,first_turn_status:work.firstTurn.status,entry:'native_Work_QBt'});
  return{status:'passed',actual_native_scope:true,actual_ui_manager_rpc:true,actual_start_conversation:true,actual_work_wrapper:true,synthetic_work_capability:true,synthetic_external_capabilities:true,created_count:4,pre_first_turn_hold_ms:16000,reversed_first_send:true,sent,uncaught_errors:errors};
 }finally{root.unmount();host.remove()}
}
