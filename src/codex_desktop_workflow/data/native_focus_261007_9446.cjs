const fs=require('node:fs'),path=require('node:path'),clock=require(process.env.CODEX_ACCEPTANCE_TIMER_MODULE);
(async()=>{
 const port=Number(process.env.ISOLATED_DEBUG_PORT),deadline=clock.now()+240000;
 let target,observations=[];
 while(!target&&clock.now()<deadline){
  try{const response=await fetch(`http://127.0.0.1:${port}/json/list`,{signal:AbortSignal.timeout(2000)});const targets=await response.json();observations.push({awake:clock.now(),targets:targets.map(t=>({type:t.type,url:t.url}))});target=targets.find(t=>t.type==='page'&&t.url==='app://-/index.html')}
  catch(error){observations.push({awake:clock.now(),error:String(error)})}
  if(observations.length>64)observations.shift();
  if(!target)await new Promise(r=>clock.setTimeout(r,200))
 }
 if(process.env.ISOLATED_RUNTIME_LOG)fs.writeFileSync(path.join(path.dirname(process.env.ISOLATED_RUNTIME_LOG),'native-primary-route-observation.json'),JSON.stringify({status:target?'primary_route_found':'primary_route_missing',observations},null,2));
 if(!target)throw Error('Exact native primary route unavailable');
 const ws=new WebSocket(target.webSocketDebuggerUrl),pending=new Map();let serial=0,detach;
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 ws.onmessage=e=>{const m=JSON.parse(e.data),p=pending.get(m.id);if(!p)return;pending.delete(m.id);clearInterval(p.timer);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial,timer=clock.setTimeout(()=>{if(pending.delete(id))reject(Error('Native focused evaluation deadline'))},120000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}))});
 try{
  detach=await clock.attachAwakeClock(send);
  const mountedDeadline=clock.now()+120000;
  let mounted=false;
  while(clock.now()<mountedDeadline){
   const ready=await send('Runtime.evaluate',{expression:`(()=>{const names=new Set();let root;for(const element of document.querySelectorAll('*')){const key=Object.keys(element).find(k=>k.startsWith('__reactFiber$'));if(key){root=element[key];while(root.return)root=root.return;break}}if(!root)return false;const visit=f=>{if(!f)return;const t=typeof f.type==='function'?f.type:f.type?.type;if(typeof t==='function')names.add(t.name);visit(f.child);visit(f.sibling)};visit(root);return ['GNc','$Mc','Isc'].every(n=>names.has(n))})()`,returnByValue:true});
   if(ready.result?.value===true){mounted=true;break}
   await new Promise(r=>clock.setTimeout(r,250));
  }
  if(!mounted)throw Error('Native application provider mount deadline');
  const proofFile=path.join(path.dirname(process.env.ISOLATED_RUNTIME_LOG),'renderer-proof-accepted.json'),proofDeadline=clock.now()+240000;
  let proofAccepted=false;while(clock.now()<proofDeadline){if(fs.existsSync(proofFile)){const proof=JSON.parse(fs.readFileSync(proofFile,'utf8'));if(proof.status==='passed'&&proof.feature_count===23){proofAccepted=true;break}}await new Promise(r=>clock.setTimeout(r,250))}
  if(!proofAccepted)throw Error('Production receiver did not accept same-run proof before stateful native checks');
  await detach();detach=await clock.attachAwakeClock(send);
  const functionSource=fs.readFileSync(path.join(__dirname,'native_focus_261007_9446.js'),'utf8');
  const input={groupId:'11111111-1111-4111-8111-111111111111',projectId:'11111111-1111-4111-8111-111111111111',projectKind:'remote',hostId:'synthetic-ssh',hostDisplayName:'Synthetic SSH',label:'project-alpha',path:'/srv/project-alpha',gitRepos:[],threadKeys:[],isCodexWorktree:false,localCwd:process.env.ISOLATED_WORKSPACE};
  if(!input.localCwd)throw Error('Synthetic local workspace missing');
  if(process.env.ISOLATED_COLD_HISTORY_SPEC){const fixture=JSON.parse(fs.readFileSync(process.env.ISOLATED_COLD_HISTORY_SPEC,'utf8'));if(fixture.count!==400||fixture.all_created_and_sent_by_actual_backend!==true||fixture.user_data_copied!==false)throw Error('Qualified real synthetic histories required');input.existingThreads=[{id:fixture.ids[0],index:0},{id:fixture.ids[399],index:399}]}
  const result=await send('Runtime.evaluate',{expression:`${functionSource}(${JSON.stringify(input)})`,awaitPromise:true,returnByValue:true});
  const value=result.result?.value;if(result.exceptionDetails||value?.status!=='passed'||value.native_new_chat_lifecycle?.status!=='passed'||value.mounted_drop?.status!=='passed'||value.native_watch?.status!=='passed')throw Error('Actual native focused cases failed: '+JSON.stringify(result));
  console.log(JSON.stringify(value));
 }finally{if(detach)await detach();ws.close();for(const p of pending.values())clearInterval(p.timer);pending.clear()}
})().then(()=>process.exit(0)).catch(e=>{console.error(String(e));process.exit(1)});
