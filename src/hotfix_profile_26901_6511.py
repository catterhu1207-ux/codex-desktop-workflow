from __future__ import annotations


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Exact semantic rebase for OpenAI.Codex 26.901.6511.0.  This profile was
# derived from the last live-validated behaviour baseline and is selected only
# after the Store ASAR and every affected entry hash match.
PAIRS = {
    "automation_priority_gate": (
        (
            b("function N8(e,t,n){if(t.isScheduled&&e(x3o)!==!0)return!1;"),
            b("function N8(e,t,n){if(t.isScheduled&&e(x3o)&&t.attentionState===`idle`)return!1;"),
        ),
    ),
    "priority_filter_recency_sorting": (
        (
            b("function _W(e){return[...e].sort((e,t)=>TAi[e.attentionState]-TAi[t.attentionState]||t.recencyAt-e.recencyAt)}"),
            b("function _W(e,t=(e,t)=>t.recencyAt-e.recencyAt){return[...e].sort(t)}"),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b("C=h==null?void 0:S.find(({item:e})=>{let t=P8(l,e);return t===P8(l,h.item)&&!p.has(t)})?.item,"),
            b("C=((e,t)=>(_.get(P8(l,t))||0)-(_.get(P8(l,e))||0)),"),
        ),
        (
            b("w=R3o(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>!n.has(P8(l,e)))),T=l(j8)===!0"),
            b("w=_W(R3o(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(P8(l,e)))),C),T=l(j8)===!0"),
        ),
        (
            b("k=R3o(l,[...b,...l(s6o,u.sidebarMode).filter(e=>{let t=P8(l,e);return!T||!E||!U3o(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(P8(l,e))&&W3o(l,e)));"),
            b("k=_W(R3o(l,[...b,...l(s6o,u.sidebarMode).filter(e=>{let t=P8(l,e);return!T||!E||!U3o(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(P8(l,e))&&W3o(l,e))),C);"),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b("s6o=Xy(Q,(e,{get:t})=>I8(t,e).filter(({item:n})=>N8(t,n,e)&&W3o(t,n)).map(({item:e})=>e))"),
            b("s6o=Xy(Q,(e,{get:t})=>_W(I8(t,e).filter(({item:n})=>N8(t,n,e)&&W3o(t,n))).map(({item:e})=>e))"),
        ),
    ),
    "project_sorting": (
        (
            b("projectOrder:u,serverOrderedPinnedThreadHostIds:d"),
            b("projectOrder:u,projectSortMode:q,serverOrderedPinnedThreadHostIds:d"),
        ),
        (
            b("let C=Hji(v,u,`start`),w=new Set(C);"),
            b("let P=e=>{let t=e.kind==`project`?m.filter(t=>t.projectKey==e.key):[e];return[e,Math.max(...t.map(e=>e.recencyAt)),Math.min(...t.map(e=>TAi[e.prioritySortAttentionState??e.attentionState]))]},C=q[0]==`m`?Hji(v,u,`start`):v.map(P).sort((e,t)=>q[0]==`p`?e[2]-t[2]||t[1]-e[1]:t[1]-e[1]).map(e=>e[0].key),w=new Set(C);"),
        ),
        (
            b("pinnedKeys:Rji({entries:h,pinnedKeyAliases:s,pinnedOrder:c,pinnedSortMode:l,serverOrderedPinnedThreadHostIds:d"),
            b("pinnedKeys:Rji({entries:h,pinnedKeyAliases:s,pinnedOrder:l===`manual`?c:h.map(P).sort((e,t)=>t[1]-e[1]).map(e=>e[0].key),pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:d"),
        ),
    ),
    "plan_pending_yellow_indicator": (
        (
            b("function oKo(e){let t=(0,uKo.c)(4),{statusState:n}=e;if((n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r=(0,P6.jsx)(sKo,{count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t[2]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,P6.jsx)(lKo,{}),t[2]=e):e=t[2],e}if(n.unread===!0){let e;return t[3]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,P6.jsx)(cKo,{}),t[3]=e):e=t[3],e}return null}"),
            b("function oKo({statusState:e}){let n=e.unreadCount||e.unread,t=e.i&&(e.p||n)?`danger`:e.p?`#eab308`:n?`info`:null,r=P6.jsx;return e.type===`loading`?r(lKo,{}):t&&r(cKo,{c:t})}"),
        ),
        (
            b("function cKo(){let e=(0,uKo.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`)?(t=(0,P6.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-codex-description`,children:(0,P6.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,P6.jsx)(`span`,{className:`absolute inset-0 rounded-full bg-info-solid`})})}),e[0]=t):t=e[0],t}"),
            b("function cKo({c:e}){return P6.jsx(`i`,{className:`mx-1.5 size-2 shrink-0 rounded-full`,style:{background:e[0]==`#`?e:`var(--color-text-${e})`}})}"),
        ),
    ),
    "remote_project_label": (
        (
            b("function Qwi(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:e.label,path:e.remotePath,gitRepos:rTi([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
            b("function qZx(e,t){return e.label!=e.id&&e.label||e.remotePath.split(`/`).pop()||t||`Remote`}function Qwi(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:qZx(e,r.get(e.hostId)),path:e.remotePath,gitRepos:rTi([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
        ),
        (
            b("function NAi(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return MAi(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"),
            b("function NAi(e,t,n){return MAi(e.map(e=>{let n=t.find(t=>t.projectId==e.projectId||t.hostId==e.hostId&&Xv(t.path)==Xv(e.path));return{...n,...e,threadKeys:n?.threadKeys||[]}}),n)}"),
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


SECONDARY_ENTRY_PATH = "webview/assets/app-primary-428a0a65766f.js"
SECONDARY_ENTRY_SOURCE_SHA256 = "b901ac16b6d81e888e1a5a44f4c6d97ef00c1814212ac6a3ecd4e069e76d9acd"
SECONDARY_PAIRS = {
    "plan_pending_detection": (
        (
            b("onDoubleClick:d,isActive:f,isGrouped:p"),
            b("onDoubleClick:d,isActive:f,P:j0,isGrouped:p"),
        ),
        (
            b("be=f!==void 0&&f,xe=p!==void 0&&p"),
            b("be=f!==void 0&&f,yn=!!j0,xe=p!==void 0&&p"),
        ),
        (
            b("t[16]!==Me||t[17]!==je||t[18]!==Pe||t[19]!==$e||t[20]!==Tt||t[21]!==se||t[22]!==rt||t[23]!==Et||t[24]!==et"),
            b("t[16]===t[16]"),
        ),
        (
            b("unreadCount:Tt||Me?0:et??0}"),
            b("unreadCount:Tt||Me?0:et??0,p:it?.type===`implementPlan`,i:yn}"),
        ),
        (
            b("t[124]!==Qe||t[125]!==rt"),
            b("t[124]!=2*Qe+b||t[125]!==rt"),
        ),
        (
            b("disableEnvTooltip:!0,isActive:ae,isUnread:a"),
            b("disableEnvTooltip:!0,isActive:ae,P:b,isUnread:a"),
        ),
        (
            b("t[124]=Qe,t[125]=rt"),
            b("t[124]=2*Qe+b,t[125]=rt"),
        ),
    ),
    "project_sorting": (
        (
            b("pinnedSortMode:q,projectOrder:J,serverOrderedPinnedThreadHostIds"),
            b("pinnedSortMode:q,projectOrder:J,projectSortMode:A,serverOrderedPinnedThreadHostIds"),
        ),
    ),
}


ATTESTATION_LOG_BRIDGE_IDENTIFIER = "U"
ATTESTATION_LOG_BRIDGE_SIGNATURES = (
    b("function VPs(){U.dispatchMessage(`view-focused`,{})}"),
    b("U.dispatchMessage(`log-message`,{level:`info`,message:`[startup][renderer] app routes mounted after ${Math.round(performance.now())}ms`}),U.dispatchMessage(`ready`,{persistedStateResponsePriority:U7?`critical`:void 0})"),
)


OFFICIAL_FEATURE_SIGNATURES = {
    "priority_filter_hold_membership": (
        b("function U3o(e,t,n){if(!N8(e,t,n))return!1;"),
        b("o6o=Xy(Q,(e,{get:t})=>_W(I8(t,e).filter(({item:n})=>U3o(t,n,e))))"),
    ),
    "priority_identity_migration": (
        b("function EAi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
    ),
    "priority_project_context_subtitle": (
        b("function LAi({chatLabel:e,task:t,projectLabel:n"),
    ),
    "active_priority_sort": (
        b("function lLi({items:e,attentionStateByThreadKey:t})"),
        b("function uLi({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r})"),
    ),
    "pinned_priority_sync": (
        b("APP_SERVER_MIGRATED_PINNED_THREAD_IDS_BY_HOST"),
        b("function EAi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
    ),
    "resume_history_on_demand": (b("function a4t(e){return e.resumeState===`resumed`"),),
    "paginated_tail_retention": (b("function i4t(e){return CS(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}"),),
    "idle_history_eviction": (
        b("function a9t({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a"),
    ),
}


SECONDARY_OFFICIAL_FEATURE_SIGNATURES = {
    "priority_click_hold": (
        b("function ojn(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a})"),
    ),
    "new_chat_file_drop": (
        b("function _H(e){if(e==null)return!1;"),
        b("onDrop:e=>{if(!M||!_H(e.dataTransfer))return;"),
    ),
    "archived_heartbeat_terminal_guard": (
        b("function WZ(e){let t=(0,JDn.c)(41),{heartbeatAutomationName:n,isRunning:r,open:i,onOpenChange:a,onConfirm:o}=e"),
        b("defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat confirmation dialog when the chat has an active heartbeat automation`"),
    ),
}


PROTECTED_OFFICIAL_SIGNATURES = tuple(
    signature
    for signatures in OFFICIAL_FEATURE_SIGNATURES.values()
    for signature in signatures
)
