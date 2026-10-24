// Limit optional background copies; interactive chat and persisted history stay native.
const fs=require('node:fs/promises');
const MAX_BYTES=1024**3;
exports.MAX_BYTES=MAX_BYTES;
exports.allow=async(client,threadId)=>{
 if(client?.hostConfig?.kind!=='local'||typeof client.readThread!=='function')return true;
 try{
  const value=await client.readThread(threadId,{includeTurns:false});
  const thread=value?.thread??value;
  if(typeof thread?.path!=='string'||!thread.path)return true;
  const info=await fs.stat(thread.path);
  return !info.isFile()||info.size<=MAX_BYTES;
 }catch{
  // Preserve upstream handling of absent/new/remote files and lookup failures.
  return true;
 }
};
