from __future__ import annotations


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Exact, hash-gated Microsoft Store 26.810.6296.0 frontend profile. Each
# behavior is separate so a partial rebase cannot be reported as complete.
PAIRS: dict[str, tuple[tuple[bytes, bytes], ...]] = {
    "priority_filter_recency_sorting": (
        (
            b("SWc=ja(Q,(e,{get:t})=>UT(xWc(t,e).filter(({item:n})=>rWc(t,n,e)))),"),
            b("SWc=ja(Q,(e,{get:t})=>xWc(t,e).filter(({item:n})=>rWc(t,n,e)).map((e,t)=>({e,t})).sort((e,t)=>t.e.recencyAt-e.e.recencyAt||e.t-t.t).map(({e})=>e)),"),
        ),
    ),
    "priority_click_hold": (
        (
            b("var Sgn,Cgn,wgn,Tgn,Egn,Dgn,Ogn,kgn,Agn,jgn,Mgn,Ngn,Pgn,Fgn,Ign,Lgn,Rgn,Dw,zgn,Ow,Bgn,Vgn,Hgn,Ugn,Wgn,kw,Aw=n((()=>"),
            b("var Sgn,Cgn,wgn,Tgn,Egn,Dgn,Ogn,kgn,Agn,jgn,Mgn,Ngn,Pgn,Fgn,Ign,Lgn,Rgn,Dw,zgn,Ow,aad,aaf,Bgn,Vgn,Hgn,Ugn,Wgn,kw,Aw=n((()=>"),
        ),
        (
            b("Ow=Ea(Q,null),Bgn=Fa(Q,({get:e})=>"),
            b("Ow=Ea(Q,null),aad=rh(`sidebar-read-priority-holds-v1`,{}),aaf=(e,t)=>{let n=Date.now();e.set(aad,{...e.get(aad),[xgn(e,t)]:[e.get(fwn,t),n,n+864e5]}),setTimeout(()=>e.set(aad,{...e.get(aad)}),864e5)},Bgn=Fa(Q,({get:e})=>"),
        ),
        (
            b("b=()=>{ue!==!0&&n!=null&&(jA(V,t,n.hostId),V.get(IA,n.hostId)?.activateThreadSummary(t)),I&&_?.()}"),
            b("b=()=>{o&&aaf(V,u),ue!==!0&&n!=null&&(jA(V,t,n.hostId),V.get(IA,n.hostId)?.activateThreadSummary(t)),I&&_?.()}"),
        ),
        (
            b("ue=()=>{sIc(oe,fw(le)),c?.(),s(),_w(oe,`/remote/${le}`,l==null?void 0:{state:l})}"),
            b("ue=()=>{n.has_unread_turn&&aaf(oe,fw(le)),sIc(oe,fw(le)),c?.(),s(),_w(oe,`/remote/${le}`,l==null?void 0:{state:l})}"),
        ),
    ),
    "priority_filter_hold_membership": (
        (
            b("function rWc(e,t,n){return iWc(e,t,n)?t.attentionState!==`idle`||t.kind===`task`&&e(Bgn)===t.threadEntry.key:!1}"),
            b("function rWc(e,t,n){let r=t.kind===`task`?t.threadEntry.key:null,i=r==null?null:Object.entries(e(aad)??{}).some(([t,n])=>xgn({get:e},t)===xgn({get:e},r)&&n?.[0]===e(fwn,r)&&n[2]>Date.now());return iWc(e,t,n)?t.attentionState!==`idle`||t.kind===`task`&&(e(Bgn)===r||i):!1}"),
        ),
    ),
    "priority_filter_live_resort": (
        (
            b("let C=u(SWc,d.sidebarMode),w=g==null?void 0:C.find(({item:e})=>{let t=o8(u,e);return t===o8(u,g.item)&&!m.has(t)})?.item,T=QUc(u,[...w==null?[]:[w],...b,...C.map(({item:e})=>e)].filter(e=>!n.has(o8(u,e)))),E=u(i8)===!0"),
            b("let C=u(SWc,d.sidebarMode),w=g==null?void 0:C.find(({item:e})=>{let t=o8(u,e);return t===o8(u,g.item)&&!m.has(t)})?.item,T=QUc(u,[...C.map(({item:e})=>e),...b].filter(e=>!n.has(o8(u,e)))),E=u(i8)===!0"),
        ),
    ),
    "priority_filter_pinned_recency_sorting": (
        (
            b("function QUc(e,t){return(0,uWc.default)(t,t=>o8(e,t))}"),
            b("function QUc(e,t){return(0,uWc.default)(t,t=>o8(e,t))}function CodexPriorityRecencySort(e,t,n){return[...t].map((t,r)=>({item:t,index:r,recencyAt:n.get(o8(e,t))??0})).sort((e,t)=>t.recencyAt-e.recencyAt||e.index-t.index).map(({item:e})=>e)}"),
        ),
        (
            b("pinnedItems:QUc(e.get,e.get(CWc,t)),recentRecencyByItemId:a"),
            b("pinnedItems:CodexPriorityRecencySort(e.get,e.get(CWc,t),i),recentRecencyByItemId:a"),
        ),
        (
            b("k=QUc(u,[...x,...u(CWc,d.sidebarMode).filter(e=>{let t=o8(u,e);return!E||!D.has(t)||O.has(t)})].filter(e=>!n.has(o8(u,e))&&aWc(u,e)))"),
            b("k=CodexPriorityRecencySort(u,QUc(u,[...x,...u(CWc,d.sidebarMode).filter(e=>{let t=o8(u,e);return!E||!D.has(t)||O.has(t)})].filter(e=>!n.has(o8(u,e))&&aWc(u,e))),v)"),
        ),
    ),
    "priority_project_context_subtitle": (
        (
            b("let u;t[8]!==n||t[9]!==i?(u=i===`chatgpt`&&n!==`chat`?(0,M8.jsxs)(M8.Fragment,{children:[(0,M8.jsx)(`span`,{\"aria-hidden\":!0,children:(0,M8.jsx)(Z,{id:`sidebarElectron.priorityThreads.details.workSeparator`,defaultMessage:`\u00b7`,description:`Separator between a Priority thread's project and its work type`})}),(0,M8.jsx)(Z,{...N8.work})]}):null,t[8]=n,t[9]=i,t[10]=u):u=t[10];"),
            b("let u=null/*priority-project-context-subtitle*/;"),
        ),
        (
            b("function iil(e){let t=(0,sil.c)(5),n=e.entryFallback?.kind===`local`?e.entryFallback:null,r;t[0]===n?r=t[1]:(r=n?.conversationId==null?null:{hostId:n.hostId??n.summary?.hostId??`local`,threadId:n.conversationId},t[0]=n,t[1]=r);let i=Po(Krl,r)??e.secondaryContent,a;return t[2]!==e||t[3]!==i?(a=(0,U5.jsx)(q3c,{...e,secondaryContent:i}),t[2]=e,t[3]=i,t[4]=a):a=t[4],a}"),
            b("function iil(e){let t=(0,sil.c)(5),n=e.entryFallback?.kind===`local`?e.entryFallback:null,r;t[0]===n?r=t[1]:(r=n?.conversationId==null?null:{hostId:n.hostId??n.summary?.hostId??`local`,threadId:n.conversationId},t[0]=n,t[1]=r);let i=Po(Krl,r),a=e.secondaryContent?.props?.projectGroup!=null,o=a?(i==null?e.secondaryContent:(0,U5.jsxs)(U5.Fragment,{children:[e.secondaryContent,` \\u00b7 `,i]})):i??e.secondaryContent,s;return t[2]!==e||t[3]!==o?(s=(0,U5.jsx)(q3c,{...e,secondaryContent:o}),t[2]=e,t[3]=o,t[4]=s):s=t[4],s}"),
        ),
    ),
    "plan_pending_detection": (
        (
            b("rt=Po(Eyn,n),it=Po(qA,n),at=qe??`local`,q;"),
            b("rt=Po(Eyn,n),it=Po(qA,n),CodexPlanPending=Po(Svr,n)?.some?.(H1t),at=qe??`local`,q;"),
        ),
        (
            b("unreadCount:wt||Me?0:et??0}"),
            b("unreadCount:wt||Me?0:et??0,plan:CodexPlanPending}"),
        ),
    ),
    "plan_pending_yellow_indicator": (
        (
            b("function S8(e){let t=(0,KJc.c)(4),{statusState:n}=e;if((n.unreadCount??0)>0){let e=n.unreadCount??0,r;return t[0]===e?r=t[1]:(r=(0,C8.jsx)(UJc,{count:e}),t[0]=e,t[1]=r),r}if(n.type===`loading`){let e;return t[2]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,C8.jsx)(GJc,{}),t[2]=e):e=t[2],e}if(n.unread===!0){let e;return t[3]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,C8.jsx)(WJc,{}),t[3]=e):e=t[3],e}return null}"),
            b("function S8({statusState:e}){return(!e.plan||!e.unread)&&(e.unreadCount??0)>0?(0,C8.jsx)(UJc,{count:e.unreadCount}):e.type===`loading`?(0,C8.jsx)(GJc,{}):e.unread?(0,C8.jsx)(WJc,{plan:e.plan}):null}"),
        ),
        (
            b("function UJc(e){let t=(0,KJc.c)(3),{count:n}=e,r=n>99?`99+`:n,i;t[0]===Symbol.for(`react.memo_cache_sentinel`)?(i={backgroundColor:`color-mix(in srgb, var(--color-text-info) 18%, transparent)`,boxShadow:`inset 0 0 0 1px color-mix(in srgb, var(--color-text-info) 72%, transparent)`,color:`var(--color-text-info)`},t[0]=i):i=t[0];let a;return t[1]===r?a=t[2]:(a=(0,C8.jsx)(`div`,{className:`relative flex h-5 min-w-5 shrink-0 items-center justify-center`,children:(0,C8.jsx)(`span`,{className:`flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[11px] leading-none font-semibold`,style:i,children:r})}),t[1]=r,t[2]=a),a}"),
            b("function UJc({count:e}){return(0,C8.jsx)(`div`,{className:`relative flex h-5 min-w-5 shrink-0 items-center justify-center`,children:(0,C8.jsx)(`span`,{className:`flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[11px] leading-none font-semibold`,style:{backgroundColor:`color-mix(in srgb, var(--color-text-info) 18%, transparent)`,boxShadow:`inset 0 0 0 1px color-mix(in srgb, var(--color-text-info) 72%, transparent)`,color:`var(--color-text-info)`},children:e>99?`99+`:e})})}"),
        ),
        (
            b("function WJc(){let e=(0,KJc.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`)?(t=(0,C8.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-codex-description`,children:(0,C8.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,C8.jsx)(`span`,{className:`absolute inset-0 rounded-full`,style:{backgroundColor:`var(--color-text-info)`}})})}),e[0]=t):t=e[0],t}"),
            b("function WJc({plan:e}){return(0,C8.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-codex-description`,children:(0,C8.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,C8.jsx)(`span`,{className:`absolute inset-0 rounded-full`,style:{backgroundColor:e?`var(--color-text-warning)`:`var(--color-text-info)`}})})})}"),
        ),
        (
            b("function GJc(){let e=(0,KJc.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`)?(t=(0,C8.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-text/70`,children:(0,C8.jsx)(jm,{className:`icon-xs shrink-0`,animationDurationMs:2e3})}),e[0]=t):t=e[0],t}"),
            b("function GJc(){return(0,C8.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-text/70`,children:(0,C8.jsx)(jm,{className:`icon-xs shrink-0`,animationDurationMs:2e3})})}"),
        ),
        (
            b("function qJc(e){let t=(0,JJc.c)(6),{hasUnreadActivity:n,endContent:r}=e;if(!n){let e;return t[0]===r?e=t[1]:(e=r==null?null:(0,YJc.jsx)(YJc.Fragment,{children:r}),t[0]=r,t[1]=e),e}if(r==null){let e;return t[2]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,YJc.jsx)(S8,{statusState:{type:`idle`,unread:!0}}),t[2]=e):e=t[2],e}let i;t[3]===Symbol.for(`react.memo_cache_sentinel`)?(i=(0,YJc.jsx)(S8,{statusState:{type:`idle`,unread:!0}}),t[3]=i):i=t[3];let a;return t[4]===r?a=t[5]:(a=(0,YJc.jsxs)(`span`,{className:`flex shrink-0 items-center gap-1`,children:[r,i]}),t[4]=r,t[5]=a),a}"),
            b("function qJc({hasUnreadActivity:e,endContent:t}){let n=(0,YJc.jsx)(S8,{statusState:{type:`idle`,unread:!0}});return e?t==null?n:(0,YJc.jsxs)(`span`,{className:`flex shrink-0 items-center gap-1`,children:[t,n]}):t}"),
        ),
    ),
}


# These bindings are introduced at bundle scope. The builder verifies their
# token-level absence in the official entry and their exact final occurrence
# counts, so minifier-name collisions fail before an artifact can be produced.
INJECTED_GLOBAL_IDENTIFIER_COUNTS = {
    "priority_click_hold": {
        "aad": 7,
        "aaf": 4,
    },
    "priority_filter_pinned_recency_sorting": {
        "CodexPriorityRecencySort": 3,
    },
}

# The official bundle's CH initializer is unrelated to Priority holds. Keep
# these exact signatures intact to prevent a regression to the 1.8.15 clash.
PROTECTED_OFFICIAL_SIGNATURES = (
    b"yca,SH,CH=n((()=>",
    b"Y as sFt,CH as sG,",
)
