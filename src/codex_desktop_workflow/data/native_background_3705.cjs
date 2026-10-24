const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
function environment(bytes,kind='local',unprotected=false){
 const calls={metadata:0,stat:0,resume:0,fork:0,fresh:0,generation:0,unsubscribe:0};
 const module={exports:{}};
 vm.runInNewContext(input.guard,{module,exports:module.exports,require:name=>{
  assert.equal(name,'node:fs/promises');return{stat:async()=>{calls.stat++;return{size:bytes,isFile:()=>true}}};
 }});
 const guard=unprotected?{allow:async()=>true}:module.exports;
 const client={options:{hostConfig:{kind}},appServerVersion:'synthetic',
  sendCatalogRequest:async(request)=>{assert.equal(request.method,'thread/read');assert.equal(request.params.includeTurns,false);calls.metadata++;return{result:{thread:{path:'C:/synthetic/history.jsonl'}}}},
  resumeThread:async()=>{calls.resume++;return{modelProvider:'fixture',model:'fixture',reasoningEffort:'high'}},
  forkThread:async()=>{calls.fork++;return{thread:{id:'synthetic-child'}}},
  startThread:async()=>{calls.fresh++;return{thread:{id:'synthetic-fresh'}}},
  unsubscribeThread:async()=>{calls.unsubscribe++}};
 const native=vm.runInNewContext('({'+input.native_read_thread+','+input.native_host_getter+'})',{d:require('node:crypto')});
 client.readThread=native.readThread;
 Object.defineProperty(client,'hostConfig',Object.getOwnPropertyDescriptor(native,'hostConfig'));
 const globals={require:name=>{assert.equal(name,'../../../g.cjs');return guard},performance,DOMException,
   jn:async()=>{calls.generation++;return{synthetic:true}}};
 return{calls,client,composer:vm.runInNewContext('('+input.composer+')',globals),
   generation:vm.runInNewContext('('+input.generation+')',globals)};
}
async function composer(context){return context.composer({client:context.client,threadId:'synthetic-source',latestTurnId:'synthetic-turn',
 generationTrigger:'synthetic',prompt:'Synthetic follow-up',signal:new AbortController().signal})}
async function generation(context){return context.generation({client:context.client,sourceThreadId:'synthetic-source',prompt:'Synthetic metadata',
 model:'fixture',cwd:null,effort:'high',timeoutMs:1000,responseSchema:{},fallbackToFreshThread:true,signal:new AbortController().signal})}
(async()=>{
 const states=[];
 for(const bytes of [0,1024**3,1024**3+1,6*1024**3]){
  let context=environment(bytes);await composer(context);
  assert.equal(context.calls.resume,bytes<=1024**3?1:0,'oversized composer resumed source history');
  assert.equal(context.calls.metadata,1);assert.equal(context.calls.stat,1);
  states.push({caller:'composer',bytes,...context.calls});
  context=environment(bytes);await generation(context);
  assert.equal(context.calls.fork,bytes<=1024**3?1:0,'oversized metadata forked source history');
  assert.equal(context.calls.fresh,0,'budget failure must not silently generate without source context');
  assert.equal(context.calls.generation,bytes<=1024**3?1:0);
  states.push({caller:'metadata',bytes,...context.calls});
 }
 const remote=environment(6*1024**3,'ssh');await generation(remote);
 assert.equal(remote.calls.metadata,0);assert.equal(remote.calls.stat,0);assert.equal(remote.calls.fork,1);
 const failed=environment(0);failed.client.readThread=async()=>{throw Error('synthetic lookup failure')};await generation(failed);
 assert.equal(failed.calls.fork,1,'native lookup/fallback behavior changed');
 const negatives=[];
 for(const [name,operation]of [['unprotected_composer_copy',composer],['unprotected_ephemeral_copy',generation]]){
  const context=environment(6*1024**3,'local',true);await operation(context);
  assert.throws(()=>assert.equal(context.calls.resume+context.calls.fork,0,'oversized background history reached a native copy'),
    /oversized background history reached a native copy/,'removing the budget must fail the same no-copy invariant');
  negatives.push(name);
 }
 const wrapped=environment(6*1024**3);
 wrapped.client.readThread=async()=>{wrapped.calls.metadata++;return{thread:{path:'C:/synthetic/history.jsonl'}}};
 await generation(wrapped);assert.equal(wrapped.calls.fork,0,'wrapped native metadata bypassed the budget');
 for(const name of ['composer','metadata']){
  const context=environment(0),controller=new AbortController();
  context.client.readThread=async()=>{controller.abort();return{path:'C:/synthetic/history.jsonl'}};
  try{
   if(name==='composer')await context.composer({client:context.client,threadId:'synthetic-source',latestTurnId:'synthetic-turn',prompt:'Synthetic',signal:controller.signal});
   else await context.generation({client:context.client,sourceThreadId:'synthetic-source',prompt:'Synthetic',model:'fixture',cwd:null,effort:'high',timeoutMs:1000,responseSchema:{},fallbackToFreshThread:true,signal:controller.signal});
  }catch(error){if(error.name!=='AbortError')throw error}
  assert.equal(context.calls.resume+context.calls.fork+context.calls.fresh+context.calls.generation,0,'aborted optional generation started work');
 }
 process.stdout.write(JSON.stringify({status:'passed',maximum_history_bytes:1024**3,states,
  negative_controls_rejected:negatives,remote_behavior_preserved:true,lookup_fallback_preserved:true,
  actual_packaged_functions:true,native_metadata_request_include_turns:false,native_host_config_getter:true,
  history_or_settings_written:false,model_requests_sent:false}));
})().catch(error=>{process.stderr.write(String(error.stack||error));process.exitCode=1});
