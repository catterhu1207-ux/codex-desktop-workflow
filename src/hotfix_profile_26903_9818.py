from __future__ import annotations


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Exact semantic rebase for OpenAI.Codex 26.903.9818.0.  Every pair is selected
# only after the Store ASAR and every affected entry hash match this profile.
# The rebase re-located each behaviour from the last live-validated baseline
# (26.901.6511.0 / artifact 2.6.7-e75bae2b8a02) because the official bundle was
# re-minified with an entirely new identifier set.
PAIRS = {
    "automation_priority_gate": (
        (
            b("function $8(e,t,n){if(t.isScheduled&&e(Tns)!==!0)return!1;"),
            b("function $8(e,t,n){if(t.isScheduled&&e(Tns)&&t.attentionState===`idle`)return!1;"),
        ),
    ),
    "priority_filter_recency_sorting": (
        (
            b("function RW(e){return[...e].sort((e,t)=>IFi[e.attentionState]-IFi[t.attentionState]||t.recencyAt-e.recencyAt)}"),
            b("function RW(e,t=(e,t)=>t.recencyAt-e.recencyAt){return[...e].sort(t)}"),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b("C=h==null?void 0:S.find(({item:e})=>{let t=e5(l,e);return t===e5(l,h.item)&&!p.has(t)})?.item,"),
            b("C=((e,t)=>(_.get(e5(l,t))||0)-(_.get(e5(l,e))||0)),"),
        ),
        (
            b("w=Hns(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>!n.has(e5(l,e)))),T=l(wns)===!0"),
            b("w=RW(Hns(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(e5(l,e)))),C),T=l(wns)===!0"),
        ),
        (
            b("k=Hns(l,[...b,...l(drs,u.sidebarMode).filter(e=>{let t=e5(l,e);return!T||!E||!qns(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(e5(l,e))&&Jns(l,e)));"),
            b("k=RW(Hns(l,[...b,...l(drs,u.sidebarMode).filter(e=>{let t=e5(l,e);return!T||!E||!qns(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(e5(l,e))&&Jns(l,e))),C);"),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b("drs=Ny(Q,(e,{get:t})=>n5(t,e).filter(({item:n})=>$8(t,n,e)&&Jns(t,n)).map(({item:e})=>e))"),
            b("drs=Ny(Q,(e,{get:t})=>RW(n5(t,e).filter(({item:n})=>$8(t,n,e)&&Jns(t,n))).map(({item:e})=>e))"),
        ),
    ),
    "project_sorting": (
        (
            b("projectOrder:u,serverOrderedPinnedThreadHostIds:d"),
            b("projectOrder:u,projectSortMode:q,serverOrderedPinnedThreadHostIds:d"),
        ),
        (
            b("let C=ZIi(v,u,`start`),w=new Set(C);"),
            b("let P=e=>{let t=e.kind==`project`?m.filter(t=>t.projectKey==e.key):[e];return[e,Math.max(...t.map(e=>e.recencyAt)),Math.min(...t.map(e=>IFi[e.prioritySortAttentionState??e.attentionState]))]},C=q[0]==`m`?ZIi(v,u,`start`):v.map(P).sort((e,t)=>q[0]==`p`?e[2]-t[2]||t[1]-e[1]:t[1]-e[1]).map(e=>e[0].key),w=new Set(C);"),
        ),
        (
            b("pinnedKeys:qIi({entries:h,pinnedKeyAliases:s,pinnedOrder:c,pinnedSortMode:l,serverOrderedPinnedThreadHostIds:d"),
            b("pinnedKeys:qIi({entries:h,pinnedKeyAliases:s,pinnedOrder:l===`manual`?c:h.map(P).sort((e,t)=>t[1]-e[1]).map(e=>e[0].key),pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:d"),
        ),
    ),
    "plan_pending_yellow_indicator": (
        (
            b("function b$o(e){let t=(0,w$o.c)(4),{statusState:n}=e;if((n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r=(0,m8.jsx)(x$o,{count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t[2]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,m8.jsx)(C$o,{}),t[2]=e):e=t[2],e}if(n.unread===!0){let e;return t[3]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,m8.jsx)(S$o,{}),t[3]=e):e=t[3],e}return null}"),
            b("function b$o({statusState:e}){let n=e.unreadCount||e.unread,t=e.i&&(e.p||n)?`danger`:e.p?`#eab308`:n?`info`:null,r=m8.jsx;return e.type===`loading`?r(C$o,{}):t&&r(S$o,{c:t})}"),
        ),
        (
            b("function S$o(){let e=(0,w$o.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`)?(t=(0,m8.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-codex-description`,children:(0,m8.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,m8.jsx)(`span`,{className:`absolute inset-0 rounded-full bg-info-solid`})})}),e[0]=t):t=e[0],t}"),
            b("function S$o({c:e}){return m8.jsx(`i`,{className:`mx-1.5 size-2 shrink-0 rounded-full`,style:{background:e[0]==`#`?e:`var(--color-text-${e})`}})}"),
        ),
    ),
    "remote_project_label": (
        (
            b("function Jki(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:e.label,path:e.remotePath,gitRepos:$ki([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
            b("function qZx(e,t){return e.label!=e.id&&e.label||e.remotePath.split(`/`).pop()||t||`Remote`}function Jki(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:qZx(e,r.get(e.hostId)),path:e.remotePath,gitRepos:$ki([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
        ),
        (
            b("function WFi(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return UFi(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"),
            b("function WFi(e,t,n){return UFi(e.map(e=>{let n=t.find(t=>t.projectId==e.projectId||t.hostId==e.hostId&&t_(t.path)==t_(e.path));return{...n,...e,threadKeys:n?.threadKeys||[]}}),n)}"),
        ),
    ),
    "work_remote_project_picker": (
        (
            b("a=t??[]"),
            b("a=t?.map(e=>({...e,label:qZx(e)}))||[]"),
        ),
    ),
}


SECONDARY_ENTRY_PATH = "webview/assets/app-primary-4c40d73a1074.js"
SECONDARY_ENTRY_SOURCE_SHA256 = "5d74fae9c8de625668fce42ed66eb57539114243be93afaa288a8758551206bb"
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
            b("t[16]!==Ne||t[17]!==Me||t[18]!==Fe||t[19]!==et||t[20]!==Tt||t[21]!==se||t[22]!==it||t[23]!==Et||t[24]!==tt"),
            b("t[16]===t[16]"),
        ),
        (
            b("unreadCount:Tt||Ne?0:tt??0}"),
            b("unreadCount:Tt||Ne?0:tt??0,p:at?.type===`implementPlan`,i:yn}"),
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
            b("pinnedSortMode:G,projectOrder:K,serverOrderedPinnedThreadHostIds"),
            b("pinnedSortMode:G,projectOrder:K,projectSortMode:k,serverOrderedPinnedThreadHostIds"),
        ),
    ),
}


ATTESTATION_LOG_BRIDGE_IDENTIFIER = "H"
ATTESTATION_LOG_BRIDGE_SIGNATURES = (
    b("function zHs(){H.dispatchMessage(`view-focused`,{})}"),
    b("H.dispatchMessage(`log-message`,{level:`info`,message:`[startup][renderer] app routes mounted after ${Math.round(performance.now())}ms`}),H.dispatchMessage(`ready`,{persistedStateResponsePriority:G7?`critical`:void 0})"),
)


OFFICIAL_FEATURE_SIGNATURES = {
    "priority_filter_hold_membership": (
        b("function qns(e,t,n){if(!$8(e,t,n))return!1;"),
        b("urs=Ny(Q,(e,{get:t})=>RW(n5(t,e).filter(({item:n})=>qns(t,n,e))))"),
    ),
    "priority_identity_migration": (
        b("function LFi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n}){"),
    ),
    "priority_project_context_subtitle": (
        b("function JFi({chatLabel:e,task:t,projectLabel:n"),
    ),
    "active_priority_sort": (
        b("function hHi({items:e,attentionStateByThreadKey:t}){"),
        b("function gHi({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r}){"),
    ),
    "pinned_priority_sync": (
        b("APP_SERVER_MIGRATED_PINNED_THREAD_IDS_BY_HOST"),
        b("function LFi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n}){"),
    ),
    "resume_history_on_demand": (
        b("function Y4t(e){return e.resumeState===`resumed`&&("),
    ),
    "paginated_tail_retention": (
        b("function J4t(e){return RS(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}"),
    ),
    "idle_history_eviction": (
        b("function Y9t({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a"),
    ),
}


SECONDARY_OFFICIAL_FEATURE_SIGNATURES = {
    "priority_click_hold": (
        b("function oIn(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a})"),
    ),
    "new_chat_file_drop": (
        b("function HB(e){if(e==null)return!1;"),
        b("onDrop:e=>{if(!M||!HB(e.dataTransfer))return;"),
    ),
    "archived_heartbeat_terminal_guard": (
        b("function vY(e){let t=(0,mNn.c)(41),{heartbeatAutomationName:n,isRunning:r,open:i,onOpenChange:a,onConfirm:o}=e"),
        b("defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat confirmation dialog when the chat has an active heartbeat automation`}):(0,"),
    ),
}


PROTECTED_OFFICIAL_SIGNATURES = tuple(
    signature
    for signatures in OFFICIAL_FEATURE_SIGNATURES.values()
    for signature in signatures
)
