const fs=require('fs'),vm=require('vm'),assert=require('assert');
const Module=require('module'),payload=JSON.parse(fs.readFileSync(0,'utf8')),helpers=payload.helpers,raw=payload.entry;
const acornModule=new Module('acorn');acornModule._compile(process.binding('natives')['internal/deps/acorn/acorn/dist/acorn'],'acorn.js');
const names={CH:'CH',...payload.native_to_canonical},canonical=s=>s.replace(/[A-Za-z_$][\w$]*/g,n=>Object.hasOwn(names,n)?names[n]:n);
const ast=acornModule.exports.parse(raw,{ecmaVersion:'latest',sourceType:'module'}),wanted=new Set(['L3t','I3t','CH','F3t']),parts={};
function walk(n){if(!n||typeof n!=='object')return;if(n.type==='AssignmentExpression'&&n.left.type==='Identifier'&&wanted.has(names[n.left.name])){if(parts[names[n.left.name]])throw Error('ambiguous native idle member');parts[names[n.left.name]]=canonical(raw.slice(n.right.start,n.right.end))}for(const v of Object.values(n)){if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')walk(v)}}walk(ast);
assert.equal(Object.keys(parts).length,4,'native cache class and limits must be reachable');
const source=Object.entries(parts).filter(([k])=>k!=='L3t').map(([k,v])=>`const ${k}=${v};`).join('\n')+'\n'+Object.values(helpers).map(canonical).join('\n')+'\nconst BJn=new WeakMap();globalThis.canonicalize=e=>Xm(e,e.turns,true);globalThis.bodyCount=e=>SB(e).length;globalThis.IdleCache='+parts.L3t+';';
try{acornModule.exports.parse(source,{ecmaVersion:'latest'})}catch(e){throw Error('Native idle adapter syntax '+e.message+' context '+source.slice(e.pos-100,e.pos+100))}
function fixture(code=source,canonical=false){
 const context={};vm.runInNewContext(code,context);const rows=new Map,active=new Set,followers=new Set,roles=new Map,calls=[];
 const events=Object.fromEntries(['addConversationStateCallback','addStreamRoleStateCallback','addStreamFollowersChangedCallback','addNotificationCallback'].map(k=>[k,()=>()=>{}]));
 const params={events,now:()=>1000,logger:{debug(){},info(){},warning(){}},schedule:()=>()=>{},scheduleMicrotask:()=>{},parseUrl:()=>null,
 threadStore:{getConversation:id=>rows.get(id),isConversationActive:id=>active.has(id),updateConversationState:(id,fn)=>fn(rows.get(id)),removeConversationInterests(){}},
 streamState:{getStreamRole:id=>roles.get(id),ownsConversationHistoryStream:id=>roles.get(id)?.role==='owner',hasFollowersOrPendingFollowerReconnect:id=>followers.has(id),removeConversation:id=>roles.delete(id)},
 requestClient:{sendRequest:async(method,args)=>{assert.equal(method,'thread/unsubscribe');calls.push(args.threadId);return{status:'unsubscribed'}}},beforePassiveRelease:()=>{}};
 const cache=new context.IdleCache(params);
 function add(id,overrides={}){const row={id,title:id,resumeState:'resumed',rolloutPath:'synthetic/'+id,requests:[],turns:[{turnId:'turn-'+id,status:'completed',items:[{type:'agentMessage',text:'synthetic'}]}],threadRuntimeStatus:{type:'idle'},turnsPagination:{hasLoadedOldest:true},updatedAt:100,recencyAt:90,createdAt:10,latestModel:'thread-model',latestReasoningEffort:'medium',latestThreadSettings:{model:'thread-model',effort:'medium'},...overrides};rows.set(id,row);roles.set(id,{role:'owner'});cache.inactiveOwnerConversationSinceById.set(id,0);return row}
 const addOriginal=add;
 return {cache,params,add:(...args)=>{const row=addOriginal(...args);if(canonical){for(const turn of row.turns)for(const item of turn.items)if(item.type==='steeringUserMessage')item.targetTurnId=turn.turnId;context.canonicalize(row)}return row},rows,active,followers,roles,calls,bodyCount:context.bodyCount,canonicalize:context.canonicalize};
}
async function run(code=source,canonical=false){
 const f=fixture(code,canonical),{cache,add,active,followers}=f;
 const idle=add('idle'),current=add('current'),running=add('running',{threadRuntimeStatus:{type:'active'}}),streaming=add('streaming',{turns:[{turnId:'s',status:'inProgress',items:[]}]}),plan=add('plan',{turns:[{turnId:'p',status:'completed',items:[{type:'planImplementation',isCompleted:false}]}]}),approval=add('approval',{requests:[{method:'item/commandExecution/requestApproval',params:{turnId:'a'}}]}),pending=add('pending',{turns:[{turnId:'q',status:'completed',items:[{type:'steeringUserMessage',serverUserMessageId:null}]}]}),observed=add('observed');
 active.add('current');followers.add('observed');
 assert.equal(cache.shouldKeepConversationLoaded(plan),true,'pending plan must remain loaded');
 assert.equal(cache.shouldKeepConversationLoaded(approval),true,'approval must remain loaded');
 assert.deepEqual(Array.from(cache.getInactiveOwnerConversationIdsToUnsubscribe(1000)),['idle'],'only idle history may be unloaded');
 const blank=add('blank',{qZN:'blank',turns:[]});assert.equal(cache.shouldKeepConversationLoaded(blank),true,'new native blank page must remain loaded');cache.handleConversationStateChanged(blank);assert.equal(blank.qZN,'blank');blank.turns=[{turnId:'first-real-turn',status:'completed',items:[]}];if(canonical)f.canonicalize(blank);cache.handleConversationStateChanged(blank);assert.equal(blank.qZN,undefined,'real turn clears native new-page marker');
 const before=JSON.parse(JSON.stringify(idle));await cache.unsubscribeInactiveConversation('idle');
 assert.equal(f.bodyCount(idle),0);assert.equal(idle.resumeState,'needs_resume');assert.equal(idle.turnsPagination.hasLoadedOldest,false);assert.equal(idle.turnsPagination.olderCursor,null);
 if(canonical)assert.equal(idle.turnHistory.history.isComplete,false);
 for(const key of ['updatedAt','createdAt','recencyAt','title','id','latestModel','latestReasoningEffort','latestThreadSettings'])assert.deepEqual(idle[key],before[key],key+' changed');
 assert.deepEqual(f.calls,['idle']);assert.equal(f.roles.has('idle'),false);
 const snapshot=JSON.stringify([...f.rows]);await cache.unsubscribeInactiveConversation('current');await cache.unsubscribeInactiveConversation('running');await cache.unsubscribeInactiveConversation('plan');await cache.unsubscribeInactiveConversation('approval');assert.equal(JSON.stringify([...f.rows]),snapshot,'protected conversation modified');
 // A click while unsubscribe is in flight must protect the loaded body.
 const race=add('race');let release;f.params.requestClient.sendRequest=()=>new Promise(resolve=>release=resolve);
 const action=cache.unsubscribeInactiveConversation('race');active.add('race');release({status:'unsubscribed'});await action;assert.equal(f.bodyCount(race),1,'selected thread lost body during unsubscribe');
 return {metadata_and_all_sort_timestamps_preserved:true,thread_model_and_effort_preserved:true,current_view_preserved:true,running_and_streaming_preserved:true,real_pending_plan_preserved:true,approval_and_unsent_input_preserved:true,followers_preserved:true,pagination_marked_incomplete:true,click_race_body_preserved:true,only_idle_backend_unsubscribe:true};
}
(async()=>{
 const positive=await run(),canonical=await run(source,true);const negatives={};
 const native=fixture(),bridge={shared:{qZF(){},qZC:native.cache.constructor},Map,Set,JSON,Object};
 vm.runInNewContext(payload.renderer_helper+'\nglobalThis.checkRendererHelper=qualifyIdleCache;',bridge);
 const rendererHelper=await bridge.checkRendererHelper((v,m)=>assert(v,m));assert.equal(rendererHelper.released_idle_count,12);
 for(const [name,code]of [['old_ten_idle_cache',source.replace('const I3t=0;','const I3t=10;')],['pending_protection_removed',source.replace('e.qZN===e.id||e.requests.length>0||R0t(e,this.params.parseUrl)!=null?!0:','e.qZN===e.id?!0:')]]){
  assert.notEqual(code,source);try{await run(code);throw Error('accepted invalid mutation')}catch(e){if(e.message==='accepted invalid mutation')throw e;assert(e instanceof assert.AssertionError,e.stack);negatives[name]=String(e.message)}
 }
 const result={status:'passed',actual_packaged_class:true,actual_packaged_pending_selector:true,actual_canonical_history_setter:true,synthetic_manager_bindings:true,full_renderer_test:false,positive,canonical,rendererHelper,negatives};console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);process.exitCode=1});
