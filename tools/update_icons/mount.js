async function(stage){
 const native=this,shared=native.shared;shared.Pcn();const React=shared.ggn();
 const host=document.createElement('div');host.setAttribute('data-public-update-icon-probe',stage);document.body.append(host);
 const errors=[],root=shared.$fn().createRoot(host,{onUncaughtError:error=>errors.push(String(error))});
 const icons={published:'\u25f7',package_available:'\u2193',adaptation_ready:'\u2713'};
 try{
  root.render(React.createElement(native.updateComponent,{variant:'sidebarFooter'}));
  let button=null;
  for(let i=0;i<100&&!errors.length;i++){
   await new Promise(resolve=>setTimeout(resolve,100));
   button=host.querySelector('button[data-codex-update-stage]');
   if(button?.getAttribute('data-codex-update-stage')===stage)break;
  }
  if(errors.length||!button||button.getAttribute('data-codex-update-stage')!==stage)throw Error('Native update state failed: '+errors.join('|'));
  const label=button.textContent;
  root.render(React.createElement(native.updateComponent,{variant:'navigationRail'}));
  for(let i=0;i<100;i++){
   await new Promise(resolve=>setTimeout(resolve,100));
   button=host.querySelector('button[data-codex-update-stage]');
   if(button?.getAttribute('data-codex-update-stage')===stage&&button.querySelector('span[aria-hidden]'))break;
  }
  const expected=icons[stage];
  if(!button.textContent.includes(expected))throw Error('Native icon mismatch: '+stage+' '+button.textContent);
  if(!button.title&&!button.getAttribute('aria-label'))throw Error('Collapsed update explanation absent');
  return{status:'passed',stage,icon:expected,text:label,collapsed_text:button.textContent,title:button.title||button.getAttribute('aria-label')};
 }finally{root.unmount();host.remove()}
}
