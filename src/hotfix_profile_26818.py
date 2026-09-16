from __future__ import annotations


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Exact, hash-gated Microsoft Store 26.818.3698.0 frontend profile.
# This is a semantic rebase of the 26.814 profile onto app-initial-izy3qYQi.js.
# Every replacement is unique in the exact official entry; no version-only or
# unsupported-means-fixed fallback is permitted.
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
                "function Jml(e,t,n){if(!Yml(e,t,n))return!1;if(t.attentionState!==`idle`)return!0;if(t.kind!==`task`)return!1;"
            ),
            b(
                "function Jml(e,t,n){if(!Yml(e,t,n))return!1;if(t.h)return!0;if(t.attentionState!==`idle`)return!0;if(t.kind!==`task`)return!1;"
            ),
        ),
        (
            b(
                "let c=Qml(e(Hx,t),o);return c==null?[]:[{attentionState:e(mcn,t),isUnread:s===`unread`,needsAttention:s===`waiting`||s===`unread`,item:{attentionState:s,isScheduled:e(Xsn,t)||c.kind===`local`&&c.conversationId!=null&&c3c({automations:r,conversationId:c.conversationId})!=null,kind:`task`"
            ),
            b(
                "let c=Qml(e(Hx,t),o),h=c?.kind===`local`&&c.conversationId!=null&&c3c({automations:r,conversationId:c.conversationId})!=null;return c==null?[]:[{attentionState:e(mcn,t),isUnread:s===`unread`,needsAttention:s===`waiting`||s===`unread`,item:{attentionState:s,isScheduled:e(Xsn,t)||h,h,kind:`task`"
            ),
        ),
    ),
    "priority_filter_recency_sorting": (
        (
            b(
                "function ran(e){return[...e].sort((e,t)=>aan[e.attentionState]-"
                "aan[t.attentionState]||t.recencyAt-e.recencyAt)}"
            ),
            b(
                "function ran(e){return[...e].sort((e,t)=>t.recencyAt-e.recencyAt)}"
                "function CPS(e,t,n){return[...t].map((t,r)=>({item:t,index:r,"
                "recencyAt:n.get(t8(e,t))??0})).sort((e,t)=>t.recencyAt-e.recencyAt||"
                "e.index-t.index).map(({item:e})=>e)}"
            ),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b(
                "w=Uml(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter("
                "e=>!n.has(t8(l,e)))),T=l(Z6)===!0"
            ),
            b(
                "w=CPS(l,Uml(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter("
                "e=>!n.has(t8(l,e)))),_),T=l(Z6)===!0"
            ),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b(
                "k=Uml(l,[...b,...l(phl,u.sidebarMode).filter(e=>{let t=t8(l,e);return!T||!E||"
                "!Jml(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(t8(l,e))&&Xml(l,e)));"
            ),
            b(
                "k=CPS(l,Uml(l,[...b,...l(phl,u.sidebarMode).filter(e=>{let t=t8(l,e);return!T||!E||"
                "!Jml(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(t8(l,e))&&Xml(l,e))),_);"
            ),
        ),
    ),
    "priority_project_context_subtitle": (
        (
            b(
                "function VVl(e){let t=(0,WVl.c)(5),n=e.entryFallback?.kind===`local`?"
                "e.entryFallback:null,r;t[0]===n?r=t[1]:(r=n?.conversationId==null?null:{hostId:"
                "n.hostId??n.summary?.hostId??`local`,threadId:n.conversationId},t[0]=n,t[1]=r);"
                "let i=hs(AVl,r)??e.secondaryContent,a;return t[2]!==e||t[3]!==i?(a=(0,$5.jsx)"
                "(vMl,{...e,secondaryContent:i}),t[2]=e,t[3]=i,t[4]=a):a=t[4],a}"
            ),
            b(
                "function VVl(e){let t=(0,WVl.c)(5),n=e.entryFallback?.kind===`local`?"
                "e.entryFallback:null,r;t[0]===n?r=t[1]:(r=n?.conversationId==null?null:{hostId:"
                "n.hostId??n.summary?.hostId??`local`,threadId:n.conversationId},t[0]=n,t[1]=r);"
                "let i=hs(AVl,r),a=e.secondaryContent?.props?.projectGroup!=null,o=a?(i==null?"
                "e.secondaryContent:(0,$5.jsxs)($5.Fragment,{children:[e.secondaryContent,` · `,i]})):"
                "i??e.secondaryContent,s;return t[2]!==e||t[3]!==o?(s=(0,$5.jsx)(vMl,{...e,"
                "secondaryContent:o}),t[2]=e,t[3]=o,t[4]=s):s=t[4],s}"
            ),
        ),
        (
            b(
                "titleSuffix:V&&n.conversation.gizmo_id!=null?(0,$5.jsx)(pCl,{conversationId:e,"
                "projectId:n.conversation.gizmo_id}):void 0,secondaryContent:(0,$5.jsx)(cCl,{"
                "chatGptConversationId:e,chatGptProjectId:n.conversation.gizmo_id??void 0,itemKind:"
                "n.isCloudTask?`cloud`:`chat`,projectGroup:null,sidebarMode:o}),wrapSecondaryContent:"
            ),
            b(
                "titleSuffix:void 0,secondaryContent:(0,$5.jsx)(cCl,{chatGptConversationId:e,"
                "chatGptProjectId:n.conversation.gizmo_id??void 0,itemKind:n.isCloudTask?`cloud`:`chat`,"
                "projectGroup:null,sidebarMode:o}),wrapSecondaryContent:"
            ),
        ),
        (
            b(
                "titleSuffix:V?(0,$5.jsx)(pCl,{conversationId:e}):void 0,secondaryContent:(0,$5.jsx)"
                "(cCl,{chatGptConversationId:e,itemKind:n.isCloudTask?`cloud`:`chat`,projectGroup:null,"
                "sidebarMode:o}),wrapSecondaryContent:"
            ),
            b(
                "titleSuffix:void 0,secondaryContent:(0,$5.jsx)(cCl,{chatGptConversationId:e,"
                "itemKind:n.isCloudTask?`cloud`:`chat`,projectGroup:null,sidebarMode:o}),"
                "wrapSecondaryContent:"
            ),
        ),
        (
            b(
                "titleSuffix:V&&n.projectGroup!=null?(0,$5.jsx)(fCl,{projectLabel:n.projectGroup.label}):"
                "void 0,secondaryContent:(0,$5.jsx)(cCl,{itemKind:n.threadEntry.kind===`remote`?`cloud`:"
                "`local`,localConversationId:n.threadEntry.kind===`local`?n.threadEntry.conversationId:null,"
                "projectGroup:n.projectGroup,sidebarMode:o}),wrapSecondaryContent:"
            ),
            b(
                "titleSuffix:void 0,secondaryContent:(0,$5.jsx)(cCl,{itemKind:n.threadEntry.kind===`remote`?"
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
                "function y8(e){let t=(0,vxl.c)(4),{statusState:n}=e;if("
                "(n.unreadCount??0)>0){let e=n.unreadCount??0,r;return "
                "t[0]===e?r=t[1]:(r=(0,b8.jsx)(hxl,{count:e}),t[0]=e,t[1]=r),r}"
                "if(n.type===`loading`){let e;return t[2]===Symbol.for("
                "`react.memo_cache_sentinel`)?(e=(0,b8.jsx)(_xl,{}),t[2]=e):"
                "e=t[2],e}if(n.unread===!0){let e;return t[3]===Symbol.for("
                "`react.memo_cache_sentinel`)?(e=(0,b8.jsx)(gxl,{}),t[3]=e):"
                "e=t[3],e}return null}"
            ),
            b(
                "function y8({statusState:e}){return e.type===`loading`?(0,b8.jsx)(_xl,{}):"
                "e.plan?(0,b8.jsx)(gxl,{plan:!0,pinned:e.pinned}):(e.unreadCount??0)>0?"
                "(0,b8.jsx)(hxl,{count:e.unreadCount}):e.unread?(0,b8.jsx)(gxl,{plan:!1,pinned:e.pinned}):null}"
            ),
        ),
        (
            b(
                "function gxl(){let e=(0,vxl.c)(1),t;return e[0]===Symbol.for("
                "`react.memo_cache_sentinel`)?(t=(0,b8.jsx)(`div`,{className:"
                "`relative flex size-5 shrink-0 items-center justify-center "
                "text-codex-description`,children:(0,b8.jsx)(`span`,{className:"
                "`icon-xs relative scale-50`,children:(0,b8.jsx)(`span`,"
                "{className:`absolute inset-0 rounded-full`,style:{backgroundColor:"
                "`var(--color-text-info)`}})})}),e[0]=t):t=e[0],t}"
            ),
            b(
                "function gxl({plan:e,pinned:t}){return(0,b8.jsx)(`div`,{className:"
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
                "function gan(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));"
                "return han(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"
            ),
            b(
                "function CPx(e){let t=e.label?.trim()??``,n=e.remotePath?.split(/[/\\\\]+/).filter(Boolean).pop(),r=e.projectId??e.id??``;return!e.remotePath||t&&t!==r&&!/^[\\da-f-]{36}$/i.test(t)?t:n||t||r}"
                "function gan(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));"
                "return han(e.map(e=>{let t=r.get(e.projectId);return t==null?"
                "{...e,threadKeys:[]}:{...t,label:t.label}}),n)}"
            ),
        ),
        (
            b("label:e.label,path:e.remotePath,gitRepos:Ban([e.remotePath],n?.[e.hostId]??[]),"),
            b("label:CPx(e),path:e.remotePath,gitRepos:Ban([e.remotePath],n?.[e.hostId]??[]),"),
        ),
    ),
}


INJECTED_GLOBAL_IDENTIFIER_COUNTS = {
    "priority_filter_recency_sorting": {
        "CPS": 3,
    },
    "remote_project_label": {
        "CPx": 2,
    },
}


PROTECTED_OFFICIAL_SIGNATURES = (
    b("function ian(e,t){return e===`waiting`||!t?e:`unread`}"),
    b(
        "function bXt(e,t,n){let r=kXt(e,t),i=e.get(qy),a=xXt(e,r),o=i==null?"
        "null:xXt(e,i),s=i!=null&&(i===r||a!=null&&a===o)?i:r,c=new Map(e.get(Jy));"
        "c.set(s,n),e.set(Jy,c)}"
    ),
    b(
        "M=M.map(e=>{let t=Ucn({items:e.threadKeys.flatMap(e=>{let t=P.get(e);"
        "return t==null?[]:[t]}),attentionStateByThreadKey:g,manualOrder:y?.[e.projectId]??"
        "R(e),sortMode:j}),n=Ycn(e.threadKeys,t);return n===e.threadKeys?e:{...e,threadKeys:n}}),"
        "N=Ucn({items:N.flatMap(e=>{let t=P.get(e);"
    ),
)
