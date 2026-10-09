from __future__ import annotations


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Exact semantic rebase for OpenAI.Codex 26.901.1978.0.  This profile was
# derived from the last live-validated behaviour baseline and is selected only
# after the Store ASAR and every affected entry hash match.
PAIRS = {
    "automation_priority_gate": (
        (
            b("function O8(e,t,n){if(t.isScheduled&&e(k4o)!==!0)return!1;"),
            b("function O8(e,t,n){if(t.isScheduled&&e(k4o)&&t.attentionState===`idle`)return!1;"),
        ),
    ),
    "priority_filter_recency_sorting": (
        (
            b("function hW(e){return[...e].sort((e,t)=>nAi[e.attentionState]-nAi[t.attentionState]||t.recencyAt-e.recencyAt)}"),
            b("function hW(e,t=(e,t)=>t.recencyAt-e.recencyAt){return[...e].sort(t)}"),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b("C=h==null?void 0:S.find(({item:e})=>{let t=k8(l,e);return t===k8(l,h.item)&&!p.has(t)})?.item,"),
            b("C=((e,t)=>(_.get(k8(l,t))||0)-(_.get(k8(l,e))||0)),"),
        ),
        (
            b("w=K4o(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>!n.has(k8(l,e)))),T=l(E8)===!0"),
            b("w=hW(K4o(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(k8(l,e)))),C),T=l(E8)===!0"),
        ),
        (
            b("k=K4o(l,[...b,...l(h3o,u.sidebarMode).filter(e=>{let t=k8(l,e);return!T||!E||!Z4o(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(k8(l,e))&&Q4o(l,e)));"),
            b("k=hW(K4o(l,[...b,...l(h3o,u.sidebarMode).filter(e=>{let t=k8(l,e);return!T||!E||!Z4o(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(k8(l,e))&&Q4o(l,e))),C);"),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b("h3o=Ly(Q,(e,{get:t})=>j8(t,e).filter(({item:n})=>O8(t,n,e)&&Q4o(t,n)).map(({item:e})=>e))"),
            b("h3o=Ly(Q,(e,{get:t})=>hW(j8(t,e).filter(({item:n})=>O8(t,n,e)&&Q4o(t,n))).map(({item:e})=>e))"),
        ),
    ),
    "project_sorting": (
        (
            b("projectOrder:u,serverOrderedPinnedThreadHostIds:d"),
            b("projectOrder:u,projectSortMode:q,serverOrderedPinnedThreadHostIds:d"),
        ),
        (
            b("let C=yji(v,u,`start`),w=new Set(C);"),
            b("let P=e=>{let t=e.kind==`project`?m.filter(t=>t.projectKey==e.key):[e];return[e,Math.max(...t.map(e=>e.recencyAt)),Math.min(...t.map(e=>nAi[e.prioritySortAttentionState??e.attentionState]))]},C=q[0]==`m`?yji(v,u,`start`):v.map(P).sort((e,t)=>q[0]==`p`?e[2]-t[2]||t[1]-e[1]:t[1]-e[1]).map(e=>e[0].key),w=new Set(C);"),
        ),
        (
            b("pinnedKeys:hji({entries:h,pinnedKeyAliases:s,pinnedOrder:c,pinnedSortMode:l,serverOrderedPinnedThreadHostIds:d"),
            b("pinnedKeys:hji({entries:h,pinnedKeyAliases:s,pinnedOrder:l===`manual`?c:h.map(P).sort((e,t)=>t[1]-e[1]).map(e=>e[0].key),pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:d"),
        ),
    ),
    "plan_pending_yellow_indicator": (
        (
            b("function mGo(e){let t=(0,vGo.c)(4),{statusState:n}=e;if((n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r=(0,k6.jsx)(hGo,{count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t[2]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,k6.jsx)(_Go,{}),t[2]=e):e=t[2],e}if(n.unread===!0){let e;return t[3]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,k6.jsx)(gGo,{}),t[3]=e):e=t[3],e}return null}"),
            b("function mGo({statusState:e}){let n=e.unreadCount||e.unread,t=e.i&&(e.p||n)?`danger`:e.p?`#eab308`:n?`info`:null,r=k6.jsx;return e.type===`loading`?r(_Go,{}):t&&r(gGo,{c:t})}"),
        ),
        (
            b("function gGo(){let e=(0,vGo.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`)?(t=(0,k6.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-codex-description`,children:(0,k6.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,k6.jsx)(`span`,{className:`absolute inset-0 rounded-full bg-info-solid`})})}),e[0]=t):t=e[0],t}"),
            b("function gGo({c:e}){return k6.jsx(`i`,{className:`mx-1.5 size-2 shrink-0 rounded-full`,style:{background:e[0]==`#`?e:`var(--color-text-${e})`}})}"),
        ),
    ),
    "remote_project_label": (
        (
            b("function kwi(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:e.label,path:e.remotePath,gitRepos:Pwi([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
            b("function qZx(e,t){return e.label!=e.id&&e.label||e.remotePath.split(`/`).pop()||t||`Remote project`}function kwi(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:qZx(e,r.get(e.hostId)),path:e.remotePath,gitRepos:Pwi([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
        ),
        (
            b("function uAi(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return lAi(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"),
            b("function uAi(e,t,n){return lAi(e.map(e=>{let n=t.find(t=>t.projectId==e.projectId||t.hostId==e.hostId&&Lv(t.path)==Lv(e.path));return{...n,...e,threadKeys:n?.threadKeys||[]}}),n)}"),
        ),
    ),
    # The new-chat/Work picker reads the raw REMOTE_PROJECTS query before a
    # project necessarily reaches the saved-descriptor/live-group merge above.
    # Normalize only the display label at that earliest boundary; the original
    # id, hostId and remotePath remain untouched for routing and persistence.
    "work_remote_project_picker": (
        (
            b("a=t??[]"),
            b("a=t?.map(e=>({...e,label:qZx(e)}))||[]"),
        ),
    ),
}


SECONDARY_ENTRY_PATH = "webview/assets/app-primary-969b4ff44523.js"
SECONDARY_ENTRY_SOURCE_SHA256 = "19805bdbe9e8a044a9f11fd0a40359d430618fda22a644a1ea46e68fa8ebb6d3"
SECONDARY_PAIRS = {
    "plan_pending_detection": (
        (
            b("onDoubleClick:d,isActive:f,isGrouped:p"),
            b("onDoubleClick:d,isActive:f,P:j0,isGrouped:p"),
        ),
        (
            b("xe=f!==void 0&&f,Se=p!==void 0&&p"),
            b("xe=f!==void 0&&f,yn=!!j0,Se=p!==void 0&&p"),
        ),
        (
            b("t[16]!==Ne||t[17]!==Me||t[18]!==Fe||t[19]!==et||t[20]!==Et||t[21]!==le||t[22]!==it||t[23]!==Dt||t[24]!==tt"),
            b("t[16]===t[16]"),
        ),
        (
            b("unreadCount:Et||Ne?0:tt??0}"),
            b("unreadCount:Et||Ne?0:tt??0,p:at?.type===`implementPlan`,i:yn}"),
        ),
        (
            b("t[124]!==Qe||t[125]!==rt"),
            b("t[124]!=2*Qe+b||t[125]!==rt"),
        ),
        (
            b("disableEnvTooltip:!0,isActive:oe,isUnread:a"),
            b("disableEnvTooltip:!0,isActive:oe,P:b,isUnread:a"),
        ),
        (
            b("t[124]=Qe,t[125]=rt"),
            b("t[124]=2*Qe+b,t[125]=rt"),
        ),
    ),
    "project_sorting": (
        (
            b("pinnedSortMode:G,projectOrder:K,serverOrderedPinnedThreadHostIds"),
            b("pinnedSortMode:G,projectOrder:K,projectSortMode:k,serverOrderedPinnedThreadHostIds"),
        ),
    ),
}


ATTESTATION_LOG_BRIDGE_IDENTIFIER = "U"
ATTESTATION_LOG_BRIDGE_SIGNATURES = (
    b("function WNs(){U.dispatchMessage(`view-focused`,{})}"),
    b("U.dispatchMessage(`log-message`,{level:`info`,message:`[startup][renderer] app routes mounted after ${Math.round(performance.now())}ms`}),U.dispatchMessage(`ready`,{persistedStateResponsePriority:W7?`critical`:void 0})"),
)


OFFICIAL_FEATURE_SIGNATURES = {
    "priority_filter_hold_membership": (
        b("function Z4o(e,t,n){if(!O8(e,t,n))return!1;"),
        b("m3o=Ly(Q,(e,{get:t})=>hW(j8(t,e).filter(({item:n})=>Z4o(t,n,e))))"),
    ),
    "priority_identity_migration": (
        b("function rAi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
    ),
    "priority_project_context_subtitle": (
        b("function mAi({chatLabel:e,task:t,projectLabel:n"),
    ),
    "active_priority_sort": (
        b("function VIi({items:e,attentionStateByThreadKey:t})"),
        b("function HIi({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r})"),
    ),
    "pinned_priority_sync": (
        b("APP_SERVER_MIGRATED_PINNED_THREAD_IDS_BY_HOST"),
        b("function rAi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
    ),
    "resume_history_on_demand": (b("function r4t(e){return e.resumeState===`resumed`"),),
    "paginated_tail_retention": (b("function n4t(e){return TS(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}"),),
    "idle_history_eviction": (
        b("function n9t({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a"),
    ),
}


SECONDARY_OFFICIAL_FEATURE_SIGNATURES = {
    "priority_click_hold": (
        b("function RAn(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a})"),
    ),
    "new_chat_file_drop": (
        b("function mV(e){if(e==null)return!1;"),
        b("onDrop:e=>{if(!P||!mV(e.dataTransfer))return;"),
    ),
    "archived_heartbeat_terminal_guard": (
        b("function nZ(e){let t=(0,UDn.c)(41),{heartbeatAutomationName:n,isRunning:r,open:i,onOpenChange:a,onConfirm:o}=e"),
        b("defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat confirmation dialog when the chat has an active heartbeat automation`"),
    ),
}


PROTECTED_OFFICIAL_SIGNATURES = tuple(
    signature
    for signatures in OFFICIAL_FEATURE_SIGNATURES.values()
    for signature in signatures
)
