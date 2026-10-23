const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const target=()=>path.join(process.env.CODEX_HOME,'.cache','codex-desktop-workflow','official-update-awareness.json');
let lastRefreshAttempt=0;
const refresh=()=>{
 const now=Date.now();if(now-lastRefreshAttempt<300000)return;
 const python=process.env.CODEX_WORKFLOW_PYTHON;
 if(!python||!process.env.CODEX_HOME)return;
 lastRefreshAttempt=now;
 const child=cp.spawn(python,['-B','-X','utf8','-m','codex_desktop_workflow.update_awareness','--mode','inspect','--output',target()],{stdio:'ignore',windowsHide:true});
 child.once('error',()=>{});child.unref();
};
exports.read=()=>{
 refresh();
 try{
  const file=target(),stat=fs.lstatSync(file);
  if(!stat.isFile()||stat.isSymbolicLink()||stat.size>65536)return{};
  const value=JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,'')),status=value.last_status;
  if(value.schema_version!==2||status?.schema_version!==2||status.content_logged!==false)return{};
  return{portableUpdateAwareness:status};
 }catch{return{}}
};
exports.show=()=>{
 const python=process.env.CODEX_WORKFLOW_PYTHON;if(!python||!process.env.CODEX_HOME)return;
 const child=cp.spawn(python,['-B','-X','utf8','-m','codex_desktop_workflow.update_awareness','--mode','show','--output',target()],{stdio:'ignore',windowsHide:true});
 child.once('error',()=>{});child.unref();
};
