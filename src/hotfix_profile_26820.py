from __future__ import annotations


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Exact, hash-gated Microsoft Store 26.814.5517.0 frontend profile.
# The official 26.814.5517.0 bundle ships the priority click-hold machinery
# (pb hold map, g1t recorder, Hil/Nnn membership and the client-thread-id ->
# conversation-id migration) natively, so those behaviours are accepted as
# official and are intentionally NOT re-patched.  This profile changes only
# the behaviours that remain missing for the user:
#   1. Priority recency-only sorting, including live and pinned-item resorting.
#   2. Active heartbeat reminders remain in Priority without promoting ordinary
#      scheduled runs, and pinned notification dots take the danger colour.
#   3. Plan-pending yellow indicator (planImplementation is detected but the
#      sidebar indicator never renders a warning-coloured dot).
#   4. Remote/SSH project label (a UUID label is shown instead of the folder
#      name captured in the project path).
#   5. Priority project context survives compact thread-summary rendering.
PAIRS: dict[str, tuple[tuple[bytes, bytes], ...]] = {
    "automation_priority_gate": (
        (
            b(
                "t.attentionState!==e.attentionState||t.isScheduled!==e.isScheduled||t.kind"
                "===`task`&&e.kind===`task`&&t.threadEntry.key!==e.threadEntry.key?t:e"
            ),
            b(
                "t.attentionState!==e.attentionState||t.isScheduled!==e.isScheduled||t.h!==e.h||t.kind"
                "===`task`&&e.kind===`task`&&t.threadEntry.key!==e.threadEntry.key?t:e"
            ),
        ),
        (
            b(
                "function Hil(e,t,n){if(!Uil(e,t,n))return!1;if(t.attentionState!==`idle`)return!0;if(t.kind!==`task`)return!1;"
            ),
            b(
                "function Hil(e,t,n){if(!Uil(e,t,n))return!1;if(t.h)return!0;if(t.attentionState!==`idle`)return!0;if(t.kind!==`task`)return!1;"
            ),
        ),
        (
            b(
                "let c=Kil(e(tS,t),o);return c==null?[]:[{attentionState:e(Han,t),isUnread:s===`unread`,needsAttention:s===`waiting`||s===`unread`,item:{attentionState:s,isScheduled:e(wan,t)||c.kind===`local`&&c.conversationId!=null&&Gqc({automations:r,conversationId:c.conversationId})!=null,kind:`task`"
            ),
            b(
                "let c=Kil(e(tS,t),o),h=c?.kind===`local`&&c.conversationId!=null&&Gqc({automations:r,conversationId:c.conversationId})!=null;return c==null?[]:[{attentionState:e(Han,t),isUnread:s===`unread`,needsAttention:s===`waiting`||s===`unread`,item:{attentionState:s,isScheduled:e(wan,t)||h,h,kind:`task`"
            ),
        ),
    ),
    "priority_filter_recency_sorting": (
        (
            b(
                "function Mnn(e){return[...e].sort((e,t)=>Pnn[e.attentionState]-"
                "Pnn[t.attentionState]||t.recencyAt-e.recencyAt)}"
            ),
            b(
                "function Mnn(e){return[...e].sort((e,t)=>t.recencyAt-e.recencyAt)}"
                "function CodexPriorityStableRecencySort(e,t,n){return[...t].map((t,r)=>({item:t,index:r,"
                "recencyAt:n.get(t8(e,t))??0})).sort((e,t)=>t.recencyAt-e.recencyAt||"
                "e.index-t.index).map(({item:e})=>e)}"
            ),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b(
                "w=Lil(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter("
                "e=>!n.has(t8(l,e)))),T=l(Z6)===!0"
            ),
            b(
                "w=CodexPriorityStableRecencySort(l,Lil(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter("
                "e=>!n.has(t8(l,e)))),_),T=l(Z6)===!0"
            ),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b(
                "k=Lil(l,[...b,...l(sal,u.sidebarMode).filter(e=>{let t=t8(l,e);return!T||!E||"
                "!Hil(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(t8(l,e))&&Wil(l,e)));"
            ),
            b(
                "k=CodexPriorityStableRecencySort(l,Lil(l,[...b,...l(sal,u.sidebarMode).filter(e=>{let t=t8(l,e);return!T||!E||"
                "!Hil(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(t8(l,e))&&Wil(l,e))),_);"
            ),
        ),
    ),
    "priority_project_context_subtitle": (
        (
            b(
                "function Hjl(e){let t=(0,Gjl.c)(5),n=e.entryFallback?.kind===`local`?"
                "e.entryFallback:null,r;t[0]===n?r=t[1]:(r=n?.conversationId==null?null:{hostId:"
                "n.hostId??n.summary?.hostId??`local`,threadId:n.conversationId},t[0]=n,t[1]=r);"
                "let i=hs(Mjl,r)??e.secondaryContent,a;return t[2]!==e||t[3]!==i?(a=(0,e7.jsx)"
                "(ySl,{...e,secondaryContent:i}),t[2]=e,t[3]=i,t[4]=a):a=t[4],a}"
            ),
            b(
                "function Hjl(e){let t=(0,Gjl.c)(5),n=e.entryFallback?.kind===`local`?"
                "e.entryFallback:null,r;t[0]===n?r=t[1]:(r=n?.conversationId==null?null:{hostId:"
                "n.hostId??n.summary?.hostId??`local`,threadId:n.conversationId},t[0]=n,t[1]=r);"
                "let i=hs(Mjl,r),a=e.secondaryContent?.props?.projectGroup!=null,o=a?(i==null?"
                "e.secondaryContent:(0,e7.jsxs)(e7.Fragment,{children:[e.secondaryContent,` · `,i]})):"
                "i??e.secondaryContent,s;return t[2]!==e||t[3]!==o?(s=(0,e7.jsx)(ySl,{...e,"
                "secondaryContent:o}),t[2]=e,t[3]=o,t[4]=s):s=t[4],s}"
            ),
        ),
        (
            b(
                "titleSuffix:V&&n.conversation.gizmo_id!=null?(0,e7.jsx)(upl,{conversationId:e,"
                "projectId:n.conversation.gizmo_id}):void 0,secondaryContent:(0,e7.jsx)(apl,{"
                "chatGptConversationId:e,chatGptProjectId:n.conversation.gizmo_id??void 0,itemKind:"
                "n.isCloudTask?`cloud`:`chat`,projectGroup:null,sidebarMode:o}),wrapSecondaryContent:"
            ),
            b(
                "titleSuffix:void 0,secondaryContent:(0,e7.jsx)(apl,{chatGptConversationId:e,"
                "chatGptProjectId:n.conversation.gizmo_id??void 0,itemKind:n.isCloudTask?`cloud`:`chat`,"
                "projectGroup:null,sidebarMode:o}),wrapSecondaryContent:"
            ),
        ),
        (
            b(
                "titleSuffix:V?(0,e7.jsx)(upl,{conversationId:e}):void 0,secondaryContent:(0,e7.jsx)"
                "(apl,{chatGptConversationId:e,itemKind:n.isCloudTask?`cloud`:`chat`,projectGroup:null,"
                "sidebarMode:o}),wrapSecondaryContent:"
            ),
            b(
                "titleSuffix:void 0,secondaryContent:(0,e7.jsx)(apl,{chatGptConversationId:e,"
                "itemKind:n.isCloudTask?`cloud`:`chat`,projectGroup:null,sidebarMode:o}),"
                "wrapSecondaryContent:"
            ),
        ),
        (
            b(
                "titleSuffix:V&&n.projectGroup!=null?(0,e7.jsx)(lpl,{projectLabel:n.projectGroup.label}):"
                "void 0,secondaryContent:(0,e7.jsx)(apl,{itemKind:n.threadEntry.kind===`remote`?`cloud`:"
                "`local`,localConversationId:n.threadEntry.kind===`local`?n.threadEntry.conversationId:null,"
                "projectGroup:n.projectGroup,sidebarMode:o}),wrapSecondaryContent:"
            ),
            b(
                "titleSuffix:void 0,secondaryContent:(0,e7.jsx)(apl,{itemKind:n.threadEntry.kind===`remote`?"
                "`cloud`:`local`,localConversationId:n.threadEntry.kind===`local`?n.threadEntry.conversationId:"
                "null,projectGroup:n.projectGroup,sidebarMode:o}),wrapSecondaryContent:"
            ),
        ),
    ),
    "plan_pending_detection": (
        (
            b(
                "kt;t[19]!==je||t[20]!==Ae||t[21]!==Ne||t[22]!==Qe||t[23]!==Ct||"
                "t[24]!==se||t[25]!==nt||t[26]!==wt||t[27]!==$e?(kt=Ae?"
                "{type:`loading`}:{type:wt,unread:Ct?!1:(se??Qe===!0)||je&&(("
                "$e??0)>0||nt!=null||Ne),unreadCount:Ct||je?0:$e??0},"
                "t[19]=je,t[20]=Ae,t[21]=Ne,t[22]=Qe,t[23]=Ct,t[24]=se,"
                "t[25]=nt,t[26]=wt,t[27]=$e,t[28]=kt):kt=t[28]"
            ),
            b(
                "kt=Ae?{type:`loading`}:{type:wt,unread:Ct?!1:(se??Qe===!0)||je&&("
                "($e??0)>0||nt!=null||Ne),unreadCount:Ct||je?0:$e??0,"
                "plan:rt?.type===`implementPlan`,p:p===!0}"
            ),
        ),
        (
            b("allowActionsWhenDisabled:ot})"),
            b("allowActionsWhenDisabled:ot,p:b})"),
        ),
        (
            b("threadSummary:_e,dataAttributes:ve}=e"),
            b("threadSummary:_e,p,dataAttributes:ve}=e"),
        ),
    ),
    "plan_pending_yellow_indicator": (
        (
            b(
                "function y8(e){let t=(0,hdl.c)(4),{statusState:n}=e;if("
                "(n.unreadCount??0)>0){let e=n.unreadCount??0,r;return "
                "t[0]===e?r=t[1]:(r=(0,b8.jsx)(fdl,{count:e}),t[0]=e,t[1]=r),r}"
                "if(n.type===`loading`){let e;return t[2]===Symbol.for("
                "`react.memo_cache_sentinel`)?(e=(0,b8.jsx)(mdl,{}),t[2]=e):"
                "e=t[2],e}if(n.unread===!0){let e;return t[3]===Symbol.for("
                "`react.memo_cache_sentinel`)?(e=(0,b8.jsx)(pdl,{}),t[3]=e):"
                "e=t[3],e}return null}"
            ),
            b(
                "function y8({statusState:e}){return e.type===`loading`?(0,b8.jsx)(mdl,{}):"
                "e.plan?(0,b8.jsx)(pdl,{plan:!0,p:e.p}):(e.unreadCount??0)>0?"
                "(0,b8.jsx)(fdl,{count:e.unreadCount}):e.unread?(0,b8.jsx)(pdl,{plan:!1,p:e.p}):null}"
            ),
        ),
        (
            b(
                "function pdl(){let e=(0,hdl.c)(1),t;return e[0]===Symbol.for("
                "`react.memo_cache_sentinel`)?(t=(0,b8.jsx)(`div`,{className:"
                "`relative flex size-5 shrink-0 items-center justify-center "
                "text-codex-description`,children:(0,b8.jsx)(`span`,{className:"
                "`icon-xs relative scale-50`,children:(0,b8.jsx)(`span`,"
                "{className:`absolute inset-0 rounded-full`,style:{backgroundColor:"
                "`var(--color-text-info)`}})})}),e[0]=t):t=e[0],t}"
            ),
            b(
                "function pdl({plan:e,p:t}){return(0,b8.jsx)(`div`,{className:"
                "`relative flex size-5 shrink-0 items-center justify-center "
                "text-codex-description`,children:(0,b8.jsx)(`span`,{className:"
                "`icon-xs relative scale-50`,children:(0,b8.jsx)(`span`,"
                "{className:`absolute inset-0 rounded-full`,style:{backgroundColor:"
                "t?`var(--color-text-danger)`:e?`var(--color-text-warning)`:`var(--color-text-info)`}})})})}"
            ),
        ),
    ),
    "remote_project_label": (
        (
            b(
                "function Gnn(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));"
                "return Wnn(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"
            ),
            b(
                "function CPx(e){let t=e.label?.trim()??``,n=e.remotePath?.split(/[/\\\\]+/).filter(Boolean).pop(),r=e.projectId??e.id??``;return!e.remotePath||t&&t!==r&&!/^[\\da-f-]{36}$/i.test(t)?t:n||t||r}"
                "function Gnn(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));"
                "return Wnn(e.map(e=>{let t=r.get(e.projectId);return t==null?"
                "{...e,threadKeys:[]}:{...t,label:t.label}}),n)}"
            ),
        ),
        (
            b("label:e.label,path:e.remotePath,gitRepos:hrn([e.remotePath],n?.[e.hostId]??[]),"),
            b("label:CPx(e),path:e.remotePath,gitRepos:hrn([e.remotePath],n?.[e.hostId]??[]),"),
        ),
    ),
}


# The builder verifies the token-level absence of these identifiers in the
# official entry and their exact occurrence count in the patched entry.
# CPx is defined once and applied at the remote-project normalization boundary.
INJECTED_GLOBAL_IDENTIFIER_COUNTS = {
    "priority_filter_recency_sorting": {
        "CodexPriorityStableRecencySort": 3,
    },
    "remote_project_label": {
        "CPx": 2,
    },
}


# These official 26.814.5517.0 signatures implement the priority click-hold
# machinery.  They must remain byte-identical; any change rejects the build.
PROTECTED_OFFICIAL_SIGNATURES = (
    b("function Nnn(e,t){return e===`waiting`||!t?e:`unread`}"),
    b(
        "function g1t(e,t,n){let r=w1t(e,t),i=e.get(fb),a=_1t(e,r),o=i==null?"
        "null:_1t(e,i),s=i!=null&&(i===r||a!=null&&a===o)?i:r,c=new Map(e.get(pb));"
        "c.set(s,n),e.set(pb,c)}"
    ),
    b(
        "M=M.map(e=>{let t=_on({items:e.threadKeys.flatMap(e=>{let t=P.get(e);"
        "return t==null?[]:[t]}),attentionStateByThreadKey:g,manualOrder:y?.[e.projectId]??"
        "R(e),sortMode:j}),n=Con(e.threadKeys,t);return n===e.threadKeys?e:{...e,threadKeys:n}}),"
        "N=_on({items:N.flatMap(e=>{let t=P.get(e);"
    ),
)
