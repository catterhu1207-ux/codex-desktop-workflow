from __future__ import annotations

from hotfix_profile_26825_5331 import PAIRS as _5331_PAIRS


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Exact 26.825.6671.0 profile. The sidebar was refactored, so replacements
# are anchored to this package's own bundle rather than inherited blindly.
PAIRS = {
    "automation_priority_gate": (
        (
            b(
                "function x6(e,t,n){if(t.isScheduled&&e(Nuc)!==!0)return!1;"
                "if(n===`codex`)return!0;"
            ),
            b(
                "function x6(e,t,n){if(t.isScheduled&&e(Nuc)!==!0&&t.attentionState"
                "===`idle`)return!1;if(n===`codex`)return!0;"
            ),
        ),
    ),
    "priority_filter_recency_sorting": (
        (
            b("function zN(e){return[...e].sort((e,t)=>NCr[e.attentionState]-NCr[t.attentionState]||t.recencyAt-e.recencyAt)}"),
            b("function zN(e,t=(e,t)=>t.recencyAt-e.recencyAt){return[...e].sort(t)}"),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b(
                "C=h==null?void 0:S.find(({item:e})=>{let t=S6(l,e);return "
                "t===S6(l,h.item)&&!p.has(t)})?.item,"
            ),
            b(
                "C=((e,t)=>(_.get(S6(l,t))||0)-(_.get(S6(l,e))||0)),"
            ),
        ),
        (
            b(
                "w=Juc(l,[...C==null?[]:[C],...y,...S.map(({item:e})=>e)].filter(e=>"
                "!n.has(S6(l,e)))),T=l(v6)===!0"
            ),
            b(
                "w=zN(Juc(l,[...S.map(({item:e})=>e),...y].filter(e=>"
                "!n.has(S6(l,e)))),C),T=l(v6)===!0"
            ),
        ),
        (
            b(
                "k=Juc(l,[...b,...l(_dc,u.sidebarMode).filter(e=>{let t=S6(l,e);"
                "return!T||!E||!$uc(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})]"
                ".filter(e=>!n.has(S6(l,e))&&edc(l,e)));"
            ),
            b(
                "k=zN(Juc(l,[...b,...l(_dc,u.sidebarMode).filter(e=>{let t=S6(l,e);"
                "return!T||!E||!$uc(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})]"
                ".filter(e=>!n.has(S6(l,e))&&edc(l,e))),C);"
            ),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b(
                "_dc=Ig($,(e,{get:t})=>w6(t,e).filter(({item:n})=>x6(t,n,e)&&"
                "edc(t,n)).map(({item:e})=>e))"
            ),
            b(
                "_dc=Ig($,(e,{get:t})=>zN(w6(t,e).filter(({item:n})=>x6(t,n,e)"
                "&&edc(t,n))).map(({item:e})=>e))"
            ),
        ),
    ),
    "project_sorting": (
        (
            b(
                "function Rwr(e,{chatOrder:t=[],chatSortMode:n=`priority`,customSectionItemKeys:r,"
                "includeChatGptProjects:i=!0,includeCodexProjects:a=!0,mode:o,pinnedKeyAliases:s,"
                "pinnedOrder:c,pinnedSortMode:l=`manual`,projectOrder:u,"
                "serverOrderedPinnedThreadHostIds:d,serverOrderedPinnedThreadKeys:f,source:p})"
            ),
            b(
                "function Rwr(e,{chatOrder:t=[],chatSortMode:n=`priority`,customSectionItemKeys:r,"
                "includeChatGptProjects:i=!0,includeCodexProjects:a=!0,mode:o,pinnedKeyAliases:s,"
                "pinnedOrder:c,pinnedSortMode:l=`manual`,projectOrder:u,projectSortMode:q,"
                "serverOrderedPinnedThreadHostIds:d,serverOrderedPinnedThreadKeys:f,source:p})"
            ),
        ),
        (
            b("let C=Vwr(v,u,`start`),w=new Set(C);"),
            b(
                "let P=e=>{let t=e.kind==`project`?m.filter(t=>t.projectKey==e.key):[e];"
                "return[e,Math.max(...t.map(e=>e.recencyAt)),Math.min(...t.map(e=>"
                "NCr[e.prioritySortAttentionState??e.attentionState]))]},C=q[0]==`m`?"
                "Vwr(v,u,`start`):v.map(P).sort((e,t)=>q[0]==`p`?e[2]-t[2]||"
                "t[1]-e[1]:t[1]-e[1]).map(e=>e[0].key),w=new Set(C);"
            ),
        ),
        (
            b(
                "pinnedKeys:Lwr({entries:h,pinnedKeyAliases:s,pinnedOrder:c,"
                "pinnedSortMode:l,serverOrderedPinnedThreadHostIds:d,"
                "serverOrderedPinnedThreadKeys:f})"
            ),
            b(
                "pinnedKeys:Lwr({entries:h,pinnedKeyAliases:s,pinnedOrder:l==`manual`?c:"
                "h.map(P).sort((e,t)=>t[1]-e[1]).map(e=>e[0].key),pinnedSortMode:`manual`,"
                "serverOrderedPinnedThreadHostIds:d,serverOrderedPinnedThreadKeys:f})"
            ),
        ),
        (
            b(
                "pinnedOrder:L,pinnedSortMode:R,projectOrder:z,"
                "serverOrderedPinnedThreadHostIds:ge?.hostIdByKey"
            ),
            b(
                "pinnedOrder:L,pinnedSortMode:R,projectOrder:z,projectSortMode:w,"
                "serverOrderedPinnedThreadHostIds:ge?.hostIdByKey"
            ),
        ),
    ),
    "plan_pending_detection": (
        (
            _5331_PAIRS["plan_pending_detection"][0][0],
            b(
                "kt=je?{type:`loading`}:{type:Et,unread:!Tt&&((ce??$e===!0)||"
                "Me&&(et>0||rt||Pe)),unreadCount:Tt||Me?0:et||0,"
                "plan:it?.type===`implementPlan`,pinned:!!Pi}"
            ),
        ),
        *_5331_PAIRS["plan_pending_detection"][1:],
    ),
    "plan_pending_yellow_indicator": (
        (
            b("function p8(e){let t=(0,sEc.c)(4),{statusState:n}=e;if((n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r=(0,m8.jsx)(iEc,{count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t[2]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,m8.jsx)(oEc,{}),t[2]=e):e=t[2],e}if(n.unread===!0){let e;return t[3]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,m8.jsx)(aEc,{}),t[3]=e):e=t[3],e}return null}"),
            b("function p8({statusState:e}){let n=e.unreadCount||e.unread,t=e.pinned&&(e.plan||n)?`danger`:e.plan?`warning`:n?`info`:null,r=(0,m8.jsx);return e.type===`loading`?r(oEc,{}):t&&r(aEc,{c:t})}"),
        ),
        (
            b("function aEc(){let e=(0,sEc.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`)?(t=(0,m8.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-codex-description`,children:(0,m8.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,m8.jsx)(`span`,{className:`absolute inset-0 rounded-full bg-info-solid`})})}),e[0]=t):t=e[0],t}"),
            b("function aEc({c:e}){return(0,m8.jsx)(`i`,{className:`mx-1.5 size-2 shrink-0 rounded-full`,style:{backgroundColor:`var(--color-text-${e})`}})}"),
        ),
    ),
    "remote_project_label": (
        (
            b("function smr(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>({groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:r.get(e.hostId)??null,label:e.label,path:e.remotePath,gitRepos:fmr([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}))}"),
            b("function smr(e,t,n){let r=new Map(t.map(e=>[e.hostId,e.displayName]));return e.map(e=>{let t=e.label?.trim(),i=r.get(e.hostId);return{groupId:e.id,projectId:e.id,projectKind:`remote`,hostId:e.hostId,hostDisplayName:i,label:t&&t!=e.id&&t.length-36?t:e.remotePath.split(/[\\\\/]/).pop()||i||`Remote project`,path:e.remotePath,gitRepos:fmr([e.remotePath],n?.[e.hostId]??[]),isCodexWorktree:!1}})}"),
        ),
        (
            b("function VCr(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return BCr(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"),
            b("function VCr(e,t,n){return BCr(e.map(e=>{let n=t.find(t=>t.projectId==e.projectId||e.hostId&&t.hostId==e.hostId&&km(t.path)==km(e.path));return n?{...n,...e,threadKeys:n.threadKeys}:{...e,threadKeys:[]}}),n)}"),
        ),
    ),
}

INJECTED_GLOBAL_IDENTIFIER_COUNTS = {}

# The real renderer already publishes lifecycle diagnostics through this
# bridge. Keep the minified identifier and both call-site signatures in the
# version profile so a future Store bundle cannot silently reuse this
# transport when the renderer/main-process wiring has changed.
ATTESTATION_LOG_BRIDGE_IDENTIFIER = "Uh"
ATTESTATION_LOG_BRIDGE_SIGNATURES = (
    b("function eOl(){Uh.dispatchMessage(`view-focused`,{})}"),
    b(
        "Uh.dispatchMessage(`log-message`,{level:`info`,message:"
        "`[startup][renderer] app routes mounted after "
        "${Math.round(performance.now())}ms`})"
    ),
)

# A feature omitted from PAIRS is accepted as native only when every exact
# signature below occurs once in this hash-gated bundle.  This deliberately
# replaces the former "everything else is official" default.
OFFICIAL_FEATURE_SIGNATURES = {
    "automation_priority_gate": (
        b("function $uc(e,t,n){if(!x6(e,t,n))return!1;"),
        b("gdc=Ig($,(e,{get:t})=>zN(w6(t,e).filter(({item:n})=>$uc(t,n,e))))"),
    ),
    "priority_filter_recency_sorting": (
        b("gdc=Ig($,(e,{get:t})=>zN(w6(t,e).filter(({item:n})=>$uc(t,n,e))))"),
    ),
    "priority_filter_pinned_recency_sorting": (
        b("function PCr({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
        b("pinnedProjectThreadKeys:i,projectGroups:r"),
    ),
    "priority_filter_hold_membership": (
        b("gdc=Ig($,(e,{get:t})=>zN(w6(t,e).filter(({item:n})=>$uc(t,n,e))))"),
    ),
    "priority_click_hold": (
        b("onSelect:(e,t)=>{PLc(T,e,t,{markThreadAsRead:ae,markThreadAsUnread:oe,setPendingWorktreePinned:_})}"),
    ),
    "priority_project_context_subtitle": (
        b("projectGroup:n.projectGroup,sidebarMode:o"),
        b("projectLabel:n.projectGroup.label"),
    ),
    "priority_identity_migration": (
        b("function LVn(e){switch(e.kind){case`local`:return e.conversation==null?"),
    ),
    "project_sorting": (
        b("projectSortMode:e?.projectSortMode===`created_at`?`updated_at`"),
        b("T===`project`?mt(`projects`,Ke.projectKeys).flatMap"),
    ),
    "active_priority_sort": (
        b("gdc=Ig($,(e,{get:t})=>zN(w6(t,e).filter(({item:n})=>$uc(t,n,e))))"),
        b("threadAttentionStateByKey:new Map,threadRecencyAtByKey:new Map"),
    ),
    "pinned_priority_sync": (
        b("APP_SERVER_MIGRATED_PINNED_THREAD_IDS_BY_HOST"),
    ),
    "new_chat_file_drop": (
        b("onDrop:e=>{if(!T||!EJ(e.dataTransfer))return;e.preventDefault(),e.stopPropagation();let t=H6a(e.dataTransfer);t.length>0&&Qt(t)"),
    ),
    "work_remote_project_picker": (
        b("Qr=fhr({isExistingThread:fe!=null,executionHostId:yr,activeLocalProjectId:cn,existingAssignment:fn,homeRemoteProject:S??null,selectedRemoteProject:gn})"),
    ),
    "resume_history_on_demand": (
        b("function ODt(e){return e.resumeState===`resumed`&&(e.turnHistory?.kind===`canonical`?e.turnsPagination?.hasLoadedOldest===!0:e.turnsPagination?.hasLoadedOldest??!0)}"),
    ),
    "paginated_tail_retention": (
        b("function DDt(e){return V_(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}"),
    ),
    "archived_heartbeat_terminal_guard": (
        b("function yPc(e){let t=(0,xPc.c)(41),{heartbeatAutomationName:n,isRunning:r,open:i,onOpenChange:a,onConfirm:o}=e"),
        b("hasAttachedHeartbeatAutomation:Oe"),
        b("defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat confirmation dialog when the chat has an active heartbeat automation`"),
    ),
    "idle_history_eviction": (
        b("function bAt(e){return{id:e.conversationId,forkedFromId:e.forkedFromId??null,hostId:e.hostId,turns:[]"),
    ),
    "remote_project_label": (
        b("...smr(r,e(kN))],Ex(e,Cm.PROJECT_ORDER))"),
        b("...smr(c,u,w)],Ex(e,Cm.PROJECT_ORDER))"),
        b("return VCr(e(IN),n,r)"),
    ),
}

PROTECTED_OFFICIAL_SIGNATURES = tuple(
    signature
    for signatures in OFFICIAL_FEATURE_SIGNATURES.values()
    for signature in signatures
)
