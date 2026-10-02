async function(spec){
 const setTimeout=(callback,ms,...args)=>globalThis.__qualifiedAwakeDelay(ms).then(()=>callback(...args));
 const original=this,host='ssh-isolated-windows-service',calls=[],ok=(v,m)=>{if(!v)throw Error(m)};
 const transport=new Proxy(original.requestClient,{get(target,key){if(key==='hostId')return host;if(key==='dispose')return()=>{};if(key==='sendRequest')return async(method,params,...rest)=>{calls.push({host,method,threadId:params?.threadId??null});return target.sendRequest(method,params,...rest)};const value=Reflect.get(target,key,target);return typeof value==='function'?value.bind(target):value}});
 const boundaryCalls=[];
 function trace(value,path){if(!value||typeof value!=='object')return value;return new Proxy(value,{get(target,key){const item=Reflect.get(target,key,target);if(typeof item==='function')return function(...args){const record={path:path+'.'+String(key),arguments:args.map(v=>typeof v==='string'||v===null?v:typeof v)};boundaryCalls.push(record);try{const result=item.apply(target,args);if(result&&typeof result.then==='function')return result.catch(error=>{record.error=String(error);throw error});return result}catch(error){record.error=String(error);throw error}};return item&&typeof item==='object'?trace(item,path+'.'+String(key)):item}})}
 const serviceBindings=[];
 const settings=new Proxy(original.settings,{get(target,key){
  if(key==='readDeveloperInstructions')return async(input,...rest)=>{ok(input.hostId===host,'Unexpected developer-instruction host');serviceBindings.push({operation:'readDeveloperInstructions',requested_host:host,isolated_service_host:'local',thread_id:input.threadId});return target.readDeveloperInstructions({...input,hostId:'local'},...rest)};
  if(key==='readCatalogEntry')return async(requested,id)=>{ok(requested===host,'Unexpected catalog host');serviceBindings.push({operation:'readCatalogEntry',requested_host:host,isolated_service_host:'local',thread_id:id});const row=await target.readCatalogEntry('local',id);return row==null?row:{...row,hostId:host}};
  const value=Reflect.get(target,key,target);return typeof value==='function'?value.bind(target):value;
 }});
 const remote=new original.constructor({...original,hostId:host,transport,threadExecution:null,runtime:trace(original.runtime,'runtime'),filesystem:trace(original.filesystem,'filesystem'),settings:trace(settings,'settings'),coordination:original.streamState.params.transport,threadProjectAssignments:original.threadWorkspaceStorage.threadProjectAssignments,savedReadState:original.readState,pendingThreadArchives:new Set()});
 const records=[];
 try{
  ok(remote.getHostId()===host&&remote.requestClient.hostId===host,'SSH host mismatch');
  const entries=spec.sent.filter(e=>e.entry==='native_SSH_manager');ok(entries.length===2,'Missing original SSH entries');
  for(const entry of entries){
   ok(entry.host===host,'Original SSH host differs');
   await remote.resumeConversation({conversationId:entry.id,model:null,reasoningEffort:null,workspaceRoots:[spec.workspace],collaborationMode:null});
   let row=remote.threadStore.getConversation(entry.id);const initialModel=row?.latestModel??null;let modelPolls=0;
   while(row?.latestModel!=='fixture-model'&&modelPolls<50){await new Promise(r=>setTimeout(r,100));row=remote.threadStore.getConversation(entry.id);modelPolls++}
   const response=await remote.readThread(entry.id,{includeTurns:true});
   ok(row?.id===entry.id&&row.latestModel==='fixture-model','Restored SSH identity/model mismatch '+JSON.stringify({id:entry.id,initialModel,latestModel:row?.latestModel,resumeState:row?.resumeState}));
   ok(response.thread.id===entry.id&&response.thread.cwd===spec.workspace,'SSH routing path changed');
   ok(JSON.stringify(response.thread.turns).includes('Synthetic native facade first send '+entry.index),'SSH sent content missing');
   ok(calls.some(c=>c.method==='thread/resume'&&c.threadId===entry.id),'Actual SSH resume path not called');
   records.push({id:entry.id,host,model:row.latestModel,initial_model:initialModel,model_notification_polls:modelPolls,content_verified:true,path_verified:true,resume_state:row.resumeState});
  }
  return{status:'passed',actual_native_remote_manager:true,ssh_service_simulated:true,encrypted_ssh_transport_tested:false,host_identity_preserved:true,records,calls,serviceBindings};
 }catch(error){throw Error(String(error)+'; external service diagnostics: '+JSON.stringify(boundaryCalls.slice(-35))+'; RPC calls: '+JSON.stringify(calls.slice(-20)))}finally{if(typeof remote[Symbol.dispose]==='function')remote[Symbol.dispose]()}
}
