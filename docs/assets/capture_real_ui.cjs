const fs=require('node:fs');
const path=require('node:path');
const pause=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const port=Number(process.env.ISOLATED_DEBUG_PORT);
 if(!Number.isInteger(port)||port<1024||port>65535)throw Error('Set an isolated loopback debug port');
 const mode=process.argv[4],lang=process.argv[5];
 if(!['start','updated'].includes(mode)||!['en','zh'].includes(lang))throw Error('Usage: capture_real_ui.cjs thread-list.json output-directory start|updated en|zh');
 const pages=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();
 const page=pages.find(p=>p.type==='page'&&p.url==='app://-/index.html');
 if(!page)throw Error('Primary renderer missing');
 const ws=new WebSocket(page.webSocketDebuggerUrl);let id=0;const pending=new Map();
 ws.onmessage=e=>{const r=JSON.parse(e.data);const p=pending.get(r.id);if(p){pending.delete(r.id);r.error?p.reject(Error(r.error.message)):p.resolve(r.result)}};
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 const call=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;const timer=setTimeout(()=>{pending.delete(n);reject(Error('CDP timeout'))},15000);pending.set(n,{resolve:r=>{clearTimeout(timer);resolve(r)},reject:e=>{clearTimeout(timer);reject(e)}});ws.send(JSON.stringify({id:n,method,params}))});
 const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result?.value};
 const crypto=require('node:crypto');const asar=process.env.CAPTURE_ASAR_PATH;if(!asar)throw Error('CAPTURE_ASAR_PATH is required');const hash=crypto.createHash('sha256').update(fs.readFileSync(asar)).digest('hex');const expected=mode==='start'?'0253e77e0d735dc314341157dd213476f6ced29e8a12ccb6d48a7dcc3a2e2781':'89fba67324ffb8dd54ccf13b6f097172e697549eeb1f26396f86f972c10c5b0c';if(hash!==expected&&!(mode==='start'&&hash==='b1f960d58c554b868681e4e35957ac81a3d2a8c6b1b180eef4d4a75233830e42'))throw Error('Unexpected source/build ASAR');await call('Page.bringToFront');
 const w=path.resolve(process.argv[3]);fs.mkdirSync(w,{recursive:true});const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
 const rows=Array.isArray(input)?input:input.data||input.result?.data;
 const threads={};for(const original of rows){const t=structuredClone(original);if(t.modelProvider!=='fixture'||!['Edit docs','Update API','Fix tests'].includes(t.preview))throw Error('Only the three approved synthetic tasks are allowed');t.recencyAt=mode==='updated'?t.updatedAt:t.createdAt;threads[t.preview]=t;}
 if(Object.keys(threads).length!==3)throw Error('Exactly three fictional tasks required');
 const visible=await evaluate(`JSON.stringify([...document.querySelectorAll('[data-app-action-sidebar-thread-row]')].map(e=>({id:e.getAttribute('data-app-action-sidebar-thread-id'),title:e.getAttribute('data-app-action-sidebar-thread-title')})))`);
 const mounted=JSON.parse(visible),expectedIds=Object.values(threads).map(t=>t.id);
 if(mounted.length!==3||mounted.some(t=>!expectedIds.some(id=>t.id===id||t.id.endsWith(':'+id))))throw Error('Renderer is not the isolated three-task fixture');
 const ui=await evaluate('document.body.innerText');
 if(lang==='zh'&&!ui.includes('新聊天')||lang==='en'&&!ui.includes('New chat'))throw Error('Select the requested UI language before capture');
 const emit=async(method,params,time)=>{
  if(method==='turn/started')params={...params,turn:{...params.turn,startedAt:Math.floor(Date.parse('2026-09-27T'+time+':00+08:00')/1000)}};
  // A controlled clock is restricted to this synthetic renderer and restored after dispatch.
  await evaluate(`window.__captureClockOriginal ??= Date.now;Date.now=()=>Date.parse(${JSON.stringify('2026-09-27T'+time+':00+08:00')});window.postMessage(${JSON.stringify({type:'mcp-notification',hostId:'local',method,params})},'*');true`);
  await pause(600);await evaluate('Date.now=window.__captureClockOriginal;true');
 };
 for(const t of Object.values(threads))await emit('thread/started',{thread:t},'09:00');
 for(const [name,action,time] of [['Edit docs','start','09:10'],['Update API','start','09:50'],['Update API','complete','09:55'],['Fix tests','start','10:00'],['Fix tests','complete','10:01'],['Edit docs','complete','10:05']]){
  const t=threads[name];if(!t)throw Error('Synthetic task absent: '+name);const turn='capture-'+name.replaceAll(' ','-');
  if(action==='start')await emit('turn/started',{threadId:t.id,turn:{id:turn,status:'inProgress',items:[],error:null}},time);
  else {const item={id:turn+'-item',type:name==='Update API'?'plan':'agentMessage',text:name==='Update API'?'Add a synthetic endpoint and verify its response.':'Synthetic task completed.'};if(item.type==='agentMessage')item.phase='final_answer';await emit('item/completed',{threadId:t.id,turnId:turn,item},time);await emit('turn/completed',{threadId:t.id,turn:{id:turn,status:'completed',items:[item],error:null,durationMs:3000}},time)}
 }
 if(mode==='start'&&/Recents|最近/.test(await evaluate('document.body.innerText')))await evaluate(`(()=>{const b=[...document.querySelectorAll('button')].find(b=>/^(View activity|查看活动)/.test(b.getAttribute('aria-label')||''));if(!b)throw Error('Activity control missing');b.click();return true})()`);
 await pause(700);
 const clip=process.env.CAPTURE_CLIP?JSON.parse(process.env.CAPTURE_CLIP):{x:50,y:43,width:278,height:365,scale:1};
 const snapshot=async name=>{await call('Input.dispatchMouseEvent',{type:'mouseMoved',x:900,y:380});await pause(600);const r=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false,clip});fs.writeFileSync(path.join(w,name+'.png'),Buffer.from(r.data,'base64'));console.log('Captured synthetic renderer:',name)};
 await snapshot((mode==='start'?'after-':'before-')+lang);
 if(mode==='start'&&process.argv[6]==='states'){
  const clickRow=async(title,button)=>{const expression=`(()=>{const row=document.querySelector('[data-app-action-sidebar-thread-title="'+${JSON.stringify(title)}+'"]');if(!row)throw Error('Native row missing');const target=${button?`[...row.querySelectorAll('button')].find(b=>/^(Pin chat|置顶聊天)$/.test(b.getAttribute('aria-label')||''))`:'row'};if(!target)throw Error('Native action missing');target.click();return true})()`;await evaluate(expression);await pause(800)};
  await clickRow('Update API');await snapshot('read-yellow-'+lang);
  await clickRow('Fix tests',true);await clickRow('Update API',true);await snapshot('pinned-'+lang);
  await evaluate(`(()=>{for(const b of document.querySelectorAll('button'))if(/^(Unpin chat|取消置顶聊天)$/.test(b.getAttribute('aria-label')||''))b.click();return true})()`);await pause(800);
  const docs=structuredClone(threads['Edit docs']);docs.recencyAt=Date.parse('2026-09-27T10:10:00+08:00')/1000;docs.updatedAt=docs.recencyAt;
  await emit('thread/started',{thread:docs},'10:10');
  await emit('turn/started',{threadId:docs.id,turn:{id:'capture-docs-new-start',status:'inProgress',items:[],error:null}},'10:10');
  await emit('thread/status/changed',{threadId:docs.id,status:{type:'active',activeFlags:[]}},'10:10');
  await snapshot('running-'+lang);
  const api=threads['Update API'],turn='capture-implementation',item={id:turn+'-item',type:'agentMessage',text:'Synthetic implementation completed.',phase:'final_answer'};
  await emit('turn/started',{threadId:api.id,turn:{id:turn,status:'inProgress',items:[],error:null}},'10:11');
  await emit('item/completed',{threadId:api.id,turnId:turn,item},'10:12');
  await emit('turn/completed',{threadId:api.id,turn:{id:turn,status:'completed',items:[item],error:null,durationMs:3000}},'10:12');
  await emit('thread/status/changed',{threadId:docs.id,status:{type:'idle'}},'10:12');
  await snapshot('cleared-'+lang);
 }
 ws.close();
})().catch(e=>{console.error(e);process.exit(1)});
