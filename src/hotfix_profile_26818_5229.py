from __future__ import annotations


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Exact, hash-gated Microsoft Store 26.818.5229.0 frontend profile.
# This is a semantic rebase of the retained Priority, plan-indicator and
# remote-project-label behaviour onto app-initial-BhpTek7p.js. Every source
# signature is unique in the exact official entry; no version-only fallback is
# permitted.
PAIRS: dict[str, tuple[tuple[bytes, bytes], ...]] = {
    "automation_priority_gate": (
        (
            b(
                "if(t.isScheduled&&e(aml)!==!0)return!1;"
            ),
            b(
                "if(t.isScheduled&&t.attentionState===`idle`&&e(aml)!==!0)return!1;"
            ),
        ),
    ),
    "priority_filter_recency_sorting": (
        (
            b(
                "function pan(e){return[...e].sort((e,t)=>han[e.attentionState]-"
                "han[t.attentionState]||t.recencyAt-e.recencyAt)}"
            ),
            b(
                "function pan(e){return[...e].sort((e,t)=>t.recencyAt-e.recencyAt)}"
                "function CPS(e,t,n){return[...t].map((t,r)=>[t,r,n.get(n8(e,t))??0]).sort((e,t)=>"
                "t[2]-e[2]||e[1]-t[1]).map(e=>e[0])}"
            ),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b(
                "w=Jhl(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter("
                "e=>!n.has(n8(l,e)))),T=l(Q6)===!0"
            ),
            b(
                "w=CPS(l,Jhl(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter("
                "e=>!n.has(n8(l,e)))),_),T=l(Q6)===!0"
            ),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b(
                "k=Jhl(l,[...b,...l(vgl,u.sidebarMode).filter(e=>{let t=n8(l,e);return!T||!E||"
                "!$hl(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(n8(l,e))&&tgl(l,e)));"
            ),
            b(
                "k=CPS(l,Jhl(l,[...b,...l(vgl,u.sidebarMode).filter(e=>{let t=n8(l,e);return!T||!E||"
                "!$hl(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(n8(l,e))&&tgl(l,e))),_);"
            ),
        ),
    ),
    "priority_project_context_subtitle": (
        (
            b(
                "function KHl(e){let t=(0,YHl.c)(5),n=e.entryFallback?.kind===`local`?"
                "e.entryFallback:null,r;t[0]===n?r=t[1]:(r=n?.conversationId==null?null:{hostId:"
                "n.hostId??n.summary?.hostId??`local`,threadId:n.conversationId},t[0]=n,t[1]=r);"
                "let i=hs(FHl,r)??e.secondaryContent,a;return t[2]!==e||t[3]!==i?(a=(0,e7.jsx)"
                "(CNl,{...e,secondaryContent:i}),t[2]=e,t[3]=i,t[4]=a):a=t[4],a}"
            ),
            b(
                "function KHl(e){let t=(0,YHl.c)(5),n=e.entryFallback?.kind===`local`?"
                "e.entryFallback:null,r;t[0]===n?r=t[1]:(r=n?.conversationId==null?null:{hostId:"
                "n.hostId??n.summary?.hostId??`local`,threadId:n.conversationId},t[0]=n,t[1]=r);"
                "let i=hs(FHl,r),a=e.secondaryContent?.props?.projectGroup!=null,o=a?(i==null?"
                "e.secondaryContent:(0,e7.jsxs)(e7.Fragment,{children:[e.secondaryContent,` · `,i]})):"
                "i??e.secondaryContent,s;return t[2]!==e||t[3]!==o?(s=(0,e7.jsx)(CNl,{...e,"
                "secondaryContent:o}),t[2]=e,t[3]=o,t[4]=s):s=t[4],s}"
            ),
        ),
        (
            b(
                "titleSuffix:V&&n.conversation.gizmo_id!=null?(0,e7.jsx)(vwl,{conversationId:e,"
                "projectId:n.conversation.gizmo_id}):void 0,secondaryContent:(0,e7.jsx)(pwl,{"
                "chatGptConversationId:e,chatGptProjectId:n.conversation.gizmo_id??void 0,itemKind:"
                "n.isCloudTask?`cloud`:`chat`,projectGroup:null,sidebarMode:o}),wrapSecondaryContent:"
            ),
            b(
                "titleSuffix:void 0,secondaryContent:(0,e7.jsx)(pwl,{chatGptConversationId:e,"
                "chatGptProjectId:n.conversation.gizmo_id??void 0,itemKind:n.isCloudTask?`cloud`:`chat`,"
                "projectGroup:null,sidebarMode:o}),wrapSecondaryContent:"
            ),
        ),
        (
            b(
                "titleSuffix:V?(0,e7.jsx)(vwl,{conversationId:e}):void 0,secondaryContent:(0,e7.jsx)"
                "(pwl,{chatGptConversationId:e,itemKind:n.isCloudTask?`cloud`:`chat`,projectGroup:null,"
                "sidebarMode:o}),wrapSecondaryContent:"
            ),
            b(
                "titleSuffix:void 0,secondaryContent:(0,e7.jsx)(pwl,{chatGptConversationId:e,"
                "itemKind:n.isCloudTask?`cloud`:`chat`,projectGroup:null,sidebarMode:o}),"
                "wrapSecondaryContent:"
            ),
        ),
        (
            b(
                "titleSuffix:V&&n.projectGroup!=null?(0,e7.jsx)(_wl,{projectLabel:n.projectGroup.label}):"
                "void 0,secondaryContent:(0,e7.jsx)(pwl,{itemKind:n.threadEntry.kind===`remote`?`cloud`:"
                "`local`,localConversationId:n.threadEntry.kind===`local`?n.threadEntry.conversationId:null,"
                "projectGroup:n.projectGroup,sidebarMode:o}),wrapSecondaryContent:"
            ),
            b(
                "titleSuffix:void 0,secondaryContent:(0,e7.jsx)(pwl,{itemKind:n.threadEntry.kind===`remote`?"
                "`cloud`:`local`,localConversationId:n.threadEntry.kind===`local`?n.threadEntry.conversationId:"
                "null,projectGroup:n.projectGroup,sidebarMode:o}),wrapSecondaryContent:"
            ),
        ),
    ),
    "plan_pending_detection": (
        (
            b(
                "Dt;t[19]!==je||t[20]!==Ae||t[21]!==Ne||t[22]!==Qe||t[23]!==Ct||"
                "t[24]!==se||t[25]!==nt||t[26]!==wt||t[27]!==$e?(Dt=Ae?"
                "{type:`loading`}:{type:wt,unread:Ct?!1:(se??Qe===!0)||je&&(("
                "$e??0)>0||nt!=null||Ne),unreadCount:Ct||je?0:$e??0},"
                "t[19]=je,t[20]=Ae,t[21]=Ne,t[22]=Qe,t[23]=Ct,t[24]=se,"
                "t[25]=nt,t[26]=wt,t[27]=$e,t[28]=Dt):Dt=t[28]"
            ),
            b(
                "Dt=Ae?{type:`loading`}:{type:wt,unread:Ct?!1:(se??Qe===!0)||je&&("
                "($e??0)>0||nt!=null||Ne),unreadCount:Ct||je?0:$e??0,"
                "plan:rt?.type===`implementPlan`,pinned:Pi===!0}"
            ),
        ),
        (
            b("threadSummary:w,..._e,renderActions:ht,allowActionsWhenDisabled:ct})"),
            b("threadSummary:w,..._e,renderActions:ht,allowActionsWhenDisabled:ct,pinned:b})"),
        ),
        (
            b("threadSummary:_e,dataAttributes:ve}=e"),
            b("threadSummary:_e,pinned:Pi,dataAttributes:ve}=e"),
        ),
    ),
    "plan_pending_yellow_indicator": (
        (
            b(
                "function b8(e){let t=(0,CSl.c)(4),{statusState:n}=e;if("
                "(n.unreadCount??0)>0){let e=n.unreadCount??0,r;return "
                "t[0]===e?r=t[1]:(r=(0,x8.jsx)(bSl,{count:e}),t[0]=e,t[1]=r),r}"
                "if(n.type===`loading`){let e;return t[2]===Symbol.for("
                "`react.memo_cache_sentinel`)?(e=(0,x8.jsx)(SSl,{}),t[2]=e):"
                "e=t[2],e}if(n.unread===!0){let e;return t[3]===Symbol.for("
                "`react.memo_cache_sentinel`)?(e=(0,x8.jsx)(xSl,{}),t[3]=e):"
                "e=t[3],e}return null}"
            ),
            b(
                "function b8({statusState:e}){return e.type===`loading`?(0,x8.jsx)(SSl,{}):"
                "e.plan?(0,x8.jsx)(xSl,{plan:!0,pinned:e.pinned}):(e.unreadCount??0)>0?"
                "(0,x8.jsx)(bSl,{count:e.unreadCount}):e.unread?(0,x8.jsx)(xSl,{plan:!1,pinned:e.pinned}):null}"
            ),
        ),
        (
            b(
                "function xSl(){let e=(0,CSl.c)(1),t;return e[0]===Symbol.for("
                "`react.memo_cache_sentinel`)?(t=(0,x8.jsx)(`div`,{className:"
                "`relative flex size-5 shrink-0 items-center justify-center "
                "text-codex-description`,children:(0,x8.jsx)(`span`,{className:"
                "`icon-xs relative scale-50`,children:(0,x8.jsx)(`span`,"
                "{className:`absolute inset-0 rounded-full`,style:{backgroundColor:"
                "`var(--color-text-info)`}})})}),e[0]=t):t=e[0],t}"
            ),
            b(
                "function xSl({plan:e,pinned:t}){return(0,x8.jsx)(`span`,{className:"
                "`mx-1.5 size-2 shrink-0 rounded-full`,style:{backgroundColor:"
                "t?`var(--color-text-danger)`:e?`var(--color-text-warning)`:`var(--color-text-info)`}})}"
            ),
        ),
    ),
    "remote_project_label": (
        (
            b(
                "function Gan(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));"
                "return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,"
                "hostDisplayName:r.get(e.hostId)??null,label:e.label,path:e.remotePath,"
                "gitRepos:Xan([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"
            ),
            b(
                "function Gan(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));"
                "return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,"
                "hostDisplayName:r.get(e.hostId)??null,label:pPt(e.label)?hp(e.remotePath):e.label,path:e.remotePath,"
                "gitRepos:Xan([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"
            ),
        ),
        (
            b(
                "function Ean(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));"
                "return Tan(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"
            ),
            b(
                "function Ean(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return Tan(e.map(e=>{let n=r.get(e.projectId);return n==null?{...e,threadKeys:[]}:{...n,label:e.label}}),n)}"
            ),
        ),
        (
            b("function Ean(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));"),
            b("function CPL(e){return e.projectKind===`remote`&&pPt(e.label)?hp(e.path):e.label}function Ean(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));"),
        ),
        (
            b("children:e.label}),i?.(e)]})},e.projectId)"),
            b("children:CPL(e)}),i?.(e)]})},e.projectId)"),
        ),
        (
            b("function ool(e){return[e.label,e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}"),
            b("function ool(e){return[CPL(e),e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}"),
        ),
        (
            b("let j=A,M=j!=null&&n.projectKind!==j,N=n.label||w||T,"),
            b("let j=A,M=j!=null&&n.projectKind!==j,N=CPL(n)||w||T,"),
        ),
        (
            b("{folder:a.label||a.path||a.projectId}"),
            b("{folder:CPL(a)||a.path||a.projectId}"),
        ),
        (
            b("O=(r.path==null?void 0:h?.[r.path]?.trim())||r.label||r.projectId"),
            b("O=(r.path==null?void 0:h?.[r.path]?.trim())||CPL(r)||r.projectId"),
        ),
        (
            b("let c=n.label||n.path||n.projectId,l;"),
            b("let c=CPL(n)||n.path||n.projectId,l;"),
        ),
        (
            b("projectName:r.label,buttonClassName:`!h-5 !w-4 !p-0`"),
            b("projectName:CPL(r),buttonClassName:`!h-5 !w-4 !p-0`"),
        ),
        (
            b("v=r.label||IMe(r.path);"),
            b("v=CPL(r)||IMe(r.path);"),
        ),
    ),
    "work_remote_project_picker": (
        (
            b("p=f?.type===`local`?f.projectId:null"),
            b("p=f?.type===`local`||f?.type===`remote`?f.projectId:null"),
        ),
        (
            b("d=Y(M4s)"),
            b("d=Y(T4s).filter(e=>!xca(e))"),
        ),
        (
            b("GW(u,{...e,projectKind:`local`})"),
            b("GW(u,e)"),
        ),
    ),
}


INJECTED_GLOBAL_IDENTIFIER_COUNTS = {
    "priority_filter_recency_sorting": {"CPS": 3},
    "remote_project_label": {"CPL": 9},
}


PROTECTED_OFFICIAL_SIGNATURES = (
    b("function man(e,t){return e===`waiting`||!t?e:`unread`}"),
    b(
        "function OXt(e,t,n){let r=LXt(e,t),i=e.get(Uy),a=kXt(e,r),o=i==null?"
        "null:kXt(e,i),s=i!=null&&(i===r||a!=null&&a===o)?i:r,c=new Map(e.get(Wy));"
        "c.set(s,n),e.set(Wy,c)}"
    ),
    b(
        "M=M.map(e=>{let t=$cn({items:e.threadKeys.flatMap(e=>{let t=P.get(e);"
        "return t==null?[]:[t]}),attentionStateByThreadKey:g,manualOrder:y?.[e.projectId]??"
        "R(e),sortMode:j}),n=aln(e.threadKeys,t);return n===e.threadKeys?e:{...e,threadKeys:n}}),"
        "N=$cn({items:N.flatMap(e=>{let t=P.get(e);"
    ),
)
