from __future__ import annotations


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Exact semantic rebase for OpenAI.Codex 26.901.4073.0.  This profile was
# derived from the last live-validated behaviour baseline and is selected only
# after the Store ASAR and every affected entry hash match.
PAIRS = {
    "automation_priority_gate": (
        (
            b("function m8(e,t,n){if(t.isScheduled&&e(c3o)!==!0)return!1;"),
            b("function m8(e,t,n){if(t.isScheduled&&e(c3o)&&t.attentionState===`idle`)return!1;"),
        ),
    ),
    "priority_filter_recency_sorting": (
        (
            b("function uW(e){return[...e].sort((e,t)=>TAi[e.attentionState]-TAi[t.attentionState]||t.recencyAt-e.recencyAt)}"),
            b("function uW(e,t=(e,t)=>t.recencyAt-e.recencyAt){return[...e].sort(t)}"),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b("C=h==null?void 0:S.find(({item:e})=>{let t=h8(l,e);return t===h8(l,h.item)&&!p.has(t)})?.item,"),
            b("C=((e,t)=>(_.get(h8(l,t))||0)-(_.get(h8(l,e))||0)),"),
        ),
        (
            b("w=T3o(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>!n.has(h8(l,e)))),T=l(f8)===!0"),
            b("w=uW(T3o(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(h8(l,e)))),C),T=l(f8)===!0"),
        ),
        (
            b("k=T3o(l,[...b,...l(J3o,u.sidebarMode).filter(e=>{let t=h8(l,e);return!T||!E||!A3o(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(h8(l,e))&&j3o(l,e)));"),
            b("k=uW(T3o(l,[...b,...l(J3o,u.sidebarMode).filter(e=>{let t=h8(l,e);return!T||!E||!A3o(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(h8(l,e))&&j3o(l,e))),C);"),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b("J3o=Jy(Q,(e,{get:t})=>_8(t,e).filter(({item:n})=>m8(t,n,e)&&j3o(t,n)).map(({item:e})=>e))"),
            b("J3o=Jy(Q,(e,{get:t})=>uW(_8(t,e).filter(({item:n})=>m8(t,n,e)&&j3o(t,n))).map(({item:e})=>e))"),
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
            b("function qGo(e){let t=(0,ZGo.c)(4),{statusState:n}=e;if((n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r=(0,h6.jsx)(JGo,{count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t[2]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,h6.jsx)(XGo,{}),t[2]=e):e=t[2],e}if(n.unread===!0){let e;return t[3]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,h6.jsx)(YGo,{}),t[3]=e):e=t[3],e}return null}"),
            b("function qGo({statusState:e}){let n=e.unreadCount||e.unread,t=e.i&&(e.p||n)?`danger`:e.p?`#eab308`:n?`info`:null,r=h6.jsx;return e.type===`loading`?r(XGo,{}):t&&r(YGo,{c:t})}"),
        ),
        (
            b("function YGo(){let e=(0,ZGo.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`)?(t=(0,h6.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-codex-description`,children:(0,h6.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,h6.jsx)(`span`,{className:`absolute inset-0 rounded-full bg-info-solid`})})}),e[0]=t):t=e[0],t}"),
            b("function YGo({c:e}){return h6.jsx(`i`,{className:`mx-1.5 size-2 shrink-0 rounded-full`,style:{background:e[0]==`#`?e:`var(--color-text-${e})`}})}"),
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


SECONDARY_ENTRY_PATH = "webview/assets/app-primary-809d1fa17f2d.js"
SECONDARY_ENTRY_SOURCE_SHA256 = "266a0e23ae0bca2069a97e5783c9dc98f3119d229923b061f44a2cbfa8fb24cf"
SECONDARY_PAIRS = {
    "plan_pending_detection": (
        (
            b("onDoubleClick:d,isActive:f,isGrouped:p"),
            b("onDoubleClick:d,isActive:f,P:j0,isGrouped:p"),
        ),
        (
            b("ye=f!==void 0&&f,be=p!==void 0&&p"),
            b("ye=f!==void 0&&f,yn=!!j0,be=p!==void 0&&p"),
        ),
        (
            b("t[16]!==je||t[17]!==Ae||t[18]!==Ne||t[19]!==Qe||t[20]!==wt||t[21]!==se||t[22]!==nt||t[23]!==Tt||t[24]!==$e"),
            b("t[16]===t[16]"),
        ),
        (
            b("unreadCount:wt||je?0:$e??0}"),
            b("unreadCount:wt||je?0:$e??0,p:rt?.type===`implementPlan`,i:yn}"),
        ),
        (
            b("t[124]!==Ze||t[125]!==nt"),
            b("t[124]!=2*Ze+b||t[125]!==nt"),
        ),
        (
            b("disableEnvTooltip:!0,isActive:ae,isUnread:a"),
            b("disableEnvTooltip:!0,isActive:ae,P:b,isUnread:a"),
        ),
        (
            b("t[124]=Ze,t[125]=nt"),
            b("t[124]=2*Ze+b,t[125]=nt"),
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
    b("function uPs(){U.dispatchMessage(`view-focused`,{})}"),
    b("U.dispatchMessage(`log-message`,{level:`info`,message:`[startup][renderer] app routes mounted after ${Math.round(performance.now())}ms`}),U.dispatchMessage(`ready`,{persistedStateResponsePriority:G7?`critical`:void 0})"),
)


OFFICIAL_FEATURE_SIGNATURES = {
    "priority_filter_hold_membership": (
        b("function A3o(e,t,n){if(!m8(e,t,n))return!1;"),
        b("q3o=Jy(Q,(e,{get:t})=>uW(_8(t,e).filter(({item:n})=>A3o(t,n,e))))"),
    ),
    "priority_identity_migration": (
        b("function EAi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
    ),
    "priority_project_context_subtitle": (
        b("function LAi({chatLabel:e,task:t,projectLabel:n"),
    ),
    "active_priority_sort": (
        b("function uLi({items:e,attentionStateByThreadKey:t})"),
        b("function dLi({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r})"),
    ),
    "pinned_priority_sync": (
        b("APP_SERVER_MIGRATED_PINNED_THREAD_IDS_BY_HOST"),
        b("function EAi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
    ),
    "resume_history_on_demand": (b("function K2t(e){return e.resumeState===`resumed`"),),
    "paginated_tail_retention": (b("function G2t(e){return IS(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}"),),
    "idle_history_eviction": (
        b("function G7t({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a"),
    ),
}


SECONDARY_OFFICIAL_FEATURE_SIGNATURES = {
    "priority_click_hold": (
        b("function ZAn(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a})"),
    ),
    "new_chat_file_drop": (
        b("function bH(e){if(e==null)return!1;"),
        b("onDrop:e=>{if(!N||!bH(e.dataTransfer))return;"),
    ),
    "archived_heartbeat_terminal_guard": (
        b("function BZ(e){let t=(0,zDn.c)(41),{heartbeatAutomationName:n,isRunning:r,open:i,onOpenChange:a,onConfirm:o}=e"),
        b("defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat confirmation dialog when the chat has an active heartbeat automation`"),
    ),
}


PROTECTED_OFFICIAL_SIGNATURES = tuple(
    signature
    for signatures in OFFICIAL_FEATURE_SIGNATURES.values()
    for signature in signatures
)
