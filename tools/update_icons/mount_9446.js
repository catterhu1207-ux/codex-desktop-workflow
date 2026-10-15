async function(stage){
 const native=this,shared=native.shared;shared.ofn();const React=shared.PCn();
 const host=document.createElement('div');host.setAttribute('data-public-english-update-probe',stage);document.body.append(host);
 const errors=[],root=shared.Dgn().createRoot(host,{onUncaughtError:e=>errors.push(String(e))});
 const icons={published:'\u25f7',package_available:'\u2193',adaptation_ready:'\u2713'};
 const labels={published:'New version announced',package_available:'Official package available',adaptation_ready:'Adaptation ready'};
 try{
  root.render(React.createElement(native.updateComponent,{variant:'sidebarFooter'}));
  let button;
  for(let i=0;i<100&&!errors.length;i++){await new Promise(r=>setTimeout(r,100));button=host.querySelector('button[data-codex-update-stage]');if(button?.getAttribute('data-codex-update-stage')===stage)break}
  if(errors.length||!button||button.getAttribute('data-codex-update-stage')!==stage)throw Error('Actual update stage missing: '+stage+' '+errors.join('|'));
  const text=button.textContent,title=button.title||'',accessibleLabel=button.getAttribute('aria-label')||'';
  if(!text.includes(labels[stage])||/[\u4e00-\u9fff]/.test(text+title))throw Error('English update text mismatch: '+stage);
  root.render(React.createElement(native.updateComponent,{variant:'navigationRail'}));
  for(let i=0;i<100;i++){await new Promise(r=>setTimeout(r,100));button=host.querySelector('button[data-codex-update-stage]');if(button?.getAttribute('data-codex-update-stage')===stage&&button.querySelector('span[aria-hidden]'))break}
  const explanation=button.title||'',collapsedLabel=button.getAttribute('aria-label')||'';
  const descriptions={published:'The announced version is awaiting adaptation verification.',package_available:'Package version verified. Adaptation checks must pass before activation.',adaptation_ready:'Adaptation verified. The launcher will check again after this session exits.'};
  if(!button.textContent.includes(icons[stage])||!collapsedLabel.includes(labels[stage])||explanation!==descriptions[stage]||/[\u4e00-\u9fff]/.test(explanation+collapsedLabel))throw Error('English collapsed icon/explanation mismatch: '+JSON.stringify({stage,icon:button.textContent,explanation,collapsedLabel}));
  return{status:'passed',stage,icon:icons[stage],text,title,accessible_label:accessibleLabel,collapsed_text:button.textContent,explanation,collapsed_label:collapsedLabel,language:navigator.language};
 }finally{root.unmount();host.remove()}
}
