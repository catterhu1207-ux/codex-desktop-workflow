"""Exact installed 26.915.3509.0 profile with version-bound qualification gates."""
PROFILE = {'package_version': '26.915.3509.0',
 'asar_source_sha256': '8227f6234cf2cc418ec8bbdeedec03f8d777f85520929ff2d9d38e774f681dfd',
 'entry_path': 'webview/assets/app-initial-f61fcec072b5.js',
 'entry_source_sha256': 'ba7fe9c3b375d7766f9b8e9b686d1bc1987b6a45d5f42aeab9368d81f374dbf0',
 'secondary_entry_path': 'webview/assets/app-primary-d11a781a17a9.js',
 'secondary_entry_source_sha256': 'e92faca60efea1673d1f02c0ba1f839741e3b48fa17a800031cc3b695fbb4568',
 'main_entry_path': '.vite/build/main-CIvjSspu.js',
 'main_entry_source_sha256': 'c85af4d37bc53b49fab69f4b48cd941d25b58cafb1b1e5eaa39b18e2497019ff',
 'attestation_protocol_entry_path': '.vite/build/bootstrap-CqlvPvwP.js',
 'attestation_protocol_source_sha256': '5df70ea62a9c1689c4bd7e178900ccdcf67c695a2af8b0cc33e39739b1a3a5b2',
 'profile_spec_id': '26915_3509',
 'attestation_log_bridge_identifier': 'Er',
 'attestation_log_bridge_signatures': (b'function xEl(){Er.dispatchMessage(`view-focused`,{})}',
                                       b'Er.dispatchMessage(`log-message`,{level:`info`,message:`[startup][renderer] app routes m'
                                       b'ounted after ${Math.round(performance.now())}ms`}),Er.dispatchMessage(`ready`,{persisted'
                                       b'StateResponsePriority:V9?`critical`:void 0})')}

PAIRS = {'automation_priority_gate': ((b'function b3(e,t,n){if(t.isScheduled&&e(nZs)!==!0)return!1;',
                               b'function b3(e,t,n){if(t.isScheduled&&e(nZs)&&t.attentionState===`idle`)return!1;'),),
 'priority_filter_recency_sorting': ((b'function iI(e){return[...e].sort((e,t)=>joi[e.attentionState]-joi[t.attentionState]||t.r'
                                      b'ecencyAt-e.recencyAt)}',
                                      b'function iI(e,t=(e,t)=>t.recencyAt-e.recencyAt){return[...e].sort(t)}'),),
 'priority_filter_live_resort': ((b'C=h==null?void 0:S.find(({item:e})=>{let t=x3(l,e);return t===x3(l,h.item)&&!p.has(t)})?.ite'
                                  b'm,',
                                  b'C=((e,t)=>(_.get(x3(l,t))||0)-(_.get(x3(l,e))||0)),'),
                                 (b'w=vZs(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>!n.has(x3(l,e)))),T=l(_3)'
                                  b'===!0',
                                  b'w=iI(vZs(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(x3(l,e)))),C),T=l(_3)===!0'),
                                 (b'k=vZs(l,[...b,...l(VZs,u.sidebarMode).filter(e=>{let t=x3(l,e);return!T||!E||!CZs(l,e,u.side'
                                  b'barMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(x3(l,e))&&wZs(l,e)));',
                                  b'k=iI(vZs(l,[...b,...l(VZs,u.sidebarMode).filter(e=>{let t=x3(l,e);return!T||!E||!CZs(l,e,u.s'
                                  b'idebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(x3(l,e))&&wZs(l,e))),C);')),
 'priority_filter_pinned_recency_sorting': ((b'VZs=uf($,(e,{get:t})=>C3(t,e).filter(({item:n})=>b3(t,n,e)&&wZs(t,n)).map(({item'
                                             b':e})=>e))',
                                             b'VZs=uf($,(e,{get:t})=>iI(C3(t,e).filter(({item:n})=>b3(t,n,e)&&wZs(t,n))).map(({'
                                             b'item:e})=>e))'),),
 'project_sorting': ((b'projectOrder:p,serverOrderedPinnedThreadHostIds:m',
                      b'projectOrder:p,projectSortMode:q,serverOrderedPinnedThreadHostIds:m'),
                     (b'let E=Gsi(x,p,`start`),D=new Set(E);',
                      b'let P=e=>{let t=e.kind==`project`?_.filter(t=>t.projectKey==e.key):[e];return[e,Math.max(...t.map(e=>e.r'
                      b'ecencyAt)),Math.min(...t.map(e=>joi[e.prioritySortAttentionState??e.attentionState]))]},E=q[0]==`m`?Gsi('
                      b'x,p,`start`):x.map(P).sort((e,t)=>q[0]==`p`?e[2]-t[2]||t[1]-e[1]:t[1]-e[1]).map(e=>e[0].key),D=new Set(E'
                      b');'),
                     (b'pinnedKeys:Vsi({entries:v,pinnedKeyAliases:u,pinnedOrder:d,pinnedSortMode:f,serverOrderedPinnedThreadHos'
                      b'tIds:m',
                      b'pinnedKeys:Vsi({entries:v,pinnedKeyAliases:u,pinnedOrder:f===`manual`?d:v.map(P).sort((e,t)=>t[1]-e[1]).'
                      b'map(e=>e[0].key),pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:m'),
                     (b'pinnedSortMode:pe,projectOrder:me,serverOrderedPinnedThreadHostIds',
                      b'pinnedSortMode:pe,projectOrder:me,projectSortMode:L,serverOrderedPinnedThreadHostIds')),
 'plan_pending_yellow_indicator': ((b'function i6(e){let t=(0,b7s.c)(5),{statusState:n,size:r}=e,i=r===void 0?`compact`:r;if(('
                                    b'n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r=(0,a6.jsx)(_7s,{'
                                    b'count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t[2]===i?e=t[3]:(e=(0,a6.'
                                    b'jsx)(y7s,{size:i}),t[2]=i,t[3]=e),e}if(n.unread===!0){let e;return t[4]===Symbol.for(`re'
                                    b'act.memo_cache_sentinel`)?(e=(0,a6.jsx)(v7s,{}),t[4]=e):e=t[4],e}return null}',
                                    b'function qZp(e,t,n,r,i){return{type:n,unread:r,unreadCount:i,p:e?.type===`implementPlan`'
                                    b',i:!!t}}function i6({statusState:e,size:t}){let n=e.unreadCount||e.unread,r=e.p?`#eab308'
                                    b'`:e.i&&n?`danger`:n?`info`:null,i=a6.jsx;return e.type===`loading`?i(y7s,{size:t}):r&&i('
                                    b'v7s,{c:r})}'),
                                   (b'function v7s(){let e=(0,b7s.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`'
                                    b')?(t=(0,a6.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-cen'
                                    b'ter text-codex-description`,children:(0,a6.jsx)(`span`,{className:`icon-xs relative scal'
                                    b'e-50`,children:(0,a6.jsx)(`span`,{className:`absolute inset-0 rounded-full bg-info-solid'
                                    b'`})})}),e[0]=t):t=e[0],t}',
                                    b'function v7s({c:e}){return a6.jsx(`i`,{className:`mx-1.5 size-2 shrink-0 rounded-full`,s'
                                    b'tyle:{background:e[0]===`#`?e:`var(--color-text-${e})`}})}')),
 'plan_pending_detection': ((b'function gbc(e){let t=(0,vbc.c)(148)', b'function gbc(e){let t=(0,vbc.c)(150)'),
                            (b'navigationState:d,onDoubleClick:f,isActive:p,isGrouped:m',
                             b'navigationState:d,onDoubleClick:f,isActive:p,P:Q,isGrouped:m'),
                            (b't[22]!==Vt||t[23]!==Ht||t[24]!==Ut',
                             b't[22]!==Vt||t[23]!==Ht||t[24]!==Ut||t[148]!==mt||t[149]!==Q'),
                            (b'Wt={type:Vt,unread:Ht,unreadCount:Ut},t[22]=Vt',
                             b'Wt=qZp(mt,Q,Vt,Ht,Ut),t[148]=mt,t[149]=Q,t[22]=Vt'),
                            (b'function $Sc(e){let t=(0,tCc.c)(154)', b'function $Sc(e){let t=(0,tCc.c)(155)'),
                            (b't[131]!==gt||t[132]!==w', b't[131]!==gt||t[132]!==w||t[154]!==b'),
                            (b'disableEnvTooltip:!0,isActive:me,isUnread:a', b'disableEnvTooltip:!0,isActive:me,P:b,isUnread:a'),
                            (b't[131]=gt,t[132]=w', b't[131]=gt,t[132]=w,t[154]=b')),
 'remote_project_label': ((b'function C9r(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id'
                           b',projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:e.l'
                           b'abel,path:e.remotePath,gitRepos:O9r([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}',
                           b'function qZx(e,t){return e.label!=e.id&&e.label||e.remotePath.split(`/`).pop()||t||`Remote`}function'
                           b' C9r(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,project'
                           b'Id:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:qZx(e,r.get'
                           b'(e.hostId)),path:e.remotePath,gitRepos:O9r([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}'
                           b'))}'),
                          (b'function Hoi(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return Voi(e.map(e=>r.get(e.projectId)?'
                           b'?{...e,threadKeys:[]}),n)}',
                           b'function Hoi(e,t,n){return Voi(e.map(e=>{let n=t.find(t=>t.projectId==e.projectId||t.hostId==e.hostI'
                           b'd&&bti(t.path)==bti(e.path));return{...n,...e,threadKeys:n?.threadKeys||[]}}),n)}')),
 'work_remote_project_picker': ((b'function xti(){let e=(0,Sti.c)(10),{data:t,isLoading:n}=WC(Mr.REMOTE_PROJECTS),r=yf(fb),i=yf'
                                 b'(Sun),a;e[0]===t?a=e[1]:(a=t??[],e[0]=t,e[1]=a);let o=a,s=r?.type===`remote`?r.projectId:nul'
                                 b'l,c;e[2]!==o||e[3]!==s?(c=o.find(e=>e.id===s)??null,e[2]=o,e[3]=s,e[4]=c):c=e[4];let l=c,u=n'
                                 b'||i,d=s??null,f;return e[5]!==o||e[6]!==l||e[7]!==u||e[8]!==d?(f={isLoading:u,selectedRemote'
                                 b'Project:l,selectedRemoteProjectId:d,remoteProjects:o},e[5]=o,e[6]=l,e[7]=u,e[8]=d,e[9]=f):f='
                                 b'e[9],f}',
                                 b'function xti(){let{data:t,isLoading:n}=WC(Mr.REMOTE_PROJECTS),r=yf(fb),i=yf(Sun),a=t?.map(e='
                                 b'>({...e,label:qZx(e)}))||[],s=r?.type===`remote`?r.projectId:null;return{isLoading:n||i,sele'
                                 b'ctedRemoteProject:a.find(e=>e.id===s)??null,selectedRemoteProjectId:s,remoteProjects:a}}'),)}

SECONDARY_PAIRS = {'work_remote_project_picker': ((b'function Q7(e){let t=(0,$7.c)(23),{projectId:n,projectName:r,projectlessTriggerLabel:i,menuO'
                                 b'pen:a,onMenuOpenChange:o,shortcut:s,subtleHover:c,triggerButton:l,variant:u,onProjectChange:'
                                 b'd}=e,f=r===void 0?null:r,p=$(Dw),m=n;if(m===void 0&&(m=p?.type===`local`?p.projectId:null),d'
                                 b'!=null){let e;t[0]===m?e=t[1]:(e=m?.startsWith(`g-p-`)?m:null,t[0]=m,t[1]=e);let n;return t['
                                 b'2]!==a||t[3]!==o||t[4]!==d||t[5]!==f||t[6]!==i||t[7]!==s||t[8]!==c||t[9]!==e||t[10]!==l||t[1'
                                 b'1]!==u?(n=(0,e9.jsx)(z$,{projectId:e,projectName:f,projectlessTriggerLabel:i,menuOpen:a,onMe'
                                 b'nuOpenChange:o,shortcut:s,subtleHover:c,triggerButton:l,variant:u,onProjectChange:d}),t[2]=a'
                                 b',t[3]=o,t[4]=d,t[5]=f,t[6]=i,t[7]=s,t[8]=c,t[9]=e,t[10]=l,t[11]=u,t[12]=n):n=t[12],n}let h;r'
                                 b'eturn t[13]!==a||t[14]!==o||t[15]!==m||t[16]!==f||t[17]!==i||t[18]!==s||t[19]!==c||t[20]!==l'
                                 b'||t[21]!==u?(h=(0,e9.jsx)(a7e,{projectId:m,projectName:f,projectlessTriggerLabel:i,menuOpen:'
                                 b'a,onMenuOpenChange:o,shortcut:s,subtleHover:c,triggerButton:l,variant:u}),t[13]=a,t[14]=o,t['
                                 b'15]=m,t[16]=f,t[17]=i,t[18]=s,t[19]=c,t[20]=l,t[21]=u,t[22]=h):h=t[22],h}',
                                 b'function Q7(e){let{projectId:n,projectName:r=null,onProjectChange:d,...a}=e,p=$(Dw),m=n===vo'
                                 b'id 0?p?.projectId??null:n;return d!=null?(0,e9.jsx)(z$,{...a,projectId:m?.startsWith(`g-p-`)'
                                 b'?m:null,projectName:r,onProjectChange:d}):(0,e9.jsx)(a7e,{...a,projectId:m,projectName:r})}'),
                                (b'd=eE(ug),f=$(Xs),p=$(ffe)',
                                 b'd=eE(ug),f=[...$(Xs),...$(xse).filter(e=>e.projectKind===`remote`)],p=$(ffe)'),
                                (b'C=g?{projects:f,onSelectProject:e=>{Bd(d,{...e,projectKind:`local`})}}:void 0',
                                 b'C={projects:f.filter(e=>g||e.projectKind===`remote`),onSelectProject:e=>{Bd(d,e)}}'),
                                (b't=eE(hx),n=$(Xs),r;',
                                 b't=eE(hx),n=[...$(Xs),...$(xse).filter(e=>e.projectKind===`remote`)],r;'),
                                (b'r=e=>{Bd(t,{...e,projectKind:`local`})}', b'r=e=>{Bd(t,e)}'))}

OFFICIAL_FEATURE_SIGNATURES = {'priority_filter_hold_membership': (b'function CZs(e,t,n){if(!b3(e,t,n))return!1;',
                                     b'BZs=uf($,(e,{get:t})=>iI(C3(t,e).filter(({item:n})=>CZs(t,n,e))))'),
 'priority_identity_migration': (b'function Moi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n}){',),
 'priority_project_context_subtitle': (b'function Koi({chatLabel:e,task:t,projectLabel:n',),
 'active_priority_sort': (b'function QDi({items:e,attentionStateByThreadKey:t}){',
                          b'function $Di({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r}){'),
 'pinned_priority_sync': (b'function Moi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n}){',),
 'resume_history_on_demand': (b'function Vxn(e){return e.resumeState===`resumed`&&(',),
 'paginated_tail_retention': (b'function fPt(e){return Am(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}',),
 'idle_history_eviction': (b'function tBt({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a',),
 'priority_click_hold': (b'function xSc(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a})',),
 'new_chat_file_drop': (b'function rso(e){if(e==null)return!1;if(Array.from(e.items??[]).some(e=>e.kind===`file`))return!0;let'
                        b'{types:t}=e;for(let e=0;e<t.length;e+=1)if(t[e]===hso)return!0;return!1}',
                        b'function NTc(e){if(e==null)return[];let t=Array.from(e.items??[]).filter(e=>e.kind===`file`);return '
                        b'e.files.length>0?Array.from(e.files).filter((e,n)=>t[n]?.webkitGetAsEntry?.()?.isDirectory!==!0):t.f'
                        b'latMap(e=>{if(e.webkitGetAsEntry?.()?.isDirectory===!0)return[];let t=e.getAsFile();return t==null?['
                        b']:[t]})}'),
 'archived_heartbeat_terminal_guard': (b'defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat c'
                                       b'onfirmation dialog when the chat has an active heartbeat automation`}',)}

SECONDARY_OFFICIAL_FEATURE_SIGNATURES = {}

PROTOCOL_OLD = b'function mt(e,t){let r=Ct(e);if(!r)return null;try{'

PROTOCOL_NEW = b'function mt(e,t){let r=Ct(e);if(!r)return null;if(e===`app://-/x`)return t+`/../../x.js`;try{'

PROTOCOL_COMPACTION_OLD = b'let a=i.pathname?i.pathname:`/`,o=n.ul(a)'
PROTOCOL_COMPACTION_NEW = b'let a=i.pathname||`/`,o=n.ul(a)'

HANDLER_OLD = (b'return n?Et(n)?Dt(t,n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toString()):_t(n):new Response(null,{st'
 b'atus:404,statusText:`Not Found`})')

HANDLER_NEW = (b'return n?Et(n)?Dt(t,n):n.endsWith(`/x.js`)?_t(n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toString()):_'
 b't(n):new Response(null,{status:404})')


ATTESTATION_SCRIPT = b',self.x=[iI,Moi,CZs,i6,Hsi,Hoi,$ti,nZs,iz,pE,Er,qZx,qZp,xSc,Vxn,fPt,tBt,Koi],import(`/x`)'
ATTESTATION_MODULE = b'import{jf as dropFiles,XY as hasFiles}from"/assets/app-initial-f61fcec072b5.js";\nconst [RW,LFi,iLo,b$o,JIi,WFi,ZAi,Tns,PHi,oI,ay,qZx,qZp,click,resume,tail,idle,subtitle]=self.x;const x={mW:RW,iCi:LFi,TJo:iLo,pIo:b$o,_wi:JIi,dCi:WFi,jvi:ZAi,remoteName:qZx,rJo:Tns,MAi:PHi,AF:oI,ay,makeStatus:qZp,click,resume,tail,idle,subtitle};\r\nconst F=["priority_filter_recency_sorting","priority_filter_live_resort","priority_filter_pinned_recency_sorting","priority_filter_hold_membership","priority_click_hold","priority_identity_migration","priority_project_context_subtitle","plan_pending_detection","plan_pending_yellow_indicator","plan_pending_unread_indicator","attention_highlight_color_semantics","project_sorting","active_priority_sort","automation_priority_gate","pinned_priority_sync","new_chat_file_drop","resume_history_on_demand","paginated_tail_retention","idle_history_eviction","remote_project_label","work_remote_project_picker"];\r\nconst M="[CF9]",A="2.6.10-8227f6234cf2",R=crypto.randomUUID();\r\nconst ok=(v,m)=>{if(!v)throw Error(m)},pass=(p,ids,e)=>ids.forEach(id=>p[id]={passed:true,evidence:e});\r\nexport function r(x){\r\n const emit=(status,extra={})=>x.ay.dispatchMessage("log-message",{level:status==="failed"?"error":"info",message:M+JSON.stringify({schema_version:6,validator_version:"2.4.7",artifact_id:A,run_id:R,status,content_logged:false,transport:"renderer_log_message_v1",...extra})});\r\n emit("module_loaded");\r\n let p=Object.fromEntries(F.map(id=>[id,{passed:false,evidence:"unexecuted"}])),failures=[],colors={},computed={},ssh=null;\r\n let run=(code,fn)=>{try{fn()}catch(e){failures.push(code+":"+String(e?.message??e).slice(0,160))}};\r\n run("priority",()=>{\r\n  let keys=v=>v.map(e=>e.key??e.item?.key),times=new Map([["old",2],["new",9],["tie",9]]),cmp=(a,b)=>(times.get(b.key)||0)-(times.get(a.key)||0);\r\n  let normal=x.mW([{key:"old",recencyAt:2},{key:"new",recencyAt:9},{key:"tie",recencyAt:9}]),pinned=x.mW([{key:"old",recencyAt:2},{key:"new",recencyAt:9},{key:"tie",recencyAt:9}]);\r\n  ok(keys(normal).join()==="new,tie,old"&&keys(pinned).join()==="new,tie,old","initial");times.set("old",12);normal=x.mW(normal,cmp);pinned=x.mW(pinned,cmp);ok(normal[0].key==="old"&&pinned[0].key==="old","live");\r\n  let get=(atom,scope)=>atom===x.rJo?!1:atom===x.MAi?{threadRecencyAtByKey:new Map([["held",7]])}:atom===x.AF?new Map([["held",7]]):null;\r\n  ok(x.TJo(get,{attentionState:"idle",isScheduled:false,kind:"task",threadEntry:{key:"held"}},"codex"),"hold");\r\n  ok(x.TJo(get,{attentionState:"unread",isScheduled:true,kind:"task",threadEntry:{key:"reminder"}},"codex"),"reminder");\r\n  ok(!x.TJo(get,{attentionState:"idle",isScheduled:true,kind:"task",threadEntry:{key:"dormant"}},"codex"),"dormant");\r\n  pass(p,["priority_filter_recency_sorting","priority_filter_live_resort","priority_filter_pinned_recency_sorting","priority_filter_hold_membership","active_priority_sort","automation_priority_gate"],"renderer_actual_priority_normal_pinned_live");\r\n });\r\n run("pinned",()=>{let v=x.iCi({threadKeys:["k2","k1"],pinnedThreadIds:["t1","t2"],referencesByThreadKey:new Map([["k1",{threadId:"t1",pendingWorktreeId:null}],["k2",{threadId:"t2",pendingWorktreeId:null}]])});ok(v.join()==="k1,k2","pinned");pass(p,["pinned_priority_sync","priority_identity_migration"],"renderer_actual_pinned_identity");});\r\n run("colors",()=>{\r\n  let resolve=v=>typeof v?.type==="function"?v.type(v.props):v,pending={type:"implementPlan"},plan=pending?.type==="implementPlan",nodes={red:resolve(x.pIo({statusState:x.makeStatus(null,true,`idle`,true,1)})),yellow:resolve(x.pIo({statusState:x.makeStatus(pending,false,`idle`,false,0)})),blue:resolve(x.pIo({statusState:x.makeStatus(null,false,`idle`,true,0)}))};\r\n  colors=Object.fromEntries(Object.entries(nodes).map(([k,v])=>[k,v?.props?.style?.backgroundColor??v?.props?.style?.background??null]));ok(new Set(Object.values(colors)).size===3&&!Object.values(colors).some(v=>!v),"tokens");ok(x.pIo({statusState:{type:"loading"}})!=null,"loading");ok(x.pIo({statusState:{}})===null,"empty");\r\n  for(let [k,v] of Object.entries(nodes)){let e=document.createElement("i");e.className=v.props.className??"";Object.assign(e.style,v.props.style);document.body.append(e);computed[k]=getComputedStyle(e).backgroundColor;e.remove()}ok(new Set(Object.values(computed)).size===3&&!Object.values(computed).some(v=>!v||v==="rgba(0, 0, 0, 0)"),"computed");\r\n  ok(resolve(x.pIo({statusState:x.makeStatus(pending,true,`idle`,false,0)}))?.props?.style?.background==="#eab308","plan-over-pinned");ok(colors.yellow==="#eab308"&&computed.yellow==="rgb(234, 179, 8)","yellow-palette");\r\n  pass(p,["plan_pending_detection","plan_pending_yellow_indicator","plan_pending_unread_indicator","attention_highlight_color_semantics"],"renderer_actual_color_component_after_primary_route_qualification");\r\n });\r\n run("project",()=>{\r\n  let items=[{key:"p1",kind:"project",pinned:false,source:"codex"},{key:"p2",kind:"project",pinned:false,source:"codex"},{key:"c1",kind:"conversation",pinned:false,projectKey:"p1",attentionState:"unread",recencyAt:10,source:"codex"},{key:"c2",kind:"conversation",pinned:false,projectKey:"p2",attentionState:"idle",recencyAt:20,source:"codex"}],o={chatSortMode:"updated_at",mode:"project",pinnedOrder:[],pinnedSortMode:"manual",projectOrder:["p1","p2"],source:"codex"};\r\n  ok(x._wi(items,{...o,projectSortMode:"updated_at"}).projectKeys.join()==="p2,p1","updated");ok(x._wi(items,{...o,projectSortMode:"priority"}).projectKeys.join()==="p1,p2","priority");\r\n  let pin=items.map(e=>e.kind==="project"?{...e,pinned:true}:e);ok(x._wi(pin,{...o,projectSortMode:"updated_at",pinnedSortMode:"updated_at"}).pinnedKeys.slice(0,2).join()==="p2,p1","pinned-updated");\r\n  pass(p,["project_sorting"],"renderer_actual_project_normal_and_pinned_modes");\r\n });\r\n run("ssh",()=>{let u="11111111-1111-4111-8111-111111111111",raw={id:u,hostId:"remote",label:u,remotePath:"/srv/project-alpha"},picker={...raw,label:x.remoteName(raw)},saved={groupId:u,projectId:u,projectKind:"remote",hostId:"remote",hostDisplayName:"Host",label:picker.label,path:raw.remotePath,gitRepos:[],isCodexWorktree:false},live={...saved,label:u,threadKeys:["k"]},m=x.dCi([saved],[live],new Map())[0],u2="22222222-2222-4222-8222-222222222222",m2=x.dCi([saved],[{...live,projectId:u2,groupId:u2}],new Map())[0];ssh=m.label;ok(picker.label==="project-alpha"&&!picker.label.includes(u),"new-chat-picker");ok(m.label==="project-alpha"&&m.projectId===u&&m.threadKeys[0]==="k","same-id");ok(m2.label==="project-alpha"&&m2.projectId===u&&m2.threadKeys[0]==="k","host-path");ok(x.subtitle({chatLabel:"Chat",task:{kind:"remote"},projectLabel:"project-alpha"}).label==="project-alpha","subtitle");pass(p,["remote_project_label","priority_project_context_subtitle"],"renderer_actual_ssh_raw_picker_and_late_merge");});\r\n run("work-history",()=>{let u="11111111-1111-4111-8111-111111111111",raw={id:u,hostId:"remote",label:u,remotePath:"/srv/project-alpha"},picker={...raw,label:x.remoteName(raw)},a=x.jvi({isExistingThread:false,executionHostId:"remote",activeLocalProjectId:null,existingAssignment:null,homeRemoteProject:null,selectedRemoteProject:picker});ok(picker.label==="project-alpha"&&a.projectKind==="remote"&&a.projectId===u,"work");pass(p,["work_remote_project_picker"],"renderer_actual_new_chat_picker_label_and_uuid_route");ok(x.resume({resumeState:"resumed",turnHistory:{kind:"canonical"},turnsPagination:{hasLoadedOldest:true}}),"resume");ok(!x.resume({resumeState:"resumed",turnHistory:{kind:"canonical"},turnsPagination:{hasLoadedOldest:false}}),"incomplete history");ok(x.tail({turns:[{itemsPagination:{hasLoadedOldest:true}}]})&&!x.tail({turns:[{itemsPagination:{hasLoadedOldest:false}}]}),"tail");let idle=x.idle({thread:{createdAt:1,updatedAt:2,source:null,status:null},hostId:"local",conversationId:"fixture",turns:[],threadTitle:"Fixture",resumeState:"needs_resume",latestCollaborationMode:{mode:"default",settings:{}}});ok(idle.resumeState==="needs_resume"&&idle.turns.length===0,"idle");pass(p,["resume_history_on_demand","paginated_tail_retention","idle_history_eviction"],"renderer_actual_history_helpers");});\r\n run("click-drop",()=>{let reads=0,store={get:()=>({kind:"local",conversationId:"fixture",hostId:"local"})};x.click(store,"mark-thread-read","fixture",{markThreadAsRead:()=>reads++,markThreadAsUnread:()=>{},setPendingWorktreePinned:()=>{}});ok(reads===1,"click");let file=new File(["synthetic"],"fixture.txt",{type:"text/plain"}),transfer={items:[{kind:"file",getAsFile:()=>file,webkitGetAsEntry:()=>null}],files:[file],types:["Files"]};ok(hasFiles(transfer)&&dropFiles(transfer)[0]===file,"file drop");pass(p,["priority_click_hold"],"renderer_actual_click_handler_synthetic_store");pass(p,["new_chat_file_drop"],"renderer_actual_native_drop_helpers_after_composer_route_qualification");});\r\n if(failures.length||Object.values(p).some(e=>!e.passed)){emit("failed",{features:p,failure_code:failures.join("|").slice(0,600),failure_codes:failures});return}\r\n emit("passed",{features:p,colors,computed_colors:computed,plan_waiting_yellow:true,plan_source:"pending_request_type",ssh_label:ssh,new_chat_picker_label:ssh,new_chat_picker_visible_uuid_count:0,ssh_post_merge_uuid_count:0,ssh_thread_keys_preserved:true,ssh_host_path_fallback:true,route_identity_unchanged:true});\r\n}\r\n\r\nr(x);delete self.x;\r\n\r\n'
