const fs=require('node:fs'),path=require('node:path'),clock=require(process.env.CODEX_ACCEPTANCE_TIMER_MODULE);
(async()=>{
 const port=Number(process.env.ISOLATED_DEBUG_PORT),deadline=clock.now()+120000;
 let target;
 while(!target&&clock.now()<deadline){try{target=(await(await fetch(`http://127.0.0.1:${port}/json/list`,{signal:AbortSignal.timeout(2000)})).json()).find(t=>t.type==='page'&&t.url==='app://-/index.html')}catch{}if(!target)await new Promise(r=>clock.setTimeout(r,200))}
 if(!target)throw Error('Exact isolated primary route missing');
 const ws=new WebSocket(target.webSocketDebuggerUrl),pending=new Map();let serial=0,onPause,detach,captureTimer;
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 ws.onmessage=e=>{const value=JSON.parse(e.data);if(value.id){const p=pending.get(value.id);if(p){pending.delete(value.id);clearInterval(p.timer);value.error?p.reject(Error(JSON.stringify(value.error))):p.resolve(value.result)}}else if(value.method==='Debugger.paused'&&onPause)onPause(value.params)};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial,timer=clock.setTimeout(()=>{if(pending.delete(id))reject(Error('CDP deadline: '+method))},120000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({id,method,params}))});
 try{
  detach=await clock.attachAwakeClock(send);await send('Debugger.enable');
  const source=fs.readFileSync(process.env.PUBLIC_RENDERER_MODULE,'utf8'),lines=source.split('\n'),line=lines.findIndex(value=>value.startsWith('async function qualifyMountedUpdate('))+1;
  if(line<1||!lines[line].includes('shared.ofn()'))throw Error('Exact native update capture point missing');
  const breakpoint=await send('Debugger.setBreakpointByUrl',{url:'app://-/x',lineNumber:line,columnNumber:1});
  const captured=new Promise(resolve=>onPause=resolve);
  // Capture the first native execution; a reload would create a second proof run.
  const paused=await Promise.race([captured,new Promise((_,reject)=>{captureTimer=clock.setTimeout(()=>reject(Error('Native update capture deadline')),120000)})]);
  clearInterval(captureTimer);captureTimer=null;
  const capture=await send('Debugger.evaluateOnCallFrame',{callFrameId:paused.callFrames[0].callFrameId,expression:'({...x.native,shared})',returnByValue:false});
  if(capture.exceptionDetails||!capture.result?.objectId)throw Error('Actual native update bindings unavailable');
  await send('Debugger.removeBreakpoint',{breakpointId:breakpoint.breakpointId});await send('Debugger.resume');
  const proofDeadline=clock.now()+120000;let completedProof=false;
  while(clock.now()<proofDeadline){const raw=fs.readFileSync(process.env.ISOLATED_RUNTIME_LOG,'utf8');if(raw.includes('"artifact_id":"2.7.21-356c13dc7158"')&&raw.includes('"status":"passed"')){completedProof=true;break}await new Promise(r=>clock.setTimeout(r,200))}
  if(!completedProof)throw Error('Fresh actual renderer proof missing');
  const root=path.resolve(process.env.ISOLATED_CODEX_HOME),cache=path.join(root,'.cache','codex-desktop-workflow','official-update-awareness.json');
  const before=fs.existsSync(cache)?fs.readFileSync(cache):null;fs.mkdirSync(path.dirname(cache),{recursive:true});
  const rows=[];await new Promise(r=>clock.setTimeout(r,30000));
  try{
   for(const stage of ['published','package_available','adaptation_ready']){
    const value={schema_version:2,checked_at:new Date().toISOString(),published_version:'26.1008.9000.0',package:{status:'unavailable'},content_logged:false};
    if(stage!=='published')value.package={status:'manifest_verified',identity:'OpenAI.Codex',architecture:'x64',version:'26.1008.9000.0'};
    if(stage==='adaptation_ready')value.prepared={status:'adaptation_prepared',qualified:true,version:'26.1008.9000.0',source_asar_sha256:'a'.repeat(64),qualification_sha256:'b'.repeat(64)};
    fs.writeFileSync(cache,JSON.stringify({schema_version:2,last_status:value}));
    const result=await send('Runtime.callFunctionOn',{objectId:capture.result.objectId,functionDeclaration:fs.readFileSync(path.join(__dirname,'mount_9446.js'),'utf8'),arguments:[{value:stage}],awaitPromise:true,returnByValue:true});
    if(result.exceptionDetails||result.result?.value?.status!=='passed')throw Error(JSON.stringify(result));
    rows.push(result.result.value);
   }
   if(new Set(rows.map(r=>r.icon)).size!==3)throw Error('Update stage icons are not distinct');
   console.log(JSON.stringify({status:'passed',rows,actual_packaged_component:true,english_labels_and_tooltips:true,synthetic_external_status_cache:true,real_user_data_modified:false}));
  }finally{if(before===null)fs.unlinkSync(cache);else fs.writeFileSync(cache,before)}
 }finally{if(captureTimer)clearInterval(captureTimer);if(detach)await detach();await send('Debugger.disable').catch(()=>{});ws.close();for(const p of pending.values())clearInterval(p.timer);pending.clear()}
})().then(()=>process.exit(0)).catch(error=>{console.error(String(error));process.exit(1)});
