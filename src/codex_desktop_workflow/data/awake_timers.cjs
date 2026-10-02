const fs=require('fs');
const clock=process.env.CODEX_ACCEPTANCE_AWAKE_CLOCK;
if(!clock)throw Error('Acceptance awake clock is required');
function now(){
 const raw=fs.readFileSync(clock,'utf8');
 const end=raw.lastIndexOf('\n');
 if(end<0)throw Error('Invalid acceptance awake clock');
 const start=raw.lastIndexOf('\n',end-1)+1;
 const value=JSON.parse(raw.slice(start,end)).milliseconds;
 if(!Number.isFinite(value))throw Error('Invalid acceptance awake clock');
 return value;
}
function awakeTimeout(callback,milliseconds,...args){
 const deadline=now()+milliseconds;
 const timer=setInterval(()=>{if(now()>=deadline){clearInterval(timer);callback(...args)}},Math.min(100,Math.max(1,milliseconds)));
 return timer;
}
async function attachAwakeClock(send){
 const setup=`globalThis.__qualifiedAwakeNow=()=>globalThis.__qualifiedAwakeMilliseconds;globalThis.__qualifiedAwakeDelay=ms=>new Promise(resolve=>{const until=globalThis.__qualifiedAwakeNow()+ms;const id=setInterval(()=>{if(globalThis.__qualifiedAwakeNow()>=until){clearInterval(id);resolve()}},25)})`;
 await send('Runtime.evaluate',{expression:`globalThis.__qualifiedAwakeMilliseconds=${now()};${setup}`});
 let pending=false;
 const pulse=setInterval(async()=>{if(pending)return;pending=true;try{await send('Runtime.evaluate',{expression:`globalThis.__qualifiedAwakeMilliseconds=${now()}`})}finally{pending=false}},250);
 return()=>clearInterval(pulse);
}
module.exports={now,setTimeout:awakeTimeout,attachAwakeClock};
