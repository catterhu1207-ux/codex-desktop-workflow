exports.connect=async function(port){
 const pages=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();
 const page=pages.find(p=>p.type==='page'&&p.url==='app://-/index.html');
 if(!page)throw Error('Owned primary renderer unavailable');
 const socket=new WebSocket(page.webSocketDebuggerUrl);let next=0;const pending=new Map();
 socket.onmessage=e=>{const r=JSON.parse(e.data);const p=pending.get(r.id);if(p){pending.delete(r.id);clearTimeout(p.timer);r.error?p.reject(Error(r.error.message)):p.resolve(r.result)}};
 await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject});
 const call=(method,params={})=>new Promise((resolve,reject)=>{let id=++next;const timer=setTimeout(()=>{pending.delete(id);reject(Error(`CDP timeout: ${method}`))},15000);pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params}))});
 const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result?.value};
 const key=async(key,code,vk)=>{await call('Input.dispatchKeyEvent',{type:'keyDown',key,code,windowsVirtualKeyCode:vk,nativeVirtualKeyCode:vk});await call('Input.dispatchKeyEvent',{type:'keyUp',key,code,windowsVirtualKeyCode:vk,nativeVirtualKeyCode:vk})};
 return {call,evaluate,key,close:()=>socket.close()};
};
