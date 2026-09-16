from __future__ import annotations


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Exact semantic rebase for OpenAI.Codex 26.831.2377.0.  Every replacement is
# selected only after the Store ASAR and containing entry hashes match.
PAIRS = {
    "automation_priority_gate": (
        (
            b("function f8(e,t,n){if(t.isScheduled&&e(rJo)!==!0)return!1;"),
            b("function f8(e,t,n){if(t.isScheduled&&e(rJo)!==!0&&t.attentionState===`idle`)return!1;"),
        ),
    ),
    "priority_filter_recency_sorting": (
        (
            b("function mW(e){return[...e].sort((e,t)=>rCi[e.attentionState]-rCi[t.attentionState]||t.recencyAt-e.recencyAt)}"),
            b("function mW(e,t=(e,t)=>t.recencyAt-e.recencyAt){return[...e].sort(t)}"),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b("C=h==null?void 0:S.find(({item:e})=>{let t=p8(l,e);return t===p8(l,h.item)&&!p.has(t)})?.item,"),
            b("C=((e,t)=>(_.get(p8(l,t))||0)-(_.get(p8(l,e))||0)),"),
        ),
        (
            b("w=bJo(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>!n.has(p8(l,e)))),T=l(u8)===!0"),
            b("w=mW(bJo(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(p8(l,e)))),C),T=l(u8)===!0"),
        ),
        (
            b("k=bJo(l,[...b,...l(UJo,u.sidebarMode).filter(e=>{let t=p8(l,e);return!T||!E||!TJo(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(p8(l,e))&&EJo(l,e)));"),
            b("k=mW(bJo(l,[...b,...l(UJo,u.sidebarMode).filter(e=>{let t=p8(l,e);return!T||!E||!TJo(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(p8(l,e))&&EJo(l,e))),C);"),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b("UJo=rb(Q,(e,{get:t})=>h8(t,e).filter(({item:n})=>f8(t,n,e)&&EJo(t,n)).map(({item:e})=>e))"),
            b("UJo=rb(Q,(e,{get:t})=>mW(h8(t,e).filter(({item:n})=>f8(t,n,e)&&EJo(t,n))).map(({item:e})=>e))"),
        ),
    ),
    "project_sorting": (
        (
            b("projectOrder:u,serverOrderedPinnedThreadHostIds:d"),
            b("projectOrder:u,projectSortMode:q,serverOrderedPinnedThreadHostIds:d"),
        ),
        (
            b("let C=bwi(v,u,`start`),w=new Set(C);"),
            b("let P=e=>{let t=e.kind==`project`?m.filter(t=>t.projectKey==e.key):[e];return[e,Math.max(...t.map(e=>e.recencyAt)),Math.min(...t.map(e=>rCi[e.prioritySortAttentionState??e.attentionState]))]},C=q[0]==`m`?bwi(v,u,`start`):v.map(P).sort((e,t)=>q[0]==`p`?e[2]-t[2]||t[1]-e[1]:t[1]-e[1]).map(e=>e[0].key),w=new Set(C);"),
        ),
        (
            b("pinnedKeys:gwi({entries:h,pinnedKeyAliases:s,pinnedOrder:c,pinnedSortMode:l,serverOrderedPinnedThreadHostIds:d"),
            b("pinnedKeys:gwi({entries:h,pinnedKeyAliases:s,pinnedOrder:l===`manual`?c:h.map(P).sort((e,t)=>t[1]-e[1]).map(e=>e[0].key),pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:d"),
        ),
    ),
    "plan_pending_yellow_indicator": (
        (
            b("function pIo(e){let t=(0,_Io.c)(4),{statusState:n}=e;if((n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r=(0,g6.jsx)(mIo,{count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t[2]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,g6.jsx)(gIo,{}),t[2]=e):e=t[2],e}if(n.unread===!0){let e;return t[3]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,g6.jsx)(hIo,{}),t[3]=e):e=t[3],e}return null}"),
            b("function pIo({statusState:e}){let n=e.unreadCount||e.unread,t=e.i&&(e.p||n)?`danger`:e.p?`warning`:n?`info`:null,r=(0,g6.jsx);return e.type===`loading`?r(gIo,{}):t&&r(hIo,{c:t})}"),
        ),
        (
            b("function hIo(){let e=(0,_Io.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`)?(t=(0,g6.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-codex-description`,children:(0,g6.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,g6.jsx)(`span`,{className:`absolute inset-0 rounded-full bg-info-solid`})})}),e[0]=t):t=e[0],t}"),
            b("function hIo({c:e}){return(0,g6.jsx)(`i`,{className:`mx-1.5 size-2 shrink-0 rounded-full`,style:{backgroundColor:`var(--color-text-${e})`}})}"),
        ),
    ),
    "remote_project_label": (
        (
            b("function k_i(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:e.label,path:e.remotePath,gitRepos:P_i([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
            b(r"function k_i(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>{let t=e.label?.trim(),i=r.get(e.hostId);return{groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:i,label:t&&t!=e.id&&t.length-36?t:e.remotePath.split(/[\\/]/).filter(Boolean).pop()||i||`Remote project`,path:e.remotePath,gitRepos:P_i([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}})}"),
        ),
        (
            b("function dCi(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return uCi(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"),
            b("function dCi(e,t,n){return uCi(e.map(e=>{let n=t.find(t=>t.projectId==e.projectId||t.hostId==e.hostId&&xon(t.path)==xon(e.path));return n?{...n,...e,threadKeys:n.threadKeys}:{...e,threadKeys:[]}}),n)}"),
        ),
    ),
}


# The task-row state constructor and the unified-sidebar call site moved to a
# dynamically loaded chunk.  These replacements are part of the same profile
# and must be applied and validated together with PAIRS.
SECONDARY_ENTRY_PATH = "webview/assets/app-primary-c0512216ae0e.js"
SECONDARY_ENTRY_SOURCE_SHA256 = "a82d89acfbf973f97f1c132b17612c0f04a346b5298a891f4f88064b19a488f9"
SECONDARY_PAIRS = {
    "plan_pending_detection": (
        (
            b("onDoubleClick:u,isActive:d,isGrouped:f"),
            b("onDoubleClick:u,isActive:d,P:j0,isGrouped:f"),
        ),
        (
            b("ye=d!==void 0&&d,be=f!==void 0&&f"),
            b("ye=d!==void 0&&d,yn=!!j0,be=f!==void 0&&f"),
        ),
        (
            b("t[103]!==Ce||t[104]!==qe||t[105]!==Ze"),
            b("t[103]!==Ce||t[104]!==qe+b||t[105]!==Ze"),
        ),
        (
            b("isActive:ae,isUnread:a,hasAttachedHeartbeatAutomation:Ee"),
            b("isActive:ae,isUnread:a,P:b,hasAttachedHeartbeatAutomation:Ee"),
        ),
        (
            b("t[103]=Ce,t[104]=qe,t[105]=Ze"),
            b("t[103]=Ce,t[104]=qe+b,t[105]=Ze"),
        ),
        (
            b("t[19]!==je||t[20]!==Ae||t[21]!==Ne||t[22]!==Qe||t[23]!==wt||t[24]!==se||t[25]!==nt||t[26]!==Tt||t[27]!==$e"),
            b("t[19]===t[19]"),
        ),
        (
            b("unreadCount:wt||je?0:$e??0}"),
            b("unreadCount:wt||je?0:$e??0,p:rt?.type===`implementPlan`,i:yn}"),
        ),
    ),
    "project_sorting": (
        (
            b("pinnedSortMode:B,projectOrder:V,serverOrderedPinnedThreadHostIds"),
            b("pinnedSortMode:B,projectOrder:V,projectSortMode:w,serverOrderedPinnedThreadHostIds"),
        ),
    ),
}


ATTESTATION_LOG_BRIDGE_IDENTIFIER = "ay"
ATTESTATION_LOG_BRIDGE_SIGNATURES = (
    b("function gCs(){ay.dispatchMessage(`view-focused`,{})}"),
    b("ay.dispatchMessage(`log-message`,{level:`info`,message:`[startup][renderer] app routes mounted after ${Math.round(performance.now())}ms`}),ay.dispatchMessage(`ready`,{})"),
)


OFFICIAL_FEATURE_SIGNATURES = {
    "priority_filter_hold_membership": (
        b("function TJo(e,t,n){if(!f8(e,t,n))return!1;"),
        b("HJo=rb(Q,(e,{get:t})=>mW(h8(t,e).filter(({item:n})=>TJo(t,n,e))))"),
    ),
    "priority_identity_migration": (b("function llr(e){"), b("pendingWorktreeId")),
    "priority_project_context_subtitle": (b("function hCi({chatLabel:e,task:t,projectLabel:n"),),
    "active_priority_sort": (b("threadAttentionStateByKey:new Map,threadRecencyAtByKey:new Map"),),
    "pinned_priority_sync": (b("APP_SERVER_MIGRATED_PINNED_THREAD_IDS_BY_HOST"), b("function iCi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})")),
    "new_chat_file_drop": (b("function jv(e){"),),
    "resume_history_on_demand": (b("function C0t(e){return e.resumeState===`resumed`"),),
    "paginated_tail_retention": (b("function S0t(e){return FS(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}"),),
    "windows_watch_path_normalization": (b("pathToFileURL"),),
    "idle_history_eviction": (b("resumeState:`needs_resume`,latestTokenUsageInfo:null"),),
    "work_remote_project_picker": (b("function jvi({isExistingThread:e,executionHostId:t,activeLocalProjectId:n,existingAssignment:r,homeRemoteProject:i,selectedRemoteProject:a})"),),
}


# These native behaviours moved to the dynamically loaded primary chunk in
# 26.831.2377.0.  Keep them separate from OFFICIAL_FEATURE_SIGNATURES so the
# initial-entry patcher never treats a signature in another ASAR entry as a
# patch target.  Inspection and contract validation must resolve each exact
# signature against SECONDARY_ENTRY_PATH.
SECONDARY_OFFICIAL_FEATURE_SIGNATURES = {
    "priority_click_hold": (
        b("function Mwn(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a}"),
    ),
    "archived_heartbeat_terminal_guard": (
        b("function sQ(e){let t=(0,Lxn.c)(41),{heartbeatAutomationName:n,isRunning:r,open:i,onOpenChange:a,onConfirm:o}=e"),
        b("defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat confirmation dialog when the chat has an active heartbeat automation`"),
    ),
}

PROTECTED_OFFICIAL_SIGNATURES = tuple(
    signature
    for signatures in OFFICIAL_FEATURE_SIGNATURES.values()
    for signature in signatures
)
