from __future__ import annotations


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Rebased onto OpenAI.Codex 26.908.4834.0 from the 26.903.9818.0 baseline.
PAIRS = {
    "automation_priority_gate": (
        (
            b("function m6(e,t,n){if(t.isScheduled&&e(IIo)!==!0)return!1;"),
            b("function m6(e,t,n){if(t.isScheduled&&e(IIo)&&t.attentionState===`idle`)return!1;"),
        ),
    ),
    "priority_filter_recency_sorting": (
        (
            b("function iV(e){return[...e].sort((e,t)=>e9r[e.attentionState]-e9r[t.attentionState]||t.recencyAt-e.recencyAt)}"),
            b("function iV(e,t=(e,t)=>t.recencyAt-e.recencyAt){return[...e].sort(t)}"),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b("C=h==null?void 0:S.find(({item:e})=>{let t=h6(l,e);return t===h6(l,h.item)&&!p.has(t)})?.item,"),
            b("C=((e,t)=>(_.get(h6(l,t))||0)-(_.get(h6(l,e))||0)),"),
        ),
        (
            b("w=$Io(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>!n.has(h6(l,e)))),T=l(f6)===!0"),
            b("w=iV($Io(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(h6(l,e)))),C),T=l(f6)===!0"),
        ),
        (
            b("k=$Io(l,[...b,...l(SLo,u.sidebarMode).filter(e=>{let t=h6(l,e);return!T||!E||!iLo(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(h6(l,e))&&aLo(l,e)));"),
            b("k=iV($Io(l,[...b,...l(SLo,u.sidebarMode).filter(e=>{let t=h6(l,e);return!T||!E||!iLo(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(h6(l,e))&&aLo(l,e))),C);"),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b("SLo=rm(Q,(e,{get:t})=>_6(t,e).filter(({item:n})=>m6(t,n,e)&&aLo(t,n)).map(({item:e})=>e))"),
            b("SLo=rm(Q,(e,{get:t})=>iV(_6(t,e).filter(({item:n})=>m6(t,n,e)&&aLo(t,n))).map(({item:e})=>e))"),
        ),
    ),
    "project_sorting": (
        (
            b("projectOrder:u,serverOrderedPinnedThreadHostIds:d"),
            b("projectOrder:u,projectSortMode:q,serverOrderedPinnedThreadHostIds:d"),
        ),
        (
            b("let C=vei(v,u,`start`),w=new Set(C);"),
            b("let P=e=>{let t=e.kind==`project`?m.filter(t=>t.projectKey==e.key):[e];return[e,Math.max(...t.map(e=>e.recencyAt)),Math.min(...t.map(e=>e9r[e.prioritySortAttentionState??e.attentionState]))]},C=q[0]==`m`?vei(v,u,`start`):v.map(P).sort((e,t)=>q[0]==`p`?e[2]-t[2]||t[1]-e[1]:t[1]-e[1]).map(e=>e[0].key),w=new Set(C);"),
        ),
        (
            b("pinnedKeys:mei({entries:h,pinnedKeyAliases:s,pinnedOrder:c,pinnedSortMode:l,serverOrderedPinnedThreadHostIds:d"),
            b("pinnedKeys:mei({entries:h,pinnedKeyAliases:s,pinnedOrder:l===`manual`?c:h.map(P).sort((e,t)=>t[1]-e[1]).map(e=>e[0].key),pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:d"),
        ),
    ),
    "plan_pending_yellow_indicator": (
        (
            b("function xCo(e){let t=(0,TCo.c)(5),{statusState:n,size:r}=e,i=r===void 0?`compact`:r;if((n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r=(0,f3.jsx)(SCo,{count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t[2]===i?e=t[3]:(e=(0,f3.jsx)(wCo,{size:i}),t[2]=i,t[3]=e),e}if(n.unread===!0){let e;return t[4]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,f3.jsx)(CCo,{}),t[4]=e):e=t[4],e}return null}"),
            b("function xCo({statusState:e,size:t}){let n=e.unreadCount||e.unread,r=e.i&&(e.p||n)?`danger`:e.p?`#eab308`:n?`info`:null,i=f3.jsx;return e.type===`loading`?i(wCo,{size:t}):r&&i(CCo,{c:r})}"),
        ),
        (
            b("function CCo(){let e=(0,TCo.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`)?(t=(0,f3.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-codex-description`,children:(0,f3.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,f3.jsx)(`span`,{className:`absolute inset-0 rounded-full bg-info-solid`})})}),e[0]=t):t=e[0],t}"),
            b("function CCo({c:e}){return f3.jsx(`i`,{className:`mx-1.5 size-2 shrink-0 rounded-full`,style:{background:e[0]===`#`?e:`var(--color-text-${e})`}})}"),
        ),
    ),
    "remote_project_label": (
        (
            b("function s2r(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:e.label,path:e.remotePath,gitRepos:f2r([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
            b("function qZx(e,t){return e.label!=e.id&&e.label||e.remotePath.split(`/`).pop()||t||`Remote`}function s2r(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:qZx(e,r.get(e.hostId)),path:e.remotePath,gitRepos:f2r([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
        ),
        (
            b("function c9r(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return s9r(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"),
            b("function c9r(e,t,n){return s9r(e.map(e=>{let n=t.find(t=>t.projectId==e.projectId||t.hostId==e.hostId&&uh(t.path)==uh(e.path));return{...n,...e,threadKeys:n?.threadKeys||[]}}),n)}"),
        ),
    ),
    "work_remote_project_picker": (
        (
            b("a=t??[],"),
            b("a=t?.map(e=>({...e,label:qZx(e)}))||[],"),
        ),
    ),
}

SECONDARY_ENTRY_PATH = "webview/assets/app-primary-17b54400f32a.js"
SECONDARY_ENTRY_SOURCE_SHA256 = "8b57b72037a6478e5e2959b8e124469433f3bc19249c14f9a4dfb1f56ef8d7e7"
SECONDARY_PAIRS = {
    "plan_pending_detection": (
        (
            b("navigationState:d,onDoubleClick:f,isActive:p,isGrouped:m"),
            b("navigationState:d,onDoubleClick:f,isActive:p,P:Q,isGrouped:m"),
        ),
        (
            b("t[22]!==Pt||t[23]!==Ft||t[24]!==It"),
            b("t[22]===t[22]"),
        ),
        (
            b("unreadCount:It}"),
            b("unreadCount:It,p:st?.type===`implementPlan`,i:!!Q}"),
        ),
        (
            b("t[131]!==lt||t[132]!==w"),
            b("t[131]!=2*lt+b||t[132]!==w"),
        ),
        (
            b("disableEnvTooltip:!0,isActive:ce,isUnread:a"),
            b("disableEnvTooltip:!0,isActive:ce,P:b,isUnread:a"),
        ),
        (
            b("t[131]=lt,t[132]=w"),
            b("t[131]=2*lt+b,t[132]=w"),
        ),
    ),
    "project_sorting": (
        (
            b("pinnedSortMode:W,projectOrder:G,serverOrderedPinnedThreadHostIds"),
            b("pinnedSortMode:W,projectOrder:G,projectSortMode:k,serverOrderedPinnedThreadHostIds"),
        ),
    ),
}

ATTESTATION_LOG_BRIDGE_IDENTIFIER = "h"
ATTESTATION_LOG_BRIDGE_SIGNATURES = (
    b("function jms(){h.dispatchMessage(`view-focused`,{})}"),
    b("h.dispatchMessage(`log-message`,{level:`info`,message:`[startup][renderer] app routes mounted after ${Math.round(performance.now())}ms`}),h.dispatchMessage(`ready`,{persistedStateResponsePriority:i7?`critical`:void 0})"),
)

OFFICIAL_FEATURE_SIGNATURES = {
    "priority_filter_hold_membership": (
        b("function iLo(e,t,n){if(!m6(e,t,n))return!1;"),
        b("xLo=rm(Q,(e,{get:t})=>iV(_6(t,e).filter(({item:n})=>iLo(t,n,e))))"),
    ),
    "priority_identity_migration": (
        b("function t9r({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n}){"),
    ),
    "priority_project_context_subtitle": (
        b("function f9r({chatLabel:e,task:t,projectLabel:n"),
    ),
    "active_priority_sort": (
        b("function Qmi({items:e,attentionStateByThreadKey:t}){"),
        b("function $mi({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r}){"),
    ),
    "pinned_priority_sync": (
        b("function t9r({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n}){"),
    ),
    "resume_history_on_demand": (
        b("function Iwn(e){return e.resumeState===`resumed`&&("),
    ),
    "paginated_tail_retention": (
        b("function Fwn(e){return mT(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}"),
    ),
    "idle_history_eviction": (
        b("function zHt({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a"),
    ),
}

SECONDARY_OFFICIAL_FEATURE_SIGNATURES = {
    "priority_click_hold": (
        b("function j6t(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a})"),
    ),
    "new_chat_file_drop": (
        b("onDrop:e=>{if(!N||!e_(e.dataTransfer))return;"),
    ),
    "archived_heartbeat_terminal_guard": (
        b("function hU(e){let t=(0,U2t.c)(41),{heartbeatAutomationName:n,isRunning:r,open:i,onOpenChange:a,onConfirm:o}=e"),
        b("defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat confirmation dialog when the chat has an active heartbeat automation`}):(0,"),
    ),
}

PROTECTED_OFFICIAL_SIGNATURES = tuple(
    signature
    for signatures in OFFICIAL_FEATURE_SIGNATURES.values()
    for signature in signatures
)

