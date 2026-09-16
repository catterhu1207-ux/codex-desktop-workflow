from __future__ import annotations


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Exact, hash-gated Microsoft Store 26.825.5331.0 frontend profile.
# Every replacement below is anchored to app-initial-DWX_sBmZ.js from the
# official ASAR SHA-256 178b65229452b17b0203ab41d5ceafedccd770c9bd42d239a6d048d27d80252b.
PAIRS: dict[str, tuple[tuple[bytes, bytes], ...]] = {
    "automation_priority_gate": (
        (
            b("if(t.isScheduled&&e(wuc)!==!0)return!1;"),
            b("if(t.isScheduled&&t.attentionState===`idle`&&e(wuc)!==!0)return!1;"),
        ),
    ),
    "priority_filter_recency_sorting": (
        (
            b("function SCr(e){return[...e].sort((e,t)=>wCr[e.attentionState]-wCr[t.attentionState]||t.recencyAt-e.recencyAt)}"),
            b("function SCr(e){return[...e].sort((e,t)=>t.recencyAt-e.recencyAt)}function CPS(e,t,n){return[...t].map((t,r)=>[t,r,n.get(O6(e,t))??0]).sort((e,t)=>t[2]-e[2]||e[1]-t[1]).map(e=>e[0])}"),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b("w=Buc(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>!n.has(O6(l,e)))),T=l(E6)===!0"),
            b("w=CPS(l,Buc(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>!n.has(O6(l,e)))),_),T=l(E6)===!0"),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b("k=Buc(l,[...b,...l(ddc,u.sidebarMode).filter(e=>{let t=O6(l,e);return!T||!E||!Guc(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(O6(l,e))&&quc(l,e)));"),
            b("k=CPS(l,Buc(l,[...b,...l(ddc,u.sidebarMode).filter(e=>{let t=O6(l,e);return!T||!E||!Guc(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(O6(l,e))&&quc(l,e))),_);"),
        ),
    ),
    "priority_project_context_subtitle": (
        (
            b("function tXc(e){let t=(0,iXc.c)(5),n=e.entryFallback?.kind===`local`?e.entryFallback:null,r;t[0]===n?r=t[1]:(r=n?.conversationId==null?null:{hostId:n.hostId??n.summary?.hostId??`local`,threadId:n.conversationId},t[0]=n,t[1]=r);let i=k_(WYc,r)??e.secondaryContent,a;return t[2]!==e||t[3]!==i?(a=(0,r7.jsx)(aBc,{...e,secondaryContent:i}),t[2]=e,t[3]=i,t[4]=a):a=t[4],a}"),
            b("function tXc(e){let t=(0,iXc.c)(5),n=e.entryFallback?.kind===`local`?e.entryFallback:null,r;t[0]===n?r=t[1]:(r=n?.conversationId==null?null:{hostId:n.hostId??n.summary?.hostId??`local`,threadId:n.conversationId},t[0]=n,t[1]=r);let i=k_(WYc,r),a=e.secondaryContent?.props?.projectGroup!=null,o=a?(i==null?e.secondaryContent:(0,r7.jsxs)(r7.Fragment,{children:[e.secondaryContent,` · `,i]})):i??e.secondaryContent,s;return t[2]!==e||t[3]!==o?(s=(0,r7.jsx)(aBc,{...e,secondaryContent:o}),t[2]=e,t[3]=o,t[4]=s):s=t[4],s}"),
        ),
        (
            b("titleSuffix:B&&n.conversation.gizmo_id!=null?(0,r7.jsx)(uMc,{conversationId:e,projectId:n.conversation.gizmo_id}):void 0,secondaryContent:"),
            b("titleSuffix:void 0,secondaryContent:"),
        ),
        (
            b("titleSuffix:B?(0,r7.jsx)(uMc,{conversationId:e}):void 0,secondaryContent:"),
            b("titleSuffix:null,secondaryContent:"),
        ),
        (
            b("titleSuffix:B&&n.projectGroup!=null?(0,r7.jsx)(lMc,{projectLabel:n.projectGroup.label}):void 0,secondaryContent:"),
            b("titleSuffix:undefined,secondaryContent:"),
        ),
    ),
    "plan_pending_detection": (
        (
            b("kt;t[19]!==Me||t[20]!==je||t[21]!==Pe||t[22]!==$e||t[23]!==Tt||t[24]!==ce||t[25]!==rt||t[26]!==Et||t[27]!==et?(kt=je?{type:`loading`}:{type:Et,unread:Tt?!1:(ce??$e===!0)||Me&&((et??0)>0||rt!=null||Pe),unreadCount:Tt||Me?0:et??0},t[19]=Me,t[20]=je,t[21]=Pe,t[22]=$e,t[23]=Tt,t[24]=ce,t[25]=rt,t[26]=Et,t[27]=et,t[28]=kt):kt=t[28]"),
            b("kt=je?{type:`loading`}:{type:Et,unread:Tt?!1:(ce??$e===!0)||Me&&((et??0)>0||rt!=null||Pe),unreadCount:Tt||Me?0:et??0,plan:rt?.type===`implementPlan`,pinned:Pi===!0}"),
        ),
        (
            b("threadSummary:w,...pe,renderActions:nt,allowActionsWhenDisabled:Ye})"),
            b("threadSummary:w,...pe,renderActions:nt,allowActionsWhenDisabled:Ye,pinned:b})"),
        ),
        (
            b("threadSummary:ve,dataAttributes:ye}=e"),
            b("threadSummary:ve,pinned:Pi,dataAttributes:ye}=e"),
        ),
    ),
    "plan_pending_yellow_indicator": (
        (
            b("function m8(e){let t=(0,aEc.c)(4),{statusState:n}=e;if((n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r=(0,h8.jsx)(nEc,{count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t[2]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,h8.jsx)(iEc,{}),t[2]=e):e=t[2],e}if(n.unread===!0){let e;return t[3]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,h8.jsx)(rEc,{}),t[3]=e):e=t[3],e}return null}"),
            b("function m8({statusState:e}){return e.type===`loading`?(0,h8.jsx)(iEc,{}):e.plan?(0,h8.jsx)(rEc,{plan:!0,pinned:e.pinned}):(e.unreadCount??0)>0?(0,h8.jsx)(nEc,{count:e.unreadCount}):e.unread?(0,h8.jsx)(rEc,{plan:!1,pinned:e.pinned}):null}"),
        ),
        (
            b("function rEc(){let e=(0,aEc.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`)?(t=(0,h8.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-codex-description`,children:(0,h8.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,h8.jsx)(`span`,{className:`absolute inset-0 rounded-full bg-info-solid`})})}),e[0]=t):t=e[0],t}"),
            b("function rEc({plan:e,pinned:t}){return(0,h8.jsx)(`span`,{className:`mx-1.5 size-2 shrink-0 rounded-full`,style:{backgroundColor:t?`var(--color-text-danger)`:e?`var(--color-text-warning)`:`var(--color-text-info)`}})}"),
        ),
    ),
    "remote_project_label": (
        (
            b("function Kpr(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:e.label,path:e.remotePath,gitRepos:Zpr([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
            b("function Kpr(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:CPL({projectKind:`remote`,label:e.label,path:e.remotePath}),path:e.remotePath,gitRepos:Zpr([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
        ),
        (
            b("function MCr(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return jCr(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"),
            b("function CPL(e,t){let n=e.label?.trim(),r=t?.label?.trim(),i=e.path??e.remotePath;if(e.projectKind!==`remote`)return n??e.label;if(n&&IPs(n))return n;if(r&&IPs(r))return r;return typeof i===`string`&&IPs(rg(i))?rg(i):`Remote project`}function MCr(e,t,n){let r=new Map(t.map(e=>[e.projectId,e])),i=new Map(t.filter(e=>e.hostId!=null&&e.path!=null).map(e=>[e.hostId+`|`+e.path,e]));return jCr(e.map(e=>{let t=r.get(e.projectId)??i.get(e.hostId+`|`+e.path);return t==null?{...e,label:CPL(e),threadKeys:[]}:{...t,...e,label:CPL(e,t),threadKeys:t.threadKeys??[]}}),n)}"),
        ),
        (b("children:e.label}),i?.(e)]})},e.projectId)"), b("children:CPL(e)}),i?.(e)]})},e.projectId)")),
        (b("function uZo(e){return[e.label,e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}"), b("function uZo(e){return[CPL(e),e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}")),
        (b("function Nic(e){return[e.label,e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}"), b("function Nic(e){return[CPL(e),e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}")),
        (b("let j=A,M=j!=null&&n.projectKind!==j,N=n.label||w||T,"), b("let j=A,M=j!=null&&n.projectKind!==j,N=CPL(n)||w||T,")),
        (b("{folder:a.label||a.path||a.projectId}"), b("{folder:CPL(a)||a.path||a.projectId}")),
        (b("O=(r.path==null?void 0:h?.[r.path]?.trim())||r.label||r.projectId"), b("O=(r.path==null?void 0:h?.[r.path]?.trim())||CPL(r)||r.projectId")),
        (b("let c=n.label||n.path||n.projectId,l;"), b("let c=CPL(n)||n.path||n.projectId,l;")),
        (b("projectName:r.label,buttonClassName:`!h-5 !w-4 !p-0`"), b("projectName:CPL(r),buttonClassName:`!h-5 !w-4 !p-0`")),
        (b("v=r.label||rg(r.path);"), b("v=CPL(r)||rg(r.path);")),
    ),
}


INJECTED_GLOBAL_IDENTIFIER_COUNTS = {
    "priority_filter_recency_sorting": {"CPS": 3},
    "remote_project_label": {"CPL": 13},
}


# Exact official signatures for behaviours that 26.825.5331.0 already ships.
PROTECTED_OFFICIAL_SIGNATURES = (
    b("function CCr(e,t){return e===`waiting`||!t?e:`unread`}"),
    b("ce=W?.type===`local`?W.projectId:null;M?ce=n:g&&(ce=z??ce);"),
    b("function iac({activeProjectId:e,projects:t,remoteConnections:n,selectedRemoteProject:r})"),
)
