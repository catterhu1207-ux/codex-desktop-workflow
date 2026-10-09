async function(expectedCount=0){
 const n=this,shared=n.shared,React=shared.ggn(),jsx=React.createElement;
 const ok=(value,message)=>{if(!value)throw Error(message)};
 let selected=null,depth=-1;
 for(const element of document.querySelectorAll('*')){const key=Object.keys(element).find(k=>k.startsWith('__reactFiber$'));if(!key)continue;let f=element[key],d=0;for(let p=f;p;p=p.return)d++;if(d>depth){depth=d;selected=f}}
 ok(selected,'Native root fiber unavailable');
 let contexts=new Map();
 for(let f=selected;f;f=f.return){let type=f.type,context=type?._context??(type?.$$typeof===Symbol.for('react.context')?type:null);if(context&&f.memoizedProps&&'value'in f.memoizedProps&&!contexts.has(context))contexts.set(context,f.memoizedProps.value)}
 const auth={accountId:'synthetic-sidebar-account',authMethod:'chatgpt',isAuthenticated:true,isLoggedIn:true};
 contexts.set(shared.cJ,auth);
 const host=document.createElement('div');host.setAttribute('data-qualified-native-sidebar','');Object.assign(host.style,{position:'fixed',left:'0',top:'0',width:'300px',height:'800px',zIndex:'2147483000'});document.body.append(host);
 const errors=[];let store=null,mounted=0;
 const root=shared.$fn().createRoot(host,{onUncaughtError:e=>errors.push(String(e)),onCaughtError:e=>errors.push(String(e))});
 function Probe(){store=n.scopeHook(n.scope);React.useLayoutEffect(()=>{mounted++},[]);return jsx(n.sidebar,{catalogPageScope:null,catalogSourcesReady:true,codexFeaturesAllowed:true,conversationSections:false,unreadsOnly:false,sidebarMode:'codex',workCloudSidebarContentVisible:false,workLocalSidebarContentVisible:true})}
 const wait=()=>globalThis.__qualifiedAwakeDelay(400);
 let tree=jsx(Probe);for(const [context,value] of contexts)tree=jsx(context.Provider,{value},tree);
 try{
  root.render(tree);for(let i=0;i<20&&!mounted&&!errors.length;i++)await wait();ok(store&&mounted>0&&!errors.length,'Native sidebar mount: '+errors.join('|'));ok(host.querySelector('*'),'Native sidebar produced no elements');
  await wait();
  let catalogCount=0,loadedCount=0,pages=0,historyChecks=[];
  if(expectedCount>0){
   const manager=shared.lXt(store,'local');
   const threads=[];let cursor=null;
   do{const page=await manager.sendRequest('thread/list',{limit:100,cursor,sortKey:'updated_at',modelProviders:null,archived:false,useStateDbOnly:true},{priority:'background',source:'thread_list'});threads.push(...page.data);pages++;cursor=page.nextCursor}while(cursor);
   catalogCount=threads.length;ok(catalogCount>=expectedCount,'Actual backend catalog did not contain '+expectedCount+' tasks: '+catalogCount);
   await manager.observeCatalogThreads(threads);
   const loaded=await manager.loadRecentConversationIds(threads.map(t=>t.id));loadedCount=loaded.length;
   ok(loadedCount>=expectedCount,'Native metadata hydration omitted historical tasks: '+loadedCount);
   for(const thread of [threads[0],threads.at(-1)]){
    const read=await manager.sendRequest('thread/read',{threadId:thread.id,includeTurns:true});
    ok(read.thread.id===thread.id&&read.thread.turns.length>0,'Actual first/last synthetic history failed');
    historyChecks.push({id:thread.id,turn_count:read.thread.turns.length,identity_match:true});
   }
   await manager.refreshRecentConversations({mode:'expanded',sortKey:'updated_at'});await wait();
  }
  const args={sidebarMode:'codex',mode:'project',includeAllProjects:true,chatGptSource:{projects:[],pinnedProjects:[],chatTargets:[],pinnedTargets:[]}};
  let negativeError=null;try{store.get(n.wrong)}catch(e){negativeError=String(e)}
  ok(negativeError?.includes("reading 'id'"),'Old T0n callback must fail in the actual scope reader');
  const layout=store.get(n.selector,args);ok(layout?.layout,'Correct T0n callback failed after negative check');
  let counts=[];
  for(const mode of ['manual','updated_at','manual','updated_at']){
   store.set(n.persistedPrefs,{chatSortMode:mode,initialized:true,mode:'project',projectSortMode:mode,manualSortVersion:1});await wait();
   ok(!errors.length,'Native sidebar live settings: '+errors.join('|'));ok(store.get(n.prefs).projectSortMode===mode,'Native sidebar setting value');
   counts.push({mode,element_count:host.querySelectorAll('*').length});
  }
  let nativeFibers=0;const walk=f=>{if(!f)return;if(f.type===n.sidebar)nativeFibers++;walk(f.child);walk(f.sibling)};const fiberKey=Object.keys(host).find(k=>k.startsWith('__reactContainer$'));walk(host[fiberKey]?.stateNode?.current??host[fiberKey]);
  ok(nativeFibers>0,'Actual bss React consumer was not mounted');
  return {status:'passed',actual_bss_consumer:true,actual_settings_scope:true,synthetic_account_binding:true,external_credentials_used:false,account_id:auth.accountId,auth_method:auth.authMethod,actual_native_provider_count:contexts.size,native_sidebar_fiber_count:nativeFibers,live_updates:counts,uncaught_errors:errors,old_T0n_negative_error:negativeError,correct_T0n_after_negative:true,backend_catalog_count:catalogCount,native_metadata_loaded_count:loadedCount,backend_pages:pages,first_and_last_history:historyChecks,native_catalog_count:layout.chatOrderInput.allKeys.length,native_layout_counts:{projects:layout.layout.projectKeys.length,pinned:layout.layout.pinnedKeys.length,chats:layout.layout.chatKeys.length,groups:layout.allCodexProjectGroups.length}};
 }finally{root.unmount();host.remove()}
}
