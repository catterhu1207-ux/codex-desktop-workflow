const {now,setTimeout,attachAwakeClock}=require(process.env.CODEX_ACCEPTANCE_TIMER_MODULE);
const fs=require('fs');
(async()=>{
 const port=Number(process.env.ISOLATED_DEBUG_PORT),location=JSON.parse(fs.readFileSync(__dirname+'/sidebar-capture-location.json','utf8'));
 let target=null;const deadline=now()+60000;
 while(!target&&now()<deadline){try{target=(await(await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t=>t.type==='page'&&t.url==='app://-/index.html')}catch{}if(!target)await new Promise(r=>setTimeout(r,80))}
 if(!target)throw Error('Missing isolated primary page');
 const ws=new WebSocket(target.webSocketDebuggerUrl);let id=0,pending=new Map(),pause;
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 ws.onmessage=event=>{const value=JSON.parse(event.data);if(value.id){const p=pending.get(value.id);if(p){pending.delete(value.id);value.error?p.reject(Error(JSON.stringify(value.error))):p.resolve(value.result)}}else if(value.method==='Debugger.paused'&&pause)pause(value.params)};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const key=++id;pending.set(key,{resolve,reject});ws.send(JSON.stringify({id:key,method,params}));setTimeout(()=>{if(pending.delete(key))reject(Error('CDP deadline '+method))},30000).unref()});
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
  const result=await send('Runtime.callFunctionOn',{objectId:capture.result.objectId,functionDeclaration:fs.readFileSync(__dirname+(process.env.NATIVE_SIDEBAR_PROFILE==='faithful'?'/native_sidebar_function.js':'/native_sidebar_basic_function.js'),'utf8'),awaitPromise:true,returnByValue:true});
  if(result.exceptionDetails)throw Error(JSON.stringify(result.exceptionDetails));
  if(result.result?.value?.status!=='passed')throw Error(JSON.stringify(result));
  console.log(JSON.stringify(result.result.value));
 }finally{if(detachAwakeClock)detachAwakeClock();await send('Debugger.disable').catch(()=>{});ws.close()}
})().catch(e=>{console.error(String(e));process.exitCode=1});
