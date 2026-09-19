'Exact 26.915.4065.0 source gates and rebased accepted behavior.'

PROFILE = {'package_version': '26.915.4065.0',
 'asar_source_sha256': 'b8aeb817cd1ee6ef50efe8a97985d3be41de89688a5addfe0a444e1e52348096',
 'entry_path': 'webview/assets/app-initial-6c4523b43a11.js',
 'entry_source_sha256': '146b5204b30bd1766f19c0dd5b76f23515a77708ae80bb66ded6469e11431374',
 'secondary_entry_path': 'webview/assets/app-primary-355549b35da9.js',
 'secondary_entry_source_sha256': 'b2ba870a12454be5134b17f538b8caa3314ce5d7b9f0412b637168d3aa682a24',
 'main_entry_path': '.vite/build/main-LM8MUIFp.js',
 'main_entry_source_sha256': 'c71bf3ffecef5fd390b4cd16d120d39dce30d30bffe3c563c8c74c1b691da018',
 'attestation_protocol_entry_path': '.vite/build/bootstrap-DK4EfNwt.js',
 'attestation_protocol_source_sha256': 'dbdbdd3ef5dde93dd196a59846edf244dc653341213e0fd45eebb133b5df10ba',
 'profile_spec_id': '26915_4065',
 'attestation_log_bridge_identifier': 'Dr',
 'attestation_log_bridge_signatures': (b'function GTl(){Dr.dispatchMessage(`view-focused`,{})}',
                                       b'Dr.dispatchMessage(`log-message`,{level:`info`,message:`[startup][renderer] '
                                       b'app routes mounted after ${Math.round(performance.now())}ms`}),Dr.dispatchMe'
                                       b'ssage(`ready`,{persistedStateResponsePriority:B9?`critical`:void 0})')}

PAIRS = {'automation_priority_gate': ((b'function aZs(e,t,n){if(t.isScheduled&&e(LXs)!==!0)return!1;',
                               b'function aZs(e,t,n){if(t.isScheduled&&e(LXs)&&t.attentionState===`idle`)return!1;'),),
 'priority_filter_recency_sorting': ((b'function rI(e){return[...e].sort((e,t)=>Noi[e.attentionState]-Noi[t.attentio'
                                      b'nState]||t.recencyAt-e.recencyAt)}',
                                      b'function rI(e,t=(e,t)=>t.recencyAt-e.recencyAt){return[...e].sort(t)}'),),
 'priority_filter_live_resort': ((b'C=h==null?void 0:S.find(({item:e})=>{let t=B3(l,e);return t===B3(l,h.item)&&!p.h'
                                  b'as(t)})?.item,',
                                  b'C=((e,t)=>(_.get(B3(l,t))||0)-(_.get(B3(l,e))||0)),'),
                                 (b'w=$Xs(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>!n.has(B3(l,e'
                                  b')))),T=l(L3)===!0',
                                  b'w=rI($Xs(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(B3(l,e)))),C),T=l(L3)'
                                  b'===!0'),
                                 (b'k=$Xs(l,[...b,...l(wZs,u.sidebarMode).filter(e=>{let t=B3(l,e);return!T||!E||!iZ'
                                  b's(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(B3(l,e))&&oZs(l,e)'
                                  b'));',
                                  b'k=rI($Xs(l,[...b,...l(wZs,u.sidebarMode).filter(e=>{let t=B3(l,e);return!T||!E||'
                                  b'!iZs(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(B3(l,e))&&oZs(l'
                                  b',e))),C);')),
 'priority_filter_pinned_recency_sorting': ((b'wZs=uf($,(e,{get:t})=>V3(t,e).filter(({item:n})=>aZs(t,n,e)&&oZs(t,n)).m'
                                             b'ap(({item:e})=>e))',
                                             b'wZs=uf($,(e,{get:t})=>rI(V3(t,e).filter(({item:n})=>aZs(t,n,e)&&oZs(t,n)'
                                             b')).map(({item:e})=>e))'),),
 'project_sorting': ((b'projectOrder:p,serverOrderedPinnedThreadHostIds:m',
                      b'projectOrder:p,projectSortMode:q,serverOrderedPinnedThreadHostIds:m'),
                     (b'let E=qsi(x,p,`start`),D=new Set(E);',
                      b'let P=e=>{let t=e.kind==`project`?_.filter(t=>t.projectKey==e.key):[e];return[e,Math.max(...'
                      b't.map(e=>e.recencyAt)),Math.min(...t.map(e=>Noi[e.prioritySortAttentionState??e.attentionSta'
                      b'te]))]},E=q[0]==`m`?qsi(x,p,`start`):x.map(P).sort((e,t)=>q[0]==`p`?e[2]-t[2]||t[1]-e[1]:t[1'
                      b']-e[1]).map(e=>e[0].key),D=new Set(E);'),
                     (b'pinnedKeys:Usi({entries:v,pinnedKeyAliases:u,pinnedOrder:d,pinnedSortMode:f,serverOrderedPin'
                      b'nedThreadHostIds:m',
                      b'pinnedKeys:Usi({entries:v,pinnedKeyAliases:u,pinnedOrder:f===`manual`?d:v.map(P).sort((e,t)='
                      b'>t[1]-e[1]).map(e=>e[0].key),pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:m'),
                     (b'pinnedSortMode:pe,projectOrder:me,serverOrderedPinnedThreadHostIds',
                      b'pinnedSortMode:pe,projectOrder:me,projectSortMode:L,serverOrderedPinnedThreadHostIds')),
 'plan_pending_yellow_indicator': ((b'function m6(e){let t=(0,d7s.c)(5),{statusState:n,size:r}=e,i=r===void 0?`compact'
                                    b'`:r;if((n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r='
                                    b'(0,h6.jsx)(c7s,{count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t'
                                    b'[2]===i?e=t[3]:(e=(0,h6.jsx)(u7s,{size:i}),t[2]=i,t[3]=e),e}if(n.unread===!0){le'
                                    b't e;return t[4]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,h6.jsx)(l7s,{}),'
                                    b't[4]=e):e=t[4],e}return null}',
                                    b'function qZp(e,t,n,r,i){return{type:n,unread:r,unreadCount:i,p:e?.type===`implem'
                                    b'entPlan`,i:!!t}}function m6({statusState:e,size:t}){let n=e.unreadCount||e.unrea'
                                    b'd,r=e.p?`#eab308`:e.i&&n?`danger`:n?`info`:null,i=h6.jsx;return e.type===`loadin'
                                    b'g`?i(u7s,{size:t}):r&&i(l7s,{c:r})}'),
                                   (b'function l7s(){let e=(0,d7s.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_s'
                                    b'entinel`)?(t=(0,h6.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-ce'
                                    b'nter justify-center text-codex-description`,children:(0,h6.jsx)(`span`,{classNam'
                                    b'e:`icon-xs relative scale-50`,children:(0,h6.jsx)(`span`,{className:`absolute in'
                                    b'set-0 rounded-full bg-info-solid`})})}),e[0]=t):t=e[0],t}',
                                    b'function l7s({c:e}){return h6.jsx(`i`,{className:`mx-1.5 size-2 shrink-0 rounded'
                                    b'-full`,style:{background:e[0]===`#`?e:`var(--color-text-${e})`}})}')),
 'plan_pending_detection': ((b'function hbc(e){let t=(0,_bc.c)(148)', b'function hbc(e){let t=(0,_bc.c)(150)'),
                            (b'navigationState:d,onDoubleClick:f,isActive:p,isGrouped:m',
                             b'navigationState:d,onDoubleClick:f,isActive:p,P:Q,isGrouped:m'),
                            (b't[22]!==Vt||t[23]!==Ht||t[24]!==Ut',
                             b't[22]!==Vt||t[23]!==Ht||t[24]!==Ut||t[148]!==mt||t[149]!==Q'),
                            (b'Wt={type:Vt,unread:Ht,unreadCount:Ut},t[22]=Vt',
                             b'Wt=qZp(mt,Q,Vt,Ht,Ut),t[148]=mt,t[149]=Q,t[22]=Vt'),
                            (b'function QSc(e){let t=(0,eCc.c)(154)', b'function QSc(e){let t=(0,eCc.c)(155)'),
                            (b't[131]!==gt||t[132]!==w', b't[131]!==gt||t[132]!==w||t[154]!==b'),
                            (b'disableEnvTooltip:!0,isActive:me,isUnread:a',
                             b'disableEnvTooltip:!0,isActive:me,P:b,isUnread:a'),
                            (b't[131]=gt,t[132]=w', b't[131]=gt,t[132]=w,t[154]=b')),
 'remote_project_label': ((b'function T9r(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({'
                           b'groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e'
                           b'.hostId)??null,label:e.label,path:e.remotePath,gitRepos:A9r([e.remotePath],n?.[e.hostId]'
                           b'??[]),isCodexWorktree:!1}))}',
                           b'function qZx(e,t){return e.label!=e.id&&e.label||e.remotePath.split(`/`).pop()||t||`Remo'
                           b'te`}function T9r(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e'
                           b'=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.g'
                           b'et(e.hostId)??null,label:qZx(e,r.get(e.hostId)),path:e.remotePath,gitRepos:A9r([e.remote'
                           b'Path],n?.[e.hostId]??[]),isCodexWorktree:!1}))}'),
                          (b'function Woi(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return Uoi(e.map(e=>r.get(e'
                           b'.projectId)??{...e,threadKeys:[]}),n)}',
                           b'function Woi(e,t,n){return Uoi(e.map(e=>{let n=t.find(t=>t.projectId==e.projectId||t.hos'
                           b'tId==e.hostId&&Sti(t.path)==Sti(e.path));return{...n,...e,threadKeys:n?.threadKeys||[]}}'
                           b'),n)}')),
 'work_remote_project_picker': ((b'function Cti(){let e=(0,wti.c)(10),{data:t,isLoading:n}=KC(Nr.REMOTE_PROJECTS),r=vf('
                                 b'hb),i=vf(yun),a;e[0]===t?a=e[1]:(a=t??[],e[0]=t,e[1]=a);let o=a,s=r?.type===`remote`'
                                 b'?r.projectId:null,c;e[2]!==o||e[3]!==s?(c=o.find(e=>e.id===s)??null,e[2]=o,e[3]=s,e['
                                 b'4]=c):c=e[4];let l=c,u=n||i,d=s??null,f;return e[5]!==o||e[6]!==l||e[7]!==u||e[8]!=='
                                 b'd?(f={isLoading:u,selectedRemoteProject:l,selectedRemoteProjectId:d,remoteProjects:o'
                                 b'},e[5]=o,e[6]=l,e[7]=u,e[8]=d,e[9]=f):f=e[9],f}',
                                 b'function Cti(){let{data:t,isLoading:n}=KC(Nr.REMOTE_PROJECTS),r=vf(hb),i=vf(yun),a=t'
                                 b'?.map(e=>({...e,label:qZx(e)}))||[],s=r?.type===`remote`?r.projectId:null;return{isL'
                                 b'oading:n||i,selectedRemoteProject:a.find(e=>e.id===s)??null,selectedRemoteProjectId:'
                                 b's,remoteProjects:a}}'),)}

SECONDARY_PAIRS = {'work_remote_project_picker': ((b'function $7(e){let t=(0,e9.c)(23),{projectId:n,projectName:r,projectlessTriggerLabel'
                                 b':i,menuOpen:a,onMenuOpenChange:o,shortcut:s,subtleHover:c,triggerButton:l,variant:u,'
                                 b'onProjectChange:d}=e,f=r===void 0?null:r,p=$(kC),m=n;if(m===void 0&&(m=p?.type===`lo'
                                 b'cal`?p.projectId:null),d!=null){let e;t[0]===m?e=t[1]:(e=m?.startsWith(`g-p-`)?m:nul'
                                 b'l,t[0]=m,t[1]=e);let n;return t[2]!==a||t[3]!==o||t[4]!==d||t[5]!==f||t[6]!==i||t[7]'
                                 b'!==s||t[8]!==c||t[9]!==e||t[10]!==l||t[11]!==u?(n=(0,t9.jsx)(B$,{projectId:e,project'
                                 b'Name:f,projectlessTriggerLabel:i,menuOpen:a,onMenuOpenChange:o,shortcut:s,subtleHove'
                                 b'r:c,triggerButton:l,variant:u,onProjectChange:d}),t[2]=a,t[3]=o,t[4]=d,t[5]=f,t[6]=i'
                                 b',t[7]=s,t[8]=c,t[9]=e,t[10]=l,t[11]=u,t[12]=n):n=t[12],n}let h;return t[13]!==a||t[1'
                                 b'4]!==o||t[15]!==m||t[16]!==f||t[17]!==i||t[18]!==s||t[19]!==c||t[20]!==l||t[21]!==u?'
                                 b'(h=(0,t9.jsx)(i7e,{projectId:m,projectName:f,projectlessTriggerLabel:i,menuOpen:a,on'
                                 b'MenuOpenChange:o,shortcut:s,subtleHover:c,triggerButton:l,variant:u}),t[13]=a,t[14]='
                                 b'o,t[15]=m,t[16]=f,t[17]=i,t[18]=s,t[19]=c,t[20]=l,t[21]=u,t[22]=h):h=t[22],h}',
                                 b'function $7(e){let{projectId:n,projectName:r=null,onProjectChange:d,...a}=e,p=$(kC),'
                                 b'm=n===void 0?p?.projectId??null:n;return d!=null?(0,t9.jsx)(B$,{...a,projectId:m?.st'
                                 b'artsWith(`g-p-`)?m:null,projectName:r,onProjectChange:d}):(0,t9.jsx)(i7e,{...a,proje'
                                 b'ctId:m,projectName:r})}'),
                                (b'd=Vx(ys),f=$(xy),p=$(Pde)',
                                 b'd=Vx(ys),f=[...$(xy),...$(eve).filter(e=>e.projectKind===`remote`)],p=$(Pde)'),
                                (b'C=g?{projects:f,onSelectProject:e=>{jm(d,{...e,projectKind:`local`})}}:void 0',
                                 b'C={projects:f.filter(e=>g||e.projectKind===`remote`),onSelectProject:e=>{jm(d,e)}}'),
                                (b't=Vx(Rd),n=$(xy),r;',
                                 b't=Vx(Rd),n=[...$(xy),...$(eve).filter(e=>e.projectKind===`remote`)],r;'),
                                (b'r=e=>{jm(t,{...e,projectKind:`local`})}', b'r=e=>{jm(t,e)}'))}

OFFICIAL_FEATURE_SIGNATURES = {'priority_filter_hold_membership': (b'function iZs(e,t,n){if(!aZs(e,t,n))return!1;',
                                     b'CZs=uf($,(e,{get:t})=>rI(V3(t,e).filter(({item:n})=>iZs(t,n,e))))'),
 'priority_identity_migration': (b'function Poi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n}){',),
 'priority_project_context_subtitle': (b'function Joi({chatLabel:e,task:t,projectLabel:n',),
 'active_priority_sort': (b'function eOi({items:e,attentionStateByThreadKey:t}){',
                          b'function tOi({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r}){'),
 'pinned_priority_sync': (b'function Poi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n}){',),
 'resume_history_on_demand': (b'function Rxn(e){return e.resumeState===`resumed`&&(',),
 'paginated_tail_retention': (b'function fPt(e){return Am(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}',),
 'idle_history_eviction': (b'function oBt({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a',),
 'priority_click_hold': (b'function bSc(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a})',),
 'new_chat_file_drop': (b'function Poo(e){if(e==null)return!1;if(Array.from(e.items??[]).some(e=>e.kind===`file`))retu'
                        b'rn!0;let{types:t}=e;for(let e=0;e<t.length;e+=1)if(t[e]===Koo)return!0;return!1}',
                        b'function MTc(e){if(e==null)return[];let t=Array.from(e.items??[]).filter(e=>e.kind===`file`)'
                        b';return e.files.length>0?Array.from(e.files).filter((e,n)=>t[n]?.webkitGetAsEntry?.()?.isDir'
                        b'ectory!==!0):t.flatMap(e=>{if(e.webkitGetAsEntry?.()?.isDirectory===!0)return[];let t=e.getA'
                        b'sFile();return t==null?[]:[t]})}'),
 'archived_heartbeat_terminal_guard': (b'defaultMessage:`Archive and remove`,description:`Confirm button label for ar'
                                       b'chive chat confirmation dialog when the chat has an active heartbeat automat'
                                       b'ion`}',)}

SECONDARY_OFFICIAL_FEATURE_SIGNATURES = {}

ATTESTATION_SCRIPT = b',self.x=[rI,Poi,iZs,m6,Wsi,Woi,tni,LXs,rz,uE,Dr,qZx,qZp,bSc,Rxn,fPt,oBt,Joi],import(`/x`)'

PROTOCOL_OLD = b'function mt(e,t){let r=Ct(e);if(!r)return null;try{'

PROTOCOL_NEW = b'function mt(e,t){let r=Ct(e);if(!r)return null;if(e===`app://-/x`)return t+`/../../x.js`;try{'

PROTOCOL_COMPACTION_OLD = b'let a=i.pathname?i.pathname:`/`,o=n.ll(a)'

PROTOCOL_COMPACTION_NEW = b'let a=i.pathname||`/`,o=n.ll(a)'

HANDLER_OLD = (b'return n?Et(n)?Dt(t,n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toString()):_t(n):new Response('
 b'null,{status:404,statusText:`Not Found`})')

HANDLER_NEW = (b'return n?Et(n)?Dt(t,n):n.endsWith(`/x.js`)?_t(n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toStr'
 b'ing()):_t(n):new Response(null,{status:404})')

ATTESTATION_MODULE = (b'import{yf as dropFiles,RY as hasFiles}from"/assets/app-initial-6c4523b43a11.js";\nconst [RW,LFi,iLo,b$o,JIi,WFi,Z'
 b'Ai,Tns,PHi,oI,ay,qZx,qZp,click,resume,tail,idle,subtitle]=self.x;const x={mW:RW,iCi:LFi,TJo:iLo,pIo:b$o,_wi:JIi,dCi:'
 b'WFi,jvi:ZAi,remoteName:qZx,rJo:Tns,MAi:PHi,AF:oI,ay,makeStatus:qZp,click,resume,tail,idle,subtitle};\r\nconst F=["'
 b'priority_filter_recency_sorting","priority_filter_live_resort","priority_filter_pinned_recency_sorting","priority_fi'
 b'lter_hold_membership","priority_click_hold","priority_identity_migration","priority_project_context_subtitle","plan_'
 b'pending_detection","plan_pending_yellow_indicator","plan_pending_unread_indicator","attention_highlight_color_semant'
 b'ics","project_sorting","active_priority_sort","automation_priority_gate","pinned_priority_sync","new_chat_file_drop"'
 b',"resume_history_on_demand","paginated_tail_retention","idle_history_eviction","remote_project_label","work_remote_p'
 b'roject_picker"];\r\nconst M="[CF9]",A="2.6.11-b8aeb817cd1e",R=crypto.randomUUID();\r\nconst ok=(v,m)=>{if(!v)throw E'
 b'rror(m)},pass=(p,ids,e)=>ids.forEach(id=>p[id]={passed:true,evidence:e});\r\nexport function r(x){\r\n const emit=(s'
 b'tatus,extra={})=>x.ay.dispatchMessage("log-message",{level:status==="failed"?"error":"info",message:M+JSON.stringify'
 b'({schema_version:6,validator_version:"2.4.8",artifact_id:A,run_id:R,status,content_logged:false,transport:"renderer_'
 b'log_message_v1",...extra})});\r\n emit("module_loaded");\r\n let p=Object.fromEntries(F.map(id=>[id,{passed:false,ev'
 b'idence:"unexecuted"}])),failures=[],colors={},computed={},ssh=null;\r\n let run=(code,fn)=>{try{fn()}catch(e){fail'
 b'ures.push(code+":"+String(e?.message??e).slice(0,160))}};\r\n run("priority",()=>{\r\n  let keys=v=>v.map(e=>e.key??'
 b'e.item?.key),times=new Map([["old",2],["new",9],["tie",9]]),cmp=(a,b)=>(times.get(b.key)||0)-(times.get(a.key)||'
 b'0);\r\n  let normal=x.mW([{key:"old",recencyAt:2},{key:"new",recencyAt:9},{key:"tie",recencyAt:9}]),pinned=x.mW([{'
 b'key:"old",recencyAt:2},{key:"new",recencyAt:9},{key:"tie",recencyAt:9}]);\r\n  ok(keys(normal).join()==="new,tie,o'
 b'ld"&&keys(pinned).join()==="new,tie,old","initial");times.set("old",12);normal=x.mW(normal,cmp);pinned=x.mW(pinned,c'
 b'mp);ok(normal[0].key==="old"&&pinned[0].key==="old","live");\r\n  let get=(atom,scope)=>atom===x.rJo?!1:atom===x.M'
 b'Ai?{threadRecencyAtByKey:new Map([["held",7]])}:atom===x.AF?new Map([["held",7]]):null;\r\n  ok(x.TJo(get,{attenti'
 b'onState:"idle",isScheduled:false,kind:"task",threadEntry:{key:"held"}},"codex"),"hold");\r\n  ok(x.TJo(get,{attent'
 b'ionState:"unread",isScheduled:true,kind:"task",threadEntry:{key:"reminder"}},"codex"),"reminder");\r\n  ok(!x.TJo('
 b'get,{attentionState:"idle",isScheduled:true,kind:"task",threadEntry:{key:"dormant"}},"codex"),"dormant");\r\n  pas'
 b's(p,["priority_filter_recency_sorting","priority_filter_live_resort","priority_filter_pinned_recency_sorting","prior'
 b'ity_filter_hold_membership","active_priority_sort","automation_priority_gate"],"renderer_actual_priority_normal_pinn'
 b'ed_live");\r\n });\r\n run("pinned",()=>{let v=x.iCi({threadKeys:["k2","k1"],pinnedThreadIds:["t1","t2"],referencesB'
 b'yThreadKey:new Map([["k1",{threadId:"t1",pendingWorktreeId:null}],["k2",{threadId:"t2",pendingWorktreeId:null}]])});'
 b'ok(v.join()==="k1,k2","pinned");pass(p,["pinned_priority_sync","priority_identity_migration"],"renderer_actual_pinne'
 b'd_identity");});\r\n run("colors",()=>{\r\n  let resolve=v=>typeof v?.type==="function"?v.type(v.props):v,pending={t'
 b'ype:"implementPlan"},plan=pending?.type==="implementPlan",nodes={red:resolve(x.pIo({statusState:x.makeStatus(null,tr'
 b'ue,`idle`,true,1)})),yellow:resolve(x.pIo({statusState:x.makeStatus(pending,false,`idle`,false,0)})),blue:resolve(x.'
 b'pIo({statusState:x.makeStatus(null,false,`idle`,true,0)}))};\r\n  colors=Object.fromEntries(Object.entries(nodes).'
 b'map(([k,v])=>[k,v?.props?.style?.backgroundColor??v?.props?.style?.background??null]));ok(new Set(Object.values(colo'
 b'rs)).size===3&&!Object.values(colors).some(v=>!v),"tokens");ok(x.pIo({statusState:{type:"loading"}})!=null,"loading"'
 b');ok(x.pIo({statusState:{}})===null,"empty");\r\n  for(let [k,v] of Object.entries(nodes)){let e=document.createEl'
 b'ement("i");e.className=v.props.className??"";Object.assign(e.style,v.props.style);document.body.append(e);computed[k'
 b']=getComputedStyle(e).backgroundColor;e.remove()}ok(new Set(Object.values(computed)).size===3&&!Object.values(comput'
 b'ed).some(v=>!v||v==="rgba(0, 0, 0, 0)"),"computed");\r\n  ok(resolve(x.pIo({statusState:x.makeStatus(pending,true,'
 b'`idle`,false,0)}))?.props?.style?.background==="#eab308","plan-over-pinned");ok(colors.yellow==="#eab308"&&computed.'
 b'yellow==="rgb(234, 179, 8)","yellow-palette");ok(resolve(x.pIo({statusState:x.makeStatus(pending,true,`idle`,true,1)'
 b'}))?.props?.style?.background==="#eab308","plan-over-pinned-unread");\r\n  pass(p,["plan_pending_detection","plan_'
 b'pending_yellow_indicator","plan_pending_unread_indicator","attention_highlight_color_semantics"],"renderer_actual_co'
 b'lor_component_after_primary_route_qualification");\r\n });\r\n run("project",()=>{\r\n  let items=[{key:"p1",kind:'
 b'"project",pinned:false,source:"codex"},{key:"p2",kind:"project",pinned:false,source:"codex"},{key:"c1",kind:"convers'
 b'ation",pinned:false,projectKey:"p1",attentionState:"unread",recencyAt:10,source:"codex"},{key:"c2",kind:"conversatio'
 b'n",pinned:false,projectKey:"p2",attentionState:"idle",recencyAt:20,source:"codex"}],o={chatSortMode:"updated_at",mod'
 b'e:"project",pinnedOrder:[],pinnedSortMode:"manual",projectOrder:["p1","p2"],source:"codex"};\r\n  ok(x._wi(items,{'
 b'...o,projectSortMode:"updated_at"}).projectKeys.join()==="p2,p1","updated");ok(x._wi(items,{...o,projectSortMode:"pr'
 b'iority"}).projectKeys.join()==="p1,p2","priority");\r\n  let pin=items.map(e=>e.kind==="project"?{...e,pinned:true'
 b'}:e);ok(x._wi(pin,{...o,projectSortMode:"updated_at",pinnedSortMode:"updated_at"}).pinnedKeys.slice(0,2).join()==="p'
 b'2,p1","pinned-updated");\r\n  pass(p,["project_sorting"],"renderer_actual_project_normal_and_pinned_modes");\r\n });'
 b'\r\n run("ssh",()=>{let u="11111111-1111-4111-8111-111111111111",raw={id:u,hostId:"remote",label:u,remotePath:"/ro'
 b'ot/project-alpha"},picker={...raw,label:x.remoteName(raw)},saved={groupId:u,projectId:u,projectKind:"remote",hostId:'
 b'"remote",hostDisplayName:"Host",label:picker.label,path:raw.remotePath,gitRepos:[],isCodexWorktree:false},live={...s'
 b'aved,label:u,threadKeys:["k"]},m=x.dCi([saved],[live],new Map())[0],u2="22222222-2222-4222-8222-222222222222",m2=x.d'
 b'Ci([saved],[{...live,projectId:u2,groupId:u2}],new Map())[0];ssh=m.label;ok(picker.label==="project-alpha"&&!picker.'
 b'label.includes(u),"new-chat-picker");ok(m.label==="project-alpha"&&m.projectId===u&&m.threadKeys[0]==="k","same-id")'
 b';ok(m2.label==="project-alpha"&&m2.projectId===u&&m2.threadKeys[0]==="k","host-path");ok(x.subtitle({chatLabel:"Chat'
 b'",task:{kind:"remote"},projectLabel:"project-alpha"}).label==="project-alpha","subtitle");pass(p,["remote_project_la'
 b'bel","priority_project_context_subtitle"],"renderer_actual_ssh_raw_picker_and_late_merge");});\r\n run("work-histo'
 b'ry",()=>{let u="11111111-1111-4111-8111-111111111111",raw={id:u,hostId:"remote",label:u,remotePath:"/root/project-al'
 b'pha"},picker={...raw,label:x.remoteName(raw)},a=x.jvi({isExistingThread:false,executionHostId:"remote",activeLocalPr'
 b'ojectId:null,existingAssignment:null,homeRemoteProject:null,selectedRemoteProject:picker});ok(picker.label==="projec'
 b't-alpha"&&a.projectKind==="remote"&&a.projectId===u,"work");pass(p,["work_remote_project_picker"],"renderer_actual_n'
 b'ew_chat_picker_label_and_uuid_route");ok(x.resume({resumeState:"resumed",turnHistory:{kind:"canonical"},turnsPaginat'
 b'ion:{hasLoadedOldest:true}}),"resume");ok(!x.resume({resumeState:"resumed",turnHistory:{kind:"canonical"},turnsPagin'
 b'ation:{hasLoadedOldest:false}}),"incomplete history");ok(x.tail({turns:[{itemsPagination:{hasLoadedOldest:true}}]})&'
 b'&!x.tail({turns:[{itemsPagination:{hasLoadedOldest:false}}]}),"tail");let idle=x.idle({thread:{createdAt:1,updatedAt'
 b':2,source:null,status:null},hostId:"local",conversationId:"fixture",turns:[],threadTitle:"Fixture",resumeState:"need'
 b's_resume",latestCollaborationMode:{mode:"default",settings:{}}});ok(idle.resumeState==="needs_resume"&&idle.turns.le'
 b'ngth===0,"idle");pass(p,["resume_history_on_demand","paginated_tail_retention","idle_history_eviction"],"renderer_ac'
 b'tual_history_helpers");});\r\n run("click-drop",()=>{let reads=0,store={get:()=>({kind:"local",conversationId:"fix'
 b'ture",hostId:"local"})};x.click(store,"mark-thread-read","fixture",{markThreadAsRead:()=>reads++,markThreadAsUnread:'
 b'()=>{},setPendingWorktreePinned:()=>{}});ok(reads===1,"click");let file=new File(["synthetic"],"fixture.txt",{type:"'
 b'text/plain"}),transfer={items:[{kind:"file",getAsFile:()=>file,webkitGetAsEntry:()=>null}],files:[file],types:["File'
 b's"]};ok(hasFiles(transfer)&&dropFiles(transfer)[0]===file,"file drop");pass(p,["priority_click_hold"],"renderer_actu'
 b'al_click_handler_synthetic_store");pass(p,["new_chat_file_drop"],"renderer_actual_native_drop_helpers_after_composer'
 b'_route_qualification");});\r\n if(failures.length||Object.values(p).some(e=>!e.passed)){emit("failed",{features:p,'
 b'failure_code:failures.join("|").slice(0,600),failure_codes:failures});return}\r\n emit("passed",{features:p,colors'
 b',computed_colors:computed,plan_waiting_yellow:true,plan_source:"pending_request_type",ssh_label:ssh,new_chat_picker_'
 b'label:ssh,new_chat_picker_visible_uuid_count:0,ssh_post_merge_uuid_count:0,ssh_thread_keys_preserved:true,ssh_host_p'
 b'ath_fallback:true,route_identity_unchanged:true});\r\n}\r\n\r\nr(x);delete self.x;\r\n\r\n')
