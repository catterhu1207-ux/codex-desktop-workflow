const fs=require('node:fs'),path=require('node:path');
const {connect}=require('./cdp.cjs');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const assert=(v,m)=>{if(!v)throw Error(m)};
(async()=>{
 const mode=process.argv[2],record=JSON.parse(fs.readFileSync(path.join(process.env.RECENCY_OUTPUT,mode+'-run.json'),'utf8'));
 assert(record.synthetic_only===true,'Owned fixture only');
 const c=await connect(record.debug_port);
 const orderExpr=`(()=>({projects:Array.from(document.querySelectorAll('button[aria-label]')).map(e=>e.getAttribute('aria-label')).filter(s=>/project actions$|的项目操作$/.test(s)),titles:Array.from(document.querySelectorAll('[data-app-action-sidebar-thread-title]')).map(e=>e.getAttribute('data-app-action-sidebar-thread-title')),text:document.body.innerText.slice(0,1200)}))()`;
 try{
  await c.evaluate(`window.postMessage(${JSON.stringify({type:'navigate-to-route',path:'/local/'+record.fixtures[0].id})},'*');true`);
  for(let i=0;i<180;i++){if(await c.evaluate(`!!(document.querySelector('[data-app-action-sidebar-thread-id="local:${record.fixtures[0].id}"][data-app-action-sidebar-thread-selected="true"]') && document.querySelector('[contenteditable=true][role=textbox]'))`))break;if(i===179)throw Error('Native composer not ready');if(i%10===0)await c.evaluate(`window.postMessage(${JSON.stringify({type:'navigate-to-route',path:'/local/'+record.fixtures[0].id})},'*');true`);await sleep(500)}
  await sleep(5000);
  await c.evaluate(`window.__recencyEvents=[];window.addEventListener('message',e=>{let d=e.data;if(d?.type==='mcp-notification'&&['turn/started','turn/completed'].includes(d.method))window.__recencyEvents.push({at:performance.now(),method:d.method,thread:d.params?.threadId,turn:d.params?.turn?.id,startedAt:d.params?.turn?.startedAt})});true`);
  const before=await c.evaluate(orderExpr);
  assert(!before.projects[0]?.startsWith('Project Alpha'),'Target must initially be older');
  await c.call('Page.bringToFront');
  await c.evaluate(`document.querySelector('[contenteditable=true][role=textbox]').focus();true`);
  await c.call('Input.insertText',{text:'Run the synthetic local recency acceptance task.'});
  await c.evaluate(`(()=>{let e=document.querySelector('[data-app-action-sidebar-thread-row]');while(e){if(e.scrollHeight>e.clientHeight+10&&/auto|scroll/.test(getComputedStyle(e).overflowY)){e.scrollTop=0;return true}e=e.parentElement}return false})()`);await sleep(350);
  const shotBefore=await c.call('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(process.env.RECENCY_OUTPUT,mode+'-before.png'),Buffer.from(shotBefore.data,'base64'));
  const submitAt=await c.evaluate('performance.now()');await c.key('Enter','Enter',13);
  let after,observedAt,events;
  for(let i=0;i<160;i++){
   after=await c.evaluate(orderExpr);events=await c.evaluate('window.__recencyEvents');
   if(after.projects[0]?.startsWith('Project Alpha')&&events.some(e=>e.method==='turn/started'&&e.thread===record.fixtures[0].id)){observedAt=await c.evaluate('performance.now()');break}
   await sleep(50);
  }
  assert(observedAt,'Real start event and project reorder missing');
  const started=events.find(e=>e.method==='turn/started'&&e.thread===record.fixtures[0].id);
  assert(observedAt-started.at<=2000,'Start-to-visible reorder exceeds two seconds');
  assert(after.text.indexOf('Recency target')<after.text.indexOf('Older waiting plan'),'Task must move forward too');
  const stable=[];
  for(let i=0;i<7;i++){await sleep(10000);let state=await c.evaluate(orderExpr);assert(state.projects[0]?.startsWith('Project Alpha'),'Streaming/completion changed project order');stable.push({at:await c.evaluate('performance.now()'),first:state.projects[0]})}
  const result={status:'passed',mode,run_id:record.run_id,backend:record.backend,thread_count:record.fixtures.length,before,after,submit_at:submitAt,start_event:started,visible_at:observedAt,start_to_visible_ms:observedAt-started.at,submission_to_visible_ms:observedAt-submitAt,events:await c.evaluate('window.__recencyEvents'),stable_observation_seconds:(stable.at(-1).at-observedAt)/1000,stable,real_composer:true,refresh_used:false};
  fs.writeFileSync(path.join(process.env.RECENCY_OUTPUT,mode+'-native-start.json'),JSON.stringify(result,null,2));
  const screenshot=await c.call('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(process.env.RECENCY_OUTPUT,mode+'-native-start.png'),Buffer.from(screenshot.data,'base64'));
  console.log(JSON.stringify({status:'passed',mode,start_to_visible_ms:result.start_to_visible_ms,observed:result.stable_observation_seconds}));
 }finally{c.close()}
})().catch(e=>{console.error(e);process.exit(1)});
