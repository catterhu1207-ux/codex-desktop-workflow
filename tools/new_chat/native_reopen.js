async function(spec){
 const setTimeout=(callback,ms,...args)=>globalThis.__qualifiedAwakeDelay(ms).then(()=>callback(...args));
 const workspace=spec.workspace;
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
  const manager=shared.sJt(store,'local'),records=[];
  for(const entry of spec.sent){
   const restored=await manager.resumeConversation({conversationId:entry.id,model:null,reasoningEffort:null,workspaceRoots:[workspace],collaborationMode:null});
   let row=await manager.getConversation(entry.id);
   const initialModel=row?.latestModel??null;let modelPolls=0;
   while(row?.latestModel!=='fixture-model'&&modelPolls<50){await new Promise(r=>setTimeout(r,100));row=await manager.getConversation(entry.id);modelPolls++}
   ok(row?.id===entry.id,'Cold native row identity missing '+JSON.stringify(restored));
   ok(row.latestModel==='fixture-model','Cold native model changed '+JSON.stringify({id:entry.id,index:entry.index,initialModel,latestModel:row.latestModel,resumeState:row.resumeState,restored}));
   const response=await manager.readThread(entry.id,{includeTurns:true});
   ok(response.thread.id===entry.id&&JSON.stringify(response.thread.turns).includes('Synthetic native facade first send '+entry.index),'Cold native UI history missing');
   records.push({id:entry.id,index:entry.index,model:row.latestModel,initial_model:initialModel,model_notification_polls:modelPolls,resume_state:row.resumeState,content_verified:true,original_entry:entry.entry??'local'});
  }
  return{status:'passed',actual_native_scope:true,actual_native_resume:true,actual_native_read:true,records,uncaught_errors:errors};
 }finally{root.unmount();host.remove()}
}
