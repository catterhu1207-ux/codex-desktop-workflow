"""Exact 26.917.8451.0 source gates and rebased accepted behavior."""
PROFILE = {'package_version': '26.917.8451.0',
 'asar_source_sha256': '18d9c47f7fcced4124a6ac4c62ad3dd67ae107c22d7bca62029fa81204b86240',
 'entry_path': 'webview/assets/app-initial-8f0e46979798.js',
 'entry_source_sha256': '627397c055589927c65d1ff9490e5956a38982cd22c9ab998570c09088ea1e63',
 'secondary_entry_path': 'webview/assets/app-primary-b25c952dc388.js',
 'secondary_entry_source_sha256': '1ecc074ef73cd83146fa316f592e66bd12c41f7745f59fd6cea02fd9b5a86d6b',
 'main_entry_path': '.vite/build/main-BR_2NHW6.js',
 'main_entry_source_sha256': '1f2b91cf92fc023fb2fa41e1c1d03698fa6e37354ecd07dd0cebd21337607b08',
 'attestation_protocol_entry_path': '.vite/build/bootstrap-CiIGnI3y.js',
 'attestation_protocol_source_sha256': '119bb54ee12ed5d2b0d3b98dd068a4322232a4aa342323eb9cb5dfa6575ca158',
 'profile_spec_id': '26917_8451',
 'attestation_log_bridge_identifier': 'Jn',
 'attestation_log_bridge_signatures': (b'function KKc(){Jn.dispatchMessage(`view-focused`,{})}',
                                       b'Jn.dispatchMessage(`log-message`,{level:`info`,message:`[startup][renderer] app routes m'
                                       b'ounted after ${Math.round(performance.now())}ms`}),Jn.dispatchMessage(`ready`,{persisted'
                                       b'StateResponsePriority:R9?`critical`:void 0})')}

PAIRS = {'automation_priority_gate': ((b'function Y2(e,t,n){if(t.isScheduled&&e(cls)!==!0)return!1;',
                               b'function Y2(e,t,n){if(t.isScheduled&&e(cls)&&t.attentionState===`idle`)return!1;'),),
 'plan_pending_detection': ((b'function CVs(e){let t=(0,TVs.c)(155)', b'function CVs(e){let t=(0,TVs.c)(157)'),
                            (b'onDoubleClick:f,isActive:p,tone:m', b'onDoubleClick:f,isActive:p,P:Q,tone:m'),
                            (b't[28]!==Jt||t[29]!==Yt||t[30]!==Xt',
                             b't[28]!==Jt||t[29]!==Yt||t[30]!==Xt||t[155]!==xt||t[156]!==Q'),
                            (b'Zt={type:Jt,unread:Yt,unreadCount:Xt},t[28]=Jt',
                             b'Zt=qZp(xt,Q,Jt,Yt,Xt),t[155]=xt,t[156]=Q,t[28]=Jt'),
                            (b'function pWs(e){let t=(0,hWs.c)(171)', b'function pWs(e){let t=(0,hWs.c)(172)'),
                            (b't[148]!==jt||t[149]!==w', b't[148]!==jt||t[149]!==w||t[171]!==b'),
                            (b'disableEnvTooltip:!0,isActive:De,isUnread:a', b'disableEnvTooltip:!0,isActive:De,P:b,isUnread:a'),
                            (b't[148]=jt,t[149]=w', b't[148]=jt,t[149]=w,t[171]=b'),
                            (b'Xe=Ye!==void 0&&Ye,Ze=Xe||(k.unreadCount??0)>0', b'Xe=!!(Ye||k.p),Ze=Ye||(k.unreadCount??0)>0')),
 'plan_pending_yellow_indicator': ((b'function L4(e){let t=(0,Vbs.c)(5),{statusState:n,size:r}=e,i=r===void 0?`compact`:r;if(('
                                    b'n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r=(0,R4.jsx)(Rbs,{'
                                    b'count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t[2]===i?e=t[3]:(e=(0,R4.'
                                    b'jsx)(Bbs,{size:i}),t[2]=i,t[3]=e),e}if(n.unread===!0){let e;return t[4]===Symbol.for(`re'
                                    b'act.memo_cache_sentinel`)?(e=(0,R4.jsx)(zbs,{}),t[4]=e):e=t[4],e}return null}',
                                    b'function qZp(e,t,n,r,i){return{type:n,unread:r,unreadCount:i,p:e?.kind===`implementPlan`'
                                    b',i:!!t}}function L4({statusState:e,size:t}){let n=e.unreadCount||e.unread,r=e.p?`#eab308'
                                    b'`:e.i&&n?`danger`:n?`info`:null,i=R4.jsx;return e.type===`loading`?i(Bbs,{size:t}):r&&i('
                                    b'zbs,{c:r})}'),
                                   (b'function zbs(){let e=(0,Vbs.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`'
                                    b')?(t=(0,R4.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-cen'
                                    b'ter text-codex-description`,children:(0,R4.jsx)(`span`,{className:`icon-xs relative scal'
                                    b'e-50`,children:(0,R4.jsx)(`span`,{className:`absolute inset-0 rounded-full bg-info-solid'
                                    b'`})})}),e[0]=t):t=e[0],t}',
                                    b'function zbs({c:e}){return R4.jsx(`i`,{className:`mx-1.5 size-2 shrink-0 rounded-full`,s'
                                    b'tyle:{background:e[0]===`#`?e:`var(--color-text-${e})`}})}')),
 'priority_filter_live_resort': ((b'C=h==null?void 0:S.find(({item:e})=>{let t=X2(l,e);return t===X2(l,h.item)&&!p.has(t)})?.ite'
                                  b'm,',
                                  b'C=((e,t)=>(_.get(X2(l,t))||0)-(_.get(X2(l,e))||0)),'),
                                 (b'w=wls(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>!n.has(X2(l,e)))),T=l(K2)'
                                  b'===!0',
                                  b'w=sF(wls(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(X2(l,e)))),C),T=l(K2)===!0'),
                                 (b'k=wls(l,[...b,...l(qls,u.sidebarMode).filter(e=>{let t=X2(l,e);return!T||!E||!kls(l,e,u.side'
                                  b'barMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(X2(l,e))&&Als(l,e)));',
                                  b'k=sF(wls(l,[...b,...l(qls,u.sidebarMode).filter(e=>{let t=X2(l,e);return!T||!E||!kls(l,e,u.s'
                                  b'idebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(X2(l,e))&&Als(l,e))),C);')),
 'priority_filter_pinned_recency_sorting': ((b'qls=ns(X,(e,{get:t})=>Q2(t,e).filter(({item:n})=>Y2(t,n,e)&&Als(t,n)).map(({item'
                                             b':e})=>e))',
                                             b'qls=ns(X,(e,{get:t})=>sF(Q2(t,e).filter(({item:n})=>Y2(t,n,e)&&Als(t,n))).map(({'
                                             b'item:e})=>e))'),),
 'priority_filter_recency_sorting': ((b'function sF(e){return[...e].sort((e,t)=>rWr[e.attentionState]-rWr[t.attentionState]||t.r'
                                      b'ecencyAt-e.recencyAt)}',
                                      b'function sF(e,t=(e,t)=>t.recencyAt-e.recencyAt){return[...e].sort(t)}'),),
 'project_sorting': ((b'projectOrder:p,serverOrderedPinnedThreadHostIds:m',
                      b'projectOrder:p,projectSortMode:J,serverOrderedPinnedThreadHostIds:m'),
                     (b'let E=dWr(x,p,`start`),D=new Set(E);',
                      b'let P=e=>{let t=e.kind==`project`?_.filter(t=>t.projectKey==e.key):[e];return[e,Math.max(...t.map(e=>e.r'
                      b'ecencyAt)),Math.min(...t.map(e=>rWr[e.prioritySortAttentionState??e.attentionState]))]},E=J[0]==`m`?dWr('
                      b'x,p,`start`):x.map(P).sort((e,t)=>J[0]==`p`?e[2]-t[2]||t[1]-e[1]:t[1]-e[1]).map(e=>e[0].key),D=new Set(E'
                      b');'),
                     (b'pinnedKeys:sWr({entries:v,pinnedKeyAliases:u,pinnedOrder:d,pinnedSortMode:f,serverOrderedPinnedThreadHos'
                      b'tIds:m',
                      b'pinnedKeys:sWr({entries:v,pinnedKeyAliases:u,pinnedOrder:f===`manual`?d:v.map(P).sort((e,t)=>t[1]-e[1]).'
                      b'map(e=>e[0].key),pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:m'),
                     (b'pinnedSortMode:D,projectOrder:O,retainedUnreadKeys:r',
                      b'pinnedSortMode:D,projectOrder:O,projectSortMode:T,retainedUnreadKeys:r')),
 'remote_project_label': ((b'function gYr(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id'
                           b',projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:e.l'
                           b'abel,path:e.remotePath,gitRepos:xYr([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}',
                           b'function qZx(e,t){return e.label!=e.id&&e.label||e.remotePath.split(`/`).pop()||t||`Remote`}function'
                           b' gYr(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,project'
                           b'Id:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:qZx(e,r.get'
                           b'(e.hostId)),path:e.remotePath,gitRepos:xYr([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}'
                           b'))}'),
                          (b'function ZJr(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return XJr(e.map(e=>r.get(e.projectId)?'
                           b'?{...e,threadKeys:[]}),n)}',
                           b'function ZJr(e,t,n){return XJr(e.map(e=>{let n=t.find(t=>t.projectId==e.projectId||t.hostId==e.hostI'
                           b'd&&AYr(t.path)==AYr(e.path));return{...n,...e,threadKeys:n?.threadKeys||[]}}),n)}')),
 'work_remote_project_picker': ((b'function jYr(){let e=(0,MYr.c)(10),{data:t,isLoading:n}=VS(na.REMOTE_PROJECTS),r=lr(Cv),i=lr'
                                 b'(nUt),a;e[0]===t?a=e[1]:(a=t??[],e[0]=t,e[1]=a);let o=a,s=r?.type===`remote`?r.projectId:nul'
                                 b'l,c;e[2]!==o||e[3]!==s?(c=o.find(e=>e.id===s)??null,e[2]=o,e[3]=s,e[4]=c):c=e[4];let l=c,u=n'
                                 b'||i,d=s??null,f;return e[5]!==o||e[6]!==l||e[7]!==u||e[8]!==d?(f={isLoading:u,selectedRemote'
                                 b'Project:l,selectedRemoteProjectId:d,remoteProjects:o},e[5]=o,e[6]=l,e[7]=u,e[8]=d,e[9]=f):f='
                                 b'e[9],f}',
                                 b'function jYr(){let{data:t,isLoading:n}=VS(na.REMOTE_PROJECTS),r=lr(Cv),i=lr(nUt),a=t?.map(e='
                                 b'>({...e,label:qZx(e)}))||[],s=r?.type===`remote`?r.projectId:null;return{isLoading:n||i,sele'
                                 b'ctedRemoteProject:a.find(e=>e.id===s)??null,selectedRemoteProjectId:s,remoteProjects:a}}'),)}

SECONDARY_PAIRS = {'work_remote_project_picker': ((b'function Z7(e){let t=(0,Q7.c)(23),{projectId:n,projectName:r,projectlessTriggerLabel:i,menuO'
                                 b'pen:a,onMenuOpenChange:o,shortcut:s,subtleHover:c,triggerButton:l,variant:u,onProjectChange:'
                                 b'd}=e,f=r===void 0?null:r,p=X(rT),m=n;if(m===void 0&&(m=p?.type===`local`?p.projectId:null),d'
                                 b'!=null){let e;t[0]===m?e=t[1]:(e=m?.startsWith(`g-p-`)?m:null,t[0]=m,t[1]=e);let n;return t['
                                 b'2]!==a||t[3]!==o||t[4]!==d||t[5]!==f||t[6]!==i||t[7]!==s||t[8]!==c||t[9]!==e||t[10]!==l||t[1'
                                 b'1]!==u?(n=(0,$7.jsx)(j$,{projectId:e,projectName:f,projectlessTriggerLabel:i,menuOpen:a,onMe'
                                 b'nuOpenChange:o,shortcut:s,subtleHover:c,triggerButton:l,variant:u,onProjectChange:d}),t[2]=a'
                                 b',t[3]=o,t[4]=d,t[5]=f,t[6]=i,t[7]=s,t[8]=c,t[9]=e,t[10]=l,t[11]=u,t[12]=n):n=t[12],n}let h;r'
                                 b'eturn t[13]!==a||t[14]!==o||t[15]!==m||t[16]!==f||t[17]!==i||t[18]!==s||t[19]!==c||t[20]!==l'
                                 b'||t[21]!==u?(h=(0,$7.jsx)(Agt,{projectId:m,projectName:f,projectlessTriggerLabel:i,menuOpen:'
                                 b'a,onMenuOpenChange:o,shortcut:s,subtleHover:c,triggerButton:l,variant:u}),t[13]=a,t[14]=o,t['
                                 b'15]=m,t[16]=f,t[17]=i,t[18]=s,t[19]=c,t[20]=l,t[21]=u,t[22]=h):h=t[22],h}',
                                 b'function Z7(e){let{projectId:n,projectName:r=null,onProjectChange:d,...a}=e,p=X(rT),m=n===vo'
                                 b'id 0?p?.projectId??null:n;return d!=null?(0,$7.jsx)(j$,{...a,projectId:m?.startsWith(`g-p-`)'
                                 b'?m:null,projectName:r,onProjectChange:d}):(0,$7.jsx)(Agt,{...a,projectId:m,projectName:r})}'),
                                (b'd=ut(Ir),f=X(vpe),p=X(QDe)',
                                 b'd=ut(Ir),f=[...X(vpe),...X(gee).filter(e=>e.projectKind===`remote`)],p=X(QDe)'),
                                (b'C=g?{projects:f,onSelectProject:e=>{xd(d,{...e,projectKind:`local`})}}:void 0',
                                 b'C={projects:f.filter(e=>g||e.projectKind===`remote`),onSelectProject:e=>{xd(d,e)}}'),
                                (b't=ut(tS),n=X(vpe),r;',
                                 b't=ut(tS),n=[...X(vpe),...X(gee).filter(e=>e.projectKind===`remote`)],r;'),
                                (b'r=e=>{xd(t,{...e,projectKind:`local`})}', b'r=e=>{xd(t,e)}'))}

OFFICIAL_FEATURE_SIGNATURES = {'priority_filter_hold_membership': (b'function kls(e,t,n){if(!Y2(e,t,n))return!1;',
                                     b'Kls=ns(X,(e,{get:t})=>sF(Q2(t,e).filter(({item:n})=>kls(t,n,e))))'),
 'priority_identity_migration': (b'function RJr({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n}){',),
 'priority_project_context_subtitle': (b'function tYr({chatLabel:e,task:t,projectLabel:n',),
 'active_priority_sort': (b'function EQr({items:e,attentionStateByThreadKey:t}){',
                          b'function DQr({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r}){'),
 'pinned_priority_sync': (b'function RJr({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n}){',),
 'resume_history_on_demand': (b'function S1t(e){return e.resumeState===`resumed`&&(',),
 'paginated_tail_retention': (b'function Wlt(e){return lp(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}',),
 'idle_history_eviction': (b'function zgt({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a',),
 'priority_click_hold': (b'function FUs(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a})',),
 'new_chat_file_drop': (b'function LFa(e){if(e==null)return!1;if(Array.from(e.items??[]).some(e=>e.kind===`file`))return!0;let'
                        b'{types:t}=e;for(let e=0;e<t.length;e+=1)if(t[e]===YFa)return!0;return!1}',
                        b'function tGs(e){if(e==null)return[];let t=Array.from(e.items??[]).filter(e=>e.kind===`file`);return '
                        b'e.files.length>0?Array.from(e.files).filter((e,n)=>t[n]?.webkitGetAsEntry?.()?.isDirectory!==!0):t.f'
                        b'latMap(e=>{if(e.webkitGetAsEntry?.()?.isDirectory===!0)return[];let t=e.getAsFile();return t==null?['
                        b']:[t]})}'),
 'archived_heartbeat_terminal_guard': (b'defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat c'
                                       b'onfirmation dialog when the chat has an active heartbeat automation`}',)}

SECONDARY_OFFICIAL_FEATURE_SIGNATURES = {}

ATTESTATION_SCRIPT = b',self.x=[sF,RJr,kls,L4,cWr,ZJr,WYr,cls,pI,ET,Jn,qZx,qZp,FUs,S1t,Wlt,zgt,tYr,Hmt],import(`/x`)'

PROTOCOL_OLD = b'function pt(e,t){let r=St(e);if(!r)return null;try{'

PROTOCOL_NEW = b'function pt(e,t){let r=St(e);if(!r)return null;if(e===`app://-/x`)return t+`/../../x.js`;try{'

PROTOCOL_COMPACTION_OLD = b'let a=i.pathname?i.pathname:`/`,o=n.Tl(a)'

PROTOCOL_COMPACTION_NEW = b'let a=i.pathname||`/`,o=n.Tl(a)'

HANDLER_OLD = (b'return n?Tt(n)?Et(t,n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toString()):gt(n):new Response(null,{st'
 b'atus:404,statusText:`Not Found`})')

HANDLER_NEW = (b'return n?Tt(n)?Et(t,n):n.endsWith(`/x.js`)?gt(n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toString()):g'
 b't(n):new Response(null,{status:404})')

ATTESTATION_MODULE = (b'import{Uh as rowComponent,Dp as dropFiles,NZ as hasFiles}from"/assets/app-initial-8f0e46979798.js";\nconst [RW,LFi,iLo,b$o,JI'
 b'i,WFi,ZAi,Tns,PHi,oI,ay,qZx,qZp,click,resume,tail,idle,subtitle,pendingRequest]=self.x;const x={mW:RW,iCi:LFi,TJo:iLo,pIo:b$'
 b'o,_wi:JIi,dCi:WFi,jvi:ZAi,remoteName:qZx,rJo:Tns,MAi:PHi,AF:oI,ay,makeStatus:qZp,click,resume,tail,idle,subtitle,pendingRequ'
 b'est,rowComponent};\r\nconst F=["priority_filter_recency_sorting","priority_filter_live_resort","priority_filter_pinned_recency'
 b'_sorting","priority_filter_hold_membership","priority_click_hold","priority_identity_migration","priority_project_context_su'
 b'btitle","plan_pending_detection","plan_pending_yellow_indicator","plan_pending_unread_indicator","attention_highlight_color_'
 b'semantics","project_sorting","active_priority_sort","automation_priority_gate","pinned_priority_sync","new_chat_file_drop","'
 b'resume_history_on_demand","paginated_tail_retention","idle_history_eviction","remote_project_label","work_remote_project_pic'
 b'ker"];\r\nconst M="[CF9]",A="2.6.14-18d9c47f7fcc",R=crypto.randomUUID();\r\nconst ok=(v,m)=>{if(!v)throw Error(m)},pass=(p,i'
 b'ds,e)=>ids.forEach(id=>p[id]={passed:true,evidence:e});\r\nexport async function r(x){\r\n const emit=(status,extra={})=>x.a'
 b'y.dispatchMessage("log-message",{level:status==="failed"?"error":"info",message:M+JSON.stringify({schema_version:6,validator'
 b'_version:"2.4.11",artifact_id:A,run_id:R,status,content_logged:false,transport:"renderer_log_message_v1",...extra})});\r\n emi'
 b't("module_loaded");\r\n let p=Object.fromEntries(F.map(id=>[id,{passed:false,evidence:"unexecuted"}])),failures=[],colors={},c'
 b'omputed={},ssh=null;\r\n let run=(code,fn)=>{try{fn()}catch(e){failures.push(code+":"+String(e?.message??e).slice(0,160))}'
 b'};\r\n run("priority",()=>{\r\n  let keys=v=>v.map(e=>e.key??e.item?.key),times=new Map([["old",2],["new",9],["tie",9]]),cmp'
 b'=(a,b)=>(times.get(b.key)||0)-(times.get(a.key)||0);\r\n  let normal=x.mW([{key:"old",recencyAt:2},{key:"new",recencyAt:9},{ke'
 b'y:"tie",recencyAt:9}]),pinned=x.mW([{key:"old",recencyAt:2},{key:"new",recencyAt:9},{key:"tie",recencyAt:9}]);\r\n  ok(keys(no'
 b'rmal).join()==="new,tie,old"&&keys(pinned).join()==="new,tie,old","initial");times.set("old",12);normal=x.mW(normal,cmp);pin'
 b'ned=x.mW(pinned,cmp);ok(normal[0].key==="old"&&pinned[0].key==="old","live");\r\n  let get=(atom,scope)=>atom===x.rJo?!1:atom='
 b'==x.MAi?{threadRecencyAtByKey:new Map([["held",7]])}:atom===x.AF?new Map([["held",7]]):null;\r\n  ok(x.TJo(get,{attentionState'
 b':"idle",isScheduled:false,kind:"task",threadEntry:{key:"held"}},"codex"),"hold");\r\n  ok(x.TJo(get,{attentionState:"unread",i'
 b'sScheduled:true,kind:"task",threadEntry:{key:"reminder"}},"codex"),"reminder");\r\n  ok(!x.TJo(get,{attentionState:"idle",isSc'
 b'heduled:true,kind:"task",threadEntry:{key:"dormant"}},"codex"),"dormant");\r\n  pass(p,["priority_filter_recency_sorting","pri'
 b'ority_filter_live_resort","priority_filter_pinned_recency_sorting","priority_filter_hold_membership","active_priority_sort",'
 b'"automation_priority_gate"],"renderer_actual_priority_normal_pinned_live");\r\n });\r\n run("pinned",()=>{let v=x.iCi({threa'
 b'dKeys:["k2","k1"],pinnedThreadIds:["t1","t2"],referencesByThreadKey:new Map([["k1",{threadId:"t1",pendingWorktreeId:null}],['
 b'"k2",{threadId:"t2",pendingWorktreeId:null}]])});ok(v.join()==="k1,k2","pinned");pass(p,["pinned_priority_sync","priority_id'
 b'entity_migration"],"renderer_actual_pinned_identity");});\r\n run("colors",()=>{\r\n  let resolve=v=>typeof v?.type==="funct'
 b'ion"?v.type(v.props):v,pending=x.pendingRequest({requests:[],turns:[{turnId:"fixture",items:[{type:"planImplementation",isCo'
 b'mpleted:false}]}]}),plan=pending?.kind==="implementPlan",nodes={red:resolve(x.pIo({statusState:x.makeStatus(null,true,`idle`'
 b',true,1)})),yellow:resolve(x.pIo({statusState:x.makeStatus(pending,false,`idle`,false,0)})),blue:resolve(x.pIo({statusState:'
 b'x.makeStatus(null,false,`idle`,true,0)}))};\r\n  colors=Object.fromEntries(Object.entries(nodes).map(([k,v])=>[k,v?.props?.sty'
 b'le?.backgroundColor??v?.props?.style?.background??null]));ok(new Set(Object.values(colors)).size===3&&!Object.values(colors)'
 b'.some(v=>!v),"tokens");ok(x.pIo({statusState:{type:"loading"}})!=null,"loading");ok(x.pIo({statusState:{}})===null,"empty");'
 b'\r\n  for(let [k,v] of Object.entries(nodes)){let e=document.createElement("i");e.className=v.props.className??"";Object.assig'
 b'n(e.style,v.props.style);document.body.append(e);computed[k]=getComputedStyle(e).backgroundColor;e.remove()}ok(new Set(Objec'
 b't.values(computed)).size===3&&!Object.values(computed).some(v=>!v||v==="rgba(0, 0, 0, 0)"),"computed");\r\n  ok(resolve(x.pIo('
 b'{statusState:x.makeStatus(pending,true,`idle`,false,0)}))?.props?.style?.background==="#eab308","plan-over-pinned");ok(color'
 b's.yellow==="#eab308"&&computed.yellow==="rgb(234, 179, 8)","yellow-palette");ok(resolve(x.pIo({statusState:x.makeStatus(pend'
 b'ing,true,`idle`,true,1)}))?.props?.style?.background==="#eab308","plan-over-pinned-unread");\r\n  pass(p,["plan_pending_detect'
 b'ion","plan_pending_yellow_indicator","plan_pending_unread_indicator","attention_highlight_color_semantics"],"renderer_actual'
 b'_color_component_after_primary_route_qualification");\r\n });\r\n run("project",()=>{\r\n  let items=[{key:"p1",kind:"project"'
 b',pinned:false,source:"codex"},{key:"p2",kind:"project",pinned:false,source:"codex"},{key:"c1",kind:"conversation",pinned:fal'
 b'se,projectKey:"p1",attentionState:"unread",recencyAt:10,source:"codex"},{key:"c2",kind:"conversation",pinned:false,projectKe'
 b'y:"p2",attentionState:"idle",recencyAt:20,source:"codex"}],o={chatSortMode:"updated_at",mode:"project",pinnedOrder:[],pinned'
 b'SortMode:"manual",projectOrder:["p1","p2"],source:"codex"};\r\n  ok(x._wi(items,{...o,projectSortMode:"updated_at"}).projectKe'
 b'ys.join()==="p2,p1","updated");ok(x._wi(items,{...o,projectSortMode:"priority"}).projectKeys.join()==="p1,p2","priority");\r\n'
 b'  let pin=items.map(e=>e.kind==="project"?{...e,pinned:true}:e);ok(x._wi(pin,{...o,projectSortMode:"updated_at",pinnedSortMo'
 b'de:"updated_at"}).pinnedKeys.slice(0,2).join()==="p2,p1","pinned-updated");\r\n  pass(p,["project_sorting"],"renderer_actual_p'
 b'roject_normal_and_pinned_modes");\r\n });\r\n run("ssh",()=>{let u="c87575b4-dba0-471e-a647-31ce8575c46b",raw={id:u,hostId:"'
 b'remote",label:u,remotePath:"/root/project-alpha"},picker={...raw,label:x.remoteName(raw)},saved={groupId:u,projectId:u,proje'
 b'ctKind:"remote",hostId:"remote",hostDisplayName:"Host",label:picker.label,path:raw.remotePath,gitRepos:[],isCodexWorktree:fa'
 b'lse},live={...saved,label:u,threadKeys:["k"]},m=x.dCi([saved],[live],new Map())[0],u2="423dd422-a9ef-4fc4-8c97-583483a49850"'
 b',m2=x.dCi([saved],[{...live,projectId:u2,groupId:u2}],new Map())[0];ssh=m.label;ok(picker.label==="project-alpha"&&!picker.l'
 b'abel.includes(u),"new-chat-picker");ok(m.label==="project-alpha"&&m.projectId===u&&m.threadKeys[0]==="k","same-id");ok(m2.la'
 b'bel==="project-alpha"&&m2.projectId===u&&m2.threadKeys[0]==="k","host-path");ok(x.subtitle({chatLabel:"Chat",task:{kind:"rem'
 b'ote"},projectLabel:"project-alpha"}).label==="project-alpha","subtitle");pass(p,["remote_project_label","priority_project_co'
 b'ntext_subtitle"],"renderer_actual_ssh_raw_picker_and_late_merge");});\r\n run("work-history",()=>{let u="c87575b4-dba0-471e-a6'
 b'47-31ce8575c46b",raw={id:u,hostId:"remote",label:u,remotePath:"/root/project-alpha"},picker={...raw,label:x.remoteName(raw)}'
 b',a=x.jvi({isExistingThread:false,executionHostId:"remote",activeLocalProjectId:null,existingAssignment:null,homeRemoteProjec'
 b't:null,selectedRemoteProject:picker});ok(picker.label==="project-alpha"&&a.projectKind==="remote"&&a.projectId===u,"work");p'
 b'ass(p,["work_remote_project_picker"],"renderer_actual_new_chat_picker_label_and_uuid_route");ok(x.resume({resumeState:"resum'
 b'ed",turnHistory:{kind:"canonical"},turnsPagination:{hasLoadedOldest:true}}),"resume");ok(!x.resume({resumeState:"resumed",tu'
 b'rnHistory:{kind:"canonical"},turnsPagination:{hasLoadedOldest:false}}),"incomplete history");ok(x.tail({turns:[{itemsPaginat'
 b'ion:{hasLoadedOldest:true}}]})&&!x.tail({turns:[{itemsPagination:{hasLoadedOldest:false}}]}),"tail");let idle=x.idle({thread'
 b':{createdAt:1,updatedAt:2,source:null,status:null},hostId:"local",conversationId:"fixture",turns:[],threadTitle:"Fixture",re'
 b'sumeState:"needs_resume",latestCollaborationMode:{mode:"default",settings:{}}});ok(idle.resumeState==="needs_resume"&&idle.t'
 b'urns.length===0,"idle");pass(p,["resume_history_on_demand","paginated_tail_retention","idle_history_eviction"],"renderer_act'
 b'ual_history_helpers");});\r\n run("click-drop",()=>{let reads=0,store={get:()=>({kind:"local",conversationId:"fixture",hostId:'
 b'"local"})};x.click(store,"mark-thread-read","fixture",{markThreadAsRead:()=>reads++,markThreadAsUnread:()=>{},setPendingWork'
 b'treePinned:()=>{}});ok(reads===1,"click");let file=new File(["synthetic"],"fixture.txt",{type:"text/plain"}),transfer={items'
 b':[{kind:"file",getAsFile:()=>file,webkitGetAsEntry:()=>null}],files:[file],types:["Files"]};ok(hasFiles(transfer)&&dropFiles'
 b'(transfer)[0]===file,"file drop");pass(p,["priority_click_hold"],"renderer_actual_click_handler_synthetic_store");pass(p,["n'
 b'ew_chat_file_drop"],"renderer_actual_native_drop_helpers_after_composer_route_qualification");});\r\n let mountedRow=null;try{'
 b'mountedRow=await qualifyMountedRow(x,ok)}catch(e){failures.push("mounted-row:"+String(e))}\r\n if(failures.length||Object.valu'
 b'es(p).some(e=>!e.passed)){emit("failed",{features:p,failure_code:failures.join("|").slice(0,600),failure_codes:failures});re'
 b'turn}\r\n emit("passed",{features:p,colors,computed_colors:computed,mounted_row:mountedRow,plan_waiting_yellow:true,plan_sourc'
 b'e:"pending_request_kind",ssh_label:ssh,new_chat_picker_label:ssh,new_chat_picker_visible_uuid_count:0,ssh_post_merge_uuid_co'
 b'unt:0,ssh_thread_keys_preserved:true,ssh_host_path_fallback:true,route_identity_unchanged:true});\r\n}\r\n\r\nr(x);delete self'
 b'.x;\r\n\r\n\n// Run the real React consumer under the official renderer, with synthetic inputs.\nasync function qualifyMounted'
 b"Row(x,ok){\n const shared=await import('/assets/app-shared-baf181f346ac.js');\n shared.J2();const React=shared.e6(),jsx=React."
 b"createElement;\n const host=document.createElement('div');\n host.setAttribute('data-hotfix-plan-row-probe','');\n Object.a"
 b"ssign(host.style,{position:'fixed',left:'-10000px',top:'0',width:'400px'});\n document.body.append(host);\n let errors=[];cons"
 b't root=shared.N3().createRoot(host,{onUncaughtError:e=>errors.push(String(e))});\n const frames=()=>new Promise(resolve=>setT'
 b"imeout(resolve,80));\n const pending=done=>x.pendingRequest({requests:[],turns:[{turnId:'fixture',items:[{type:'planImplement"
 b"ation',isCompleted:done}]}]});\n const render=async(done,pinned,unread,loading=false)=>{\n  let state=x.makeStatus(pending(don"
 b"e),pinned,loading?'loading':'idle',unread,0);\n  root.render(jsx(shared.q2,{locale:'en',messages:{}},jsx(x.rowComponent,{titl"
 b"e:'Plan fixture',statusState:state,statusIndicatorReplacesMeta:true,metaContent:'meta',onClick:()=>{}})));\n  await frames();"
 b"ok(!errors.length,errors.join('|'));\n  let dot=host.querySelector('i.rounded-full');\n  return {color:dot?getComputedStyle(do"
 b't).backgroundColor:null,spinner:!!host.querySelector(\'[role="status"]\'),unread:!!host.querySelector(\'.sr-only\'),width:do'
 b"t?.getBoundingClientRect().width??0};\n };\n try{\n  let idle=await render(true,false,false);ok(!idle.color,'idle row');\n  "
 b"let plan=await render(false,false,false);ok(plan.color==='rgb(234, 179, 8)'&&plan.width>0&&!plan.unread,'read plan mounted y"
 b"ellow');\n  let pinned=await render(false,true,true);ok(pinned.color===plan.color,'pinned plan mounted yellow');\n  let loadin"
 b"g=await render(false,true,true,true);ok(!loading.color&&loading.spinner,'plan spinner');\n  let red=await render(true,true,tr"
 b'ue),blue=await render(true,false,true);ok(red.color&&blue.color&&red.color!==blue.color&&red.color!==plan.color&&blue.color!'
 b"==plan.color,'nonplan unread colors');\n  let done=await render(true,false,false);ok(!done.color&&!done.spinner,'completed ro"
 b"w cleared');\n  return {status:'passed',official_producer:true,actual_react_row:true,retained_root:true,read_plan_color:plan."
 b'color,pinned_plan_color:pinned.color,spinner:true,completed_cleared:true};\n }finally{root.unmount();host.remove()}\n}\n')

