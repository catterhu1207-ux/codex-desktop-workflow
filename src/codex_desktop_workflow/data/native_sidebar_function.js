async function(){
 const setTimeout=(callback,ms,...args)=>globalThis.__qualifiedAwakeDelay(ms).then(()=>callback(...args));
 const n=this,shared=n.shared,React=shared.mdn(),jsx=React.createElement;
 const ok=(value,message)=>{if(!value)throw Error(message)};
 let selected=null,depth=-1;
 for(const element of document.querySelectorAll('*')){const key=Object.keys(element).find(k=>k.startsWith('__reactFiber$'));if(!key)continue;let f=element[key],d=0;for(let p=f;p;p=p.return)d++;if(d>depth){depth=d;selected=f}}
 ok(selected,'Native root fiber unavailable');
 let contexts=new Map();
 for(let f=selected;f;f=f.return){let type=f.type,context=type?._context??(type?.$$typeof===Symbol.for('react.context')?type:null);if(context&&f.memoizedProps&&'value'in f.memoizedProps&&!contexts.has(context))contexts.set(context,f.memoizedProps.value)}
 const auth={accountId:'synthetic-sidebar-account',authMethod:'chatgpt',isAuthenticated:true,isLoggedIn:true};
 contexts.set(shared.bG,auth);
 const host=document.createElement('div');host.setAttribute('data-qualified-native-sidebar','');Object.assign(host.style,{position:'fixed',left:'0',top:'0',width:'300px',height:'800px',zIndex:'2147483000'});document.body.append(host);
 const errors=[];let store=null,mounted=0;
 const root=shared.scn().createRoot(host,{onUncaughtError:e=>errors.push(String(e)),onCaughtError:e=>errors.push(String(e))});
 function Probe(){store=n.scopeHook(n.scope);React.useLayoutEffect(()=>{mounted++},[]);return jsx(n.sidebar,{catalogPageScope:null,catalogSourcesReady:true,codexFeaturesAllowed:true,conversationSections:false,unreadsOnly:false,sidebarMode:'codex',workCloudSidebarContentVisible:false,workLocalSidebarContentVisible:true})}
 const wait=()=>new Promise(resolve=>setTimeout(resolve,400));
 let tree=jsx(Probe);for(const [context,value] of contexts)tree=jsx(context.Provider,{value},tree);
 try{
  root.render(tree);for(let i=0;i<20&&!mounted&&!errors.length;i++)await wait();ok(store&&mounted>0&&!errors.length,'Native sidebar mount: '+errors.join('|'));ok(host.querySelector('*'),'Native sidebar produced no elements');
  ok(shared.INt,'Native external shared-object family unavailable');
  store.set(shared.INt,'remote_ssh_connections',[{hostId:'synthetic-ssh-host',displayName:'Synthetic SSH host',source:'discovered',alias:'synthetic-unconfigured-host',autoConnect:true,hostname:null,sshPort:null,identity:null,connectionAnalyticsId:'00000000-0000-4000-8000-000000000001'}]);
  store.set(shared.INt,'remote_wsl_connections',[]);
  store.set(shared.INt,'remote_control_connections',[]);
  await wait();
  const args={sidebarMode:'codex',mode:'project',includeAllProjects:true,chatGptSource:{projects:[],pinnedProjects:[],chatTargets:[],pinnedTargets:[]}};
  let negativeError=null;try{store.get(n.wrong)}catch(e){negativeError=String(e)}
  ok(negativeError?.includes("reading 'id'"),'Old T0n callback must fail in the actual scope reader');
  const layout=store.get(n.selector,args);ok(layout?.layout,'Correct T0n callback failed after negative check');
  ok(layout.layout.projectKeys.length>0&&layout.layout.pinnedKeys.length>0,'Native normal and pinned project recovery was empty');
  const groups=[...layout.allCodexProjectGroups,...layout.orderedPinnedProjectGroups];
  ok(groups.some(g=>g.projectKind==='local')&&groups.some(g=>g.projectKind==='remote'),'Native local and SSH group recovery missing');
  let counts=[];
  for(const mode of ['manual','updated_at','manual','updated_at']){
   const before=store.get(n.prefs);
   store.set(n.persistedPrefs,{chatSortMode:mode,initialized:true,mode:'project',projectSortMode:mode,manualSortVersion:1});
   const observations=[];
   for(let attempt=0;attempt<15;attempt++){await wait();const actual=store.get(n.prefs);observations.push({actual,persisted:store.get(n.persistedPrefs)});if(actual.projectSortMode===mode)break}
   ok(!errors.length,'Native sidebar live settings: '+errors.join('|'));ok(store.get(n.prefs).projectSortMode===mode,'Native sidebar setting value '+JSON.stringify({mode,before,observations}));
   counts.push({mode,element_count:host.querySelectorAll('*').length,observations});
  }
  let nativeFibers=0;const walk=f=>{if(!f)return;if(f.type===n.sidebar)nativeFibers++;walk(f.child);walk(f.sibling)};const fiberKey=Object.keys(host).find(k=>k.startsWith('__reactContainer$'));walk(host[fiberKey]?.stateNode?.current??host[fiberKey]);
  ok(nativeFibers>0,'Actual bss React consumer was not mounted');
  return {status:'passed',actual_bss_consumer:true,actual_settings_scope:true,synthetic_account_binding:true,external_credentials_used:false,account_id:auth.accountId,auth_method:auth.authMethod,actual_native_provider_count:contexts.size,native_sidebar_fiber_count:nativeFibers,live_updates:counts,uncaught_errors:errors,old_T0n_negative_error:negativeError,correct_T0n_after_negative:true,native_layout_counts:{projects:layout.layout.projectKeys.length,pinned:layout.layout.pinnedKeys.length,chats:layout.layout.chatKeys.length,groups:layout.allCodexProjectGroups.length}};
 }finally{root.unmount();host.remove()}
}
