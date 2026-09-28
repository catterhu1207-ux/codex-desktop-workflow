const fs=require('node:fs'),path=require('node:path');const {connect}=require('./cdp.cjs');
const sleep=ms=>new Promise(r=>setTimeout(r,ms)),assert=(v,m)=>{if(!v)throw Error(m)};
(async()=>{
 const mode=process.argv[2],out=process.env.RECENCY_OUTPUT,r=JSON.parse(fs.readFileSync(path.join(out,mode+'-run.json'))),c=await connect(r.debug_port);assert(r.synthetic_only,'Synthetic fixture required');
 const rowsExpr=`[...document.querySelectorAll('[data-app-action-sidebar-thread-row]')].map(e=>({id:e.getAttribute('data-app-action-sidebar-thread-id'),title:e.getAttribute('data-app-action-sidebar-thread-title'),pinned:e.getAttribute('data-app-action-sidebar-thread-pinned')}))`;
 const route=async id=>{for(let i=0;i<100;i++){await c.evaluate(`window.postMessage({type:'navigate-to-route',path:'/local/'+${JSON.stringify(id)}},'*');true`);if(await c.evaluate(`!!document.querySelector('[data-app-action-sidebar-thread-id="local:${id}"][data-app-action-sidebar-thread-selected="true"]')&&!!document.querySelector('[contenteditable=true][role=textbox]')`))return;await sleep(300)}throw Error('Selected composer missing')};
 const start=async(id,check)=>{await route(id);await sleep(1000);const before=await c.evaluate(rowsExpr);await c.evaluate(`window.__matrixEvents=[];window.addEventListener('message',e=>{let d=e.data;if(d?.type==='mcp-notification'&&['turn/started','turn/completed'].includes(d.method))window.__matrixEvents.push({at:performance.now(),thread:d.params.threadId,method:d.method})});document.querySelector('[contenteditable=true][role=textbox]').focus();true`);await c.call('Input.insertText',{text:'Synthetic local sidebar matrix task.'});await c.key('Enter','Enter',13);let after,started,visible;
 for(let i=0;i<200;i++){after=await c.evaluate(rowsExpr);started=(await c.evaluate('window.__matrixEvents')).find(e=>e.thread===id&&e.method==='turn/started');if(started&&check(before,after)){visible=await c.evaluate('performance.now()');break}await sleep(50)}assert(visible&&visible-started.at<2000,'Native start ordering failed');
 for(let i=0;i<160;i++){if((await c.evaluate('window.__matrixEvents')).some(e=>e.thread===id&&e.method==='turn/completed'))break;assert(i<159,'Completion missing');await sleep(500)}
 return {status:'passed',real_composer:true,start_to_visible_ms:visible-started.at,before,after};};
 const menu=async label=>{await c.evaluate(`(()=>{const b=[...document.querySelectorAll('button[aria-label]')].find(e=>new RegExp(${JSON.stringify(label)}).test(e.getAttribute('aria-label')));if(!b)throw Error('Native menu missing');b.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,button:0,pointerType:'mouse'}));return true})()`);await sleep(300)};
 const pick=async regex=>{await c.evaluate(`(()=>{const e=[...document.querySelectorAll('[role=menuitemradio],[role=menuitem]')].find(e=>new RegExp(${JSON.stringify(regex)}).test(e.innerText));if(!e)throw Error('Native item missing');e.click();return true})()`);await sleep(400)};
 const pinned=a=>a.filter(e=>e.pinned==='true').map(e=>e.id);
 const result={};try{
 const peer=r.group_peer;assert(peer,'Group peer metadata required');
 result.project_within=await start(peer,(before,after)=>after.find(e=>e.pinned!=='true')?.id==='local:'+peer);
 for(const t of r.fixtures.slice(1,3)){await c.evaluate(`(()=>{const row=document.querySelector('[data-app-action-sidebar-thread-id="local:${t.id}"]');if(!row)throw Error('Pin row missing');if(row.getAttribute('data-app-action-sidebar-thread-pinned')!=='true'){const b=[...row.querySelectorAll('button')].find(e=>/^(Pin chat|置顶聊天)$/.test(e.getAttribute('aria-label')||''));if(!b)throw Error('Pin action missing');b.click()}return true})()`);await sleep(600)}
 result.pinned_automatic=await start(r.fixtures[1].id,(before,after)=>pinned(after)[0]==='local:'+r.fixtures[1].id);
 await menu('^(Pinned options|置顶选项)$');await pick('^(Manual|Manual order|手动排序)$');
 result.pinned_manual=await start(r.fixtures[2].id,(before,after)=>pinned(before).join()===pinned(after).join());
 await menu('(Project sidebar options|项目侧边栏选项)');await c.evaluate(`[...document.querySelectorAll('[role=menuitem]')].find(e=>/^(Organize sidebar|整理侧边栏)$/.test(e.innerText)).focus();true`);await c.key('ArrowRight','ArrowRight',39);await sleep(300);await pick('^(Combined|Combine|合并显示)$');
 result.flat=await start(r.fixtures[0].id,(before,after)=>after.find(e=>e.pinned!=='true')?.id==='local:'+r.fixtures[0].id&&pinned(before).join()===pinned(after).join());
 await menu('(Chat sidebar options|聊天侧边栏选项)');await c.evaluate(`[...document.querySelectorAll('[role=menuitem]')].find(e=>/^(Organize sidebar|整理侧边栏)$/.test(e.innerText)).focus();true`);await c.key('ArrowRight','ArrowRight',39);await sleep(300);await pick('^(By project|分项目显示)$');
 fs.writeFileSync(path.join(out,mode+'-matrix.json'),JSON.stringify({status:'passed',cases:result},null,2));console.log('Native group, pinned automatic/manual and flat starts passed');
 }
 finally{c.close()}
})().catch(e=>{console.error(e);process.exit(1)});
