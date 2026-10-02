const {now,setTimeout,attachAwakeClock}=require(process.env.CODEX_ACCEPTANCE_TIMER_MODULE);
const fs=require('fs');
(async()=>{
 const port=Number(process.env.ISOLATED_DEBUG_PORT),location=JSON.parse(fs.readFileSync(__dirname+'/sidebar-capture-location.json','utf8'));
 let target=null;const deadline=now()+60000;
 while(!target&&now()<deadline){try{target=(await(await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t=>t.type==='page'&&t.url==='app://-/index.html')}catch{}if(!target)await new Promise(r=>setTimeout(r,80))}
 if(!target)throw Error('Missing isolated primary page');
 const keepAlive=setInterval(()=>{},1000);
 const ws=new WebSocket(target.webSocketDebuggerUrl);let id=0,pending=new Map(),pause;
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 ws.onmessage=event=>{const value=JSON.parse(event.data);if(value.id){const p=pending.get(value.id);if(p){pending.delete(value.id);value.error?p.reject(Error(JSON.stringify(value.error))):p.resolve(value.result)}}else if(value.method==='Debugger.paused'&&pause)pause(value.params)};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const key=++id;pending.set(key,{resolve,reject});ws.send(JSON.stringify({id:key,method,params}));setTimeout(()=>{if(pending.delete(key))reject(Error('CDP deadline '+method))},180000).unref()});
 let detachAwakeClock=null;
 try{
  await send('Debugger.enable');
  const {breakpointId}=await send('Debugger.setBreakpointByUrl',{url:location.url,lineNumber:location.line,columnNumber:location.column});
  const event=await Promise.race([new Promise(resolve=>pause=resolve),new Promise((_,reject)=>setTimeout(()=>reject(Error('Native proof closure capture deadline')),45000))]);
  const capture=await send('Debugger.evaluateOnCallFrame',{callFrameId:event.callFrames[0].callFrameId,expression:'({...x.native,shared})',returnByValue:false});
  if(capture.exceptionDetails||!capture.result?.objectId)throw Error('Native closure unavailable: '+JSON.stringify(capture));
  await send('Debugger.removeBreakpoint',{breakpointId});await send('Debugger.resume');
  detachAwakeClock=await attachAwakeClock(send);
  await new Promise(resolve=>setTimeout(resolve,6000));
  let nativeManager=null,captureError=null;
  const methodLocation=JSON.parse(fs.readFileSync(__dirname+'/worker-manager-capture-location.json','utf8'));
  const methodBreak=await send('Debugger.setBreakpointByUrl',{url:methodLocation.url,lineNumber:methodLocation.line,columnNumber:methodLocation.column});
  pause=async event=>{try{const value=await send('Debugger.evaluateOnCallFrame',{callFrameId:event.callFrames[0].callFrameId,expression:'this',returnByValue:false});nativeManager=value.result?.objectId;await send('Debugger.removeBreakpoint',{breakpointId:methodBreak.breakpointId})}catch(error){captureError=String(error)}finally{await send('Debugger.resume').catch(()=>{})}};
  const result=await send('Runtime.callFunctionOn',{objectId:capture.result.objectId,functionDeclaration:fs.readFileSync(__dirname+'/native_scope_lifecycle.js','utf8'),arguments:[{value:process.env.SYNTHETIC_WORKSPACE}],awaitPromise:true,returnByValue:true});
  if(result.exceptionDetails)throw Error(JSON.stringify(result.exceptionDetails));
  if(result.result?.value?.status!=='passed')throw Error(JSON.stringify(result));
  if(captureError)throw Error(captureError);
  if(nativeManager){const direct=await send('Runtime.callFunctionOn',{objectId:nativeManager,functionDeclaration:fs.readFileSync(__dirname+'/native_empty_negative.js','utf8'),arguments:[{value:process.env.SYNTHETIC_WORKSPACE}],awaitPromise:true,returnByValue:true});if(direct.exceptionDetails)throw Error(JSON.stringify(direct.exceptionDetails));result.result.value.native_empty_negative=direct.result.value}
  else throw Error('Actual native manager capture missing');
  const resolver=await send('Runtime.callFunctionOn',{objectId:nativeManager,functionDeclaration:fs.readFileSync(__dirname+'/native_host_resolution.js','utf8'),arguments:[{value:process.env.SYNTHETIC_WORKSPACE}],awaitPromise:true,returnByValue:true});if(resolver.exceptionDetails)throw Error(JSON.stringify(resolver.exceptionDetails));result.result.value.host_resolution=resolver.result.value;
  const remote=await send('Runtime.callFunctionOn',{objectId:nativeManager,functionDeclaration:fs.readFileSync(__dirname+'/native_ssh_lifecycle.js','utf8'),arguments:[{value:process.env.SYNTHETIC_WORKSPACE}],awaitPromise:true,returnByValue:true});if(remote.exceptionDetails)throw Error(JSON.stringify(remote.exceptionDetails));result.result.value.ssh_lifecycle=remote.result.value;result.result.value.sent.push(...remote.result.value.records);
  console.log(JSON.stringify(result.result.value));
 }finally{if(detachAwakeClock)detachAwakeClock();await send('Debugger.disable').catch(()=>{});ws.close();clearInterval(keepAlive)}
})().catch(e=>{console.error(String(e));process.exitCode=1});
