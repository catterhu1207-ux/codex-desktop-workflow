const fs=require('fs');
const awake=require(process.env.CODEX_ACCEPTANCE_TIMER_MODULE),setTimeout=awake.setTimeout;
(async()=>{
 const port=Number(process.env.ISOLATED_DEBUG_PORT),location=JSON.parse(fs.readFileSync(process.env.PUBLIC_NATIVE_DATA+'/sidebar-capture-location_7124.json','utf8'));
 let target=null;const deadline=awake.now()+60000;
 while(!target&&awake.now()<deadline){try{target=(await(await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t=>t.type==='page'&&t.url==='app://-/index.html')}catch{}if(!target)await new Promise(r=>setTimeout(r,80))}
 if(!target)throw Error('Missing isolated primary page');
 const ws=new WebSocket(target.webSocketDebuggerUrl);let id=0,pending=new Map(),pause;
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 ws.onmessage=event=>{const value=JSON.parse(event.data);if(value.id){const p=pending.get(value.id);if(p){pending.delete(value.id);value.error?p.reject(Error(JSON.stringify(value.error))):p.resolve(value.result)}}else if(value.method==='Debugger.paused'&&pause)pause(value.params)};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const key=++id;pending.set(key,{resolve,reject});ws.send(JSON.stringify({id:key,method,params}));setTimeout(()=>{if(pending.delete(key))reject(Error('CDP deadline '+method))},30000).unref()});
 let detachAwake=null,captureTimer=null;
 try{
  detachAwake=await awake.attachAwakeClock(send);
  await send('Debugger.enable');
  const {breakpointId}=await send('Debugger.setBreakpointByUrl',{url:location.url,lineNumber:location.line,columnNumber:location.column});
  const captured=new Promise(resolve=>pause=resolve);
  // Start the actual packaged verifier after attaching, including fast startups.
  const replay=send('Runtime.evaluate',{expression:'void import("app://-/x").then(m=>m.r())',awaitPromise:false}).catch(e=>{throw e});
  const event=await Promise.race([captured,new Promise((_,reject)=>{captureTimer=setTimeout(()=>reject(Error('Native proof closure capture deadline')),60000)})]);
  clearInterval(captureTimer);captureTimer=null;
  const capture=await send('Debugger.evaluateOnCallFrame',{callFrameId:event.callFrames[0].callFrameId,expression:'({...x.native,shared})',returnByValue:false});
  if(capture.exceptionDetails||!capture.result?.objectId)throw Error('Native closure unavailable: '+JSON.stringify(capture));
  await send('Debugger.removeBreakpoint',{breakpointId});await send('Debugger.resume');await replay;
  const proofDeadline=awake.now()+60000;
  let primaryProof=null;
  while(awake.now()<proofDeadline){
   const file=process.env.ISOLATED_RUNTIME_LOG;
   const lines=file&&fs.existsSync(file)?fs.readFileSync(file,'utf8').split('\n'):[];
   primaryProof=lines.find(line=>line.includes('[CF9]')&&line.includes('"status":"passed"')&&line.includes('2.7.17-76fe7078248c')&&line.includes('rendererWindowAppearance=primary')&&line.includes('rendererWindowVisible=true'));
   if(primaryProof)break;
   await new Promise(resolve=>setTimeout(resolve,150));
  }
  if(!primaryProof)throw Error('Actual primary renderer proof missing before native stress checks');
  if(detachAwake)await detachAwake();
  detachAwake=await awake.attachAwakeClock(send);

  const path=require('node:path'),root=path.resolve(process.env.ISOLATED_CODEX_HOME),cache=path.resolve(process.env.PUBLIC_UPDATE_CACHE);
  if(!cache.startsWith(root+path.sep)||path.basename(cache)!=='official-update-awareness.json')throw Error('Unqualified update fixture path');
  const before=fs.existsSync(cache)?fs.readFileSync(cache):null;fs.mkdirSync(path.dirname(cache),{recursive:true});
  const rows=[];
  // Finish the native bridge's initial bounded network check before supplying
  // three synthetic external status responses in this isolated test profile.
  await new Promise(resolve=>setTimeout(resolve,30000));
  try{
   for(const stage of ['published','package_available','adaptation_ready']){
    const value={schema_version:2,checked_at:new Date().toISOString(),published_version:'26.1003.9000.0',package:{status:'unavailable'},content_logged:false};
    if(stage!=='published')value.package={status:'manifest_verified',identity:'OpenAI.Codex',architecture:'x64',version:'26.1003.9000.0'};
    if(stage==='adaptation_ready')value.prepared={status:'adaptation_prepared',qualified:true,version:'26.1003.9000.0',source_asar_sha256:'a'.repeat(64),qualification_sha256:'b'.repeat(64)};
    fs.writeFileSync(cache,JSON.stringify({schema_version:2,last_status:value}));
    const result=await send('Runtime.callFunctionOn',{objectId:capture.result.objectId,functionDeclaration:fs.readFileSync(__dirname+'/mount.js','utf8'),arguments:[{value:stage}],awaitPromise:true,returnByValue:true});
    if(result.exceptionDetails||result.result?.value?.status!=='passed')throw Error(JSON.stringify(result));
    rows.push(result.result.value);
   }
   if(new Set(rows.map(row=>row.icon)).size!==3)throw Error('Collapsed update states share an icon');
   console.log(JSON.stringify({status:'passed',actual_native_component:true,actual_native_ipc_bridge:true,synthetic_external_status_binding:true,no_download_performed:true,rows}));
  }finally{if(before===null){if(fs.existsSync(cache))fs.unlinkSync(cache)}else fs.writeFileSync(cache,before)}

 }finally{if(captureTimer)clearInterval(captureTimer);try{if(detachAwake)await detachAwake()}finally{await send('Debugger.disable').catch(()=>{});ws.close()}}
})().catch(e=>{console.error(String(e));process.exitCode=1});
