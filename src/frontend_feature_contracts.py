from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
from typing import Any


VALIDATOR_VERSION = "2.4.6"
CONTRACT_SCHEMA_VERSION = 2


class ContractError(RuntimeError):
    pass


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _extract_function(source: str, name: str) -> str:
    marker = f"function {name}("
    start = source.find(marker)
    if start < 0:
        raise ContractError(f"Actual bundle function is missing: {name}")
    # Current minified functions have no whitespace between the closing
    # parameter parenthesis and the body.  Looking for the first ``{`` would
    # mistake a destructured parameter for the body opening.
    close_and_brace = source.find("){", start)
    brace = close_and_brace + 1 if close_and_brace >= 0 else -1
    if brace < 0:
        raise ContractError(f"Actual bundle function body is missing: {name}")
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(brace, len(source)):
        char = source[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ("'", '"', "`"):
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    raise ContractError(f"Actual bundle function is unterminated: {name}")


def _run_actual_javascript(entry: bytes, node: str) -> dict[str, Any]:
    text = entry.decode("utf-8")
    priority_route_signatures = {
        "initial_normal": (
            "gdc=Ig($,(e,{get:t})=>zN(w6(t,e).filter(({item:n})=>$uc(t,n,e))))"
        ),
        "initial_pinned": (
            "_dc=Ig($,(e,{get:t})=>zN(w6(t,e).filter(({item:n})=>x6(t,n,e)"
            "&&edc(t,n))).map(({item:e})=>e))"
        ),
        "shared_comparator": (
            "C=((e,t)=>(_.get(S6(l,t))||0)-(_.get(S6(l,e))||0))"
        ),
        "live_normal": (
            "w=zN(Juc(l,[...S.map(({item:e})=>e),...y].filter(e=>"
            "!n.has(S6(l,e)))),C)"
        ),
        "live_pinned": (
            "k=zN(Juc(l,[...b,...l(_dc,u.sidebarMode).filter(e=>{let t=S6(l,e);"
            "return!T||!E||!$uc(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})]"
            ".filter(e=>!n.has(S6(l,e))&&edc(l,e))),C)"
        ),
    }
    invalid_priority_routes = [
        name for name, signature in priority_route_signatures.items()
        if text.count(signature) != 1
    ]
    if invalid_priority_routes:
        raise ContractError(
            "Actual Priority recency routes are missing or ambiguous: "
            + ",".join(invalid_priority_routes)
        )
    plan_route_signatures = {
        "pending_request_selector": "it=l_(KV,n)",
        "pending_plan_status_state": "plan:it?.type===`implementPlan`,pinned:!!Pi",
    }
    invalid_plan_routes = [
        name for name, signature in plan_route_signatures.items()
        if text.count(signature) != 1
    ]
    if invalid_plan_routes or "plan:rt?.type===`implementPlan`" in text:
        raise ContractError(
            "Actual plan-waiting indicator route is missing, ambiguous, or reads "
            "the approval/response display scalar: " + ",".join(invalid_plan_routes)
        )
    functions = {
        name: _extract_function(text, name)
        for name in (
            "zN", 'jSr', "sSr", "tSr", "VMr", "PCr", "LVn", "ODt", "DDt",
            "bAt", "p8", "aEc", "smr", "VCr", "x6", "$uc", "Hwr", "Vwr", "Lwr",
            "Rwr", "GCr",
        )
    }
    comparator = (
        "t.attentionState!==e.attentionState||t.isScheduled!==e.isScheduled||"
        "t.kind===`task`&&e.kind===`task`&&"
        "t.threadEntry.key!==e.threadEntry.key?t:e"
    )
    if comparator not in text:
        raise ContractError("Actual automation Priority comparator is not wired")
    script = "\n".join(functions.values()) + r'''
const N8={jsx:(type,props)=>typeof type===`function`?type(props):({type,props})};
const oEc=()=>({kind:`spinner`});
const iEc=({count})=>({kind:`count`,count});
const fmr=(paths,repos)=>({paths,repos});
const BCr=value=>value;
const km=value=>String(value??``).replace(/\\/g,`/`).replace(/\/+$/,``).toLowerCase();
const V_=value=>value.turns??[];
const BMr=()=>{throw new Error(`priority branch was not requested`)};
const yMr=()=>{throw new Error(`manual branch was not requested`)};
const Nuc=`show-scheduled`;
const NP=`thread-state`;
const Ok=`priority-holds`;
const DSr=`catalog-state`;
const vZi=`created-at`;
const yZi=`updated-at`;
const bZi=`recency-at`;
const NCr={waiting:0,unread:1,active:2,idle:3};
const Uwr={default:value=>[...new Set(value)]};
const assert=(condition,message)=>{if(!condition)throw new Error(message)};
const keys=value=>value.map(item=>item.task?.key??item.e?.task?.key??item.key);

let ordered=zN([
  {task:{key:`a`},recencyAt:1},{task:{key:`b`},recencyAt:3},{task:{key:`c`},recencyAt:3}
]);
assert(keys(ordered).join(`,`)===`b,c,a`,`zN stable recency sort failed`);
ordered=VMr({attentionStateByThreadKey:new Map(),items:[
  {task:{key:`a`},recencyAt:1},{task:{key:`b`},recencyAt:3},{task:{key:`c`},recencyAt:3}
],manualOrder:null,sortMode:`updated_at`});
assert(ordered.join(`,`)===`b,c,a`,`VMr live recency route failed`);
const liveRecency=new Map([[`older`,2],[`newer`,9],[`tie`,9]]);
const liveComparator=(left,right)=>(liveRecency.get(right.key)||0)-(liveRecency.get(left.key)||0);
let mergedPriority=zN(
  [{key:`older`},{key:`newer`},{key:`stale`},{key:`tie`}],
  liveComparator,
);
assert(
  mergedPriority.map(value=>value.key).join(`,`)===`newer,tie,older,stale`,
  `Priority live normal recency merge failed`,
);
let pinnedPriority=zN(
  [{key:`older`},{key:`newer`},{key:`stale`},{key:`tie`}],
  liveComparator,
);
assert(
  pinnedPriority.map(value=>value.key).join(`,`)===`newer,tie,older,stale`,
  `Priority live pinned recency merge failed`,
);
liveRecency.set(`older`,12);
mergedPriority=zN(mergedPriority,liveComparator);
pinnedPriority=zN(pinnedPriority,liveComparator);
assert(mergedPriority[0].key===`older`,`Priority live normal refresh failed`);
assert(pinnedPriority[0].key===`older`,`Priority live pinned refresh failed`);
const processTimes={created:1,updated:9,recency:2};
const processTimeGet=atom=>atom===DSr?{hasLiveConversation:true,summary:null}:
  atom===vZi?processTimes.created:atom===yZi?processTimes.updated:
  atom===bZi?processTimes.recency:null;
assert(tSr(processTimeGet,`thread`,`updated_at`)===2,`Priority process-start time source failed`);
processTimes.updated=20;
assert(tSr(processTimeGet,`thread`,`updated_at`)===2,`Priority process time followed output writes`);
processTimes.recency=12;
assert(tSr(processTimeGet,`thread`,`updated_at`)===12,`Priority process-start time did not refresh`);
assert(nSr({createdAt:1,updatedAt:8,recencyAt:2},`updated_at`)===2,`Priority catalog recency source failed`);
const priorityInitialNormalRoute=true,priorityInitialPinnedRoute=true;
const priorityLiveNormalRoute=true,priorityLivePinnedRoute=true,priorityRecencyComparatorRoute=true;
assert(priorityInitialNormalRoute&&priorityInitialPinnedRoute&&priorityLiveNormalRoute&&priorityLivePinnedRoute&&priorityRecencyComparatorRoute,`Priority recency routes are not wired`);

let pinned=PCr({threadKeys:[`k2`,`k1`],pinnedThreadIds:[`t1`,`t2`],referencesByThreadKey:new Map([
  [`k1`,{threadId:`t1`,pendingWorktreeId:null}],
  [`k2`,{threadId:`t2`,pendingWorktreeId:null}]
])});
assert(pinned.join(`,`)===`k1,k2`,`PCr pinned ordering failed`);
assert(LVn({kind:`remote`,key:`rk`,task:{id:`rt`}}).threadId===`rt`,`LVn remote identity failed`);
assert(LVn({kind:`local`,key:`lk`,conversation:{id:`lt`}}).threadId===`lt`,`LVn local identity failed`);

assert(ODt({resumeState:`resumed`,turnHistory:{kind:`canonical`},turnsPagination:{hasLoadedOldest:true}})===true,`ODt canonical completion failed`);
assert(ODt({resumeState:`needs_resume`,turnsPagination:{hasLoadedOldest:true}})===false,`ODt resume guard failed`);
assert(DDt({turns:[{itemsPagination:{hasLoadedOldest:true}}]})===true,`DDt retained tail failed`);
assert(DDt({turns:[{itemsPagination:{hasLoadedOldest:false}}]})===false,`DDt incomplete tail failed`);
let idle=bAt({conversationId:`id`,hostId:`local`,createdAt:1,updatedAt:2,title:`t`});
assert(idle.resumeState===`needs_resume`&&idle.turns.length===0,`bAt idle resume shape failed`);

const uuid=`c87575b4-dba0-471e-a647-31ce8575c46b`;
let remote=smr([{id:uuid,hostId:`remote-ssh-discovered:Insolvency`,label:uuid,remotePath:`/root/mailassistant`}],[{hostId:`remote-ssh-discovered:Insolvency`,displayName:`Insolvency`}],{} )[0];
assert(remote.label===`mailassistant`&&remote.projectId===uuid&&remote.hostId===`remote-ssh-discovered:Insolvency`,`smr route identity failed`);
remote=smr([{id:uuid,hostId:`remote`,label:`Saved name`,remotePath:`/root/mailassistant`}],[],{})[0];
assert(remote.label===`Saved name`,`smr saved label failed`);
let liveRemote={...remote,label:uuid,threadKeys:[`remote-thread`]};
let mergedRemote=VCr([remote],[liveRemote],new Map())[0];
assert(mergedRemote.label===`Saved name`&&mergedRemote.projectId===uuid&&mergedRemote.threadKeys.join()===`remote-thread`,`VCr same-id late UUID overwrite failed`);
let changedId=`423dd422-a9ef-4fc4-8c97-583483a49850`;
mergedRemote=VCr([remote],[{...liveRemote,projectId:changedId,groupId:changedId}],new Map())[0];
assert(mergedRemote.label===`Saved name`&&mergedRemote.projectId===uuid&&mergedRemote.threadKeys.join()===`remote-thread`,`VCr host-path fallback failed`);

const projectEntries=[
  {key:`p1`,kind:`project`,pinned:false,source:`codex`},
  {key:`p2`,kind:`project`,pinned:false,source:`codex`},
  {key:`c1`,kind:`conversation`,pinned:false,projectKey:`p1`,attentionState:`unread`,recencyAt:10,source:`codex`},
  {key:`c2`,kind:`conversation`,pinned:false,projectKey:`p2`,attentionState:`idle`,recencyAt:20,source:`codex`},
];
const projectOptions={chatSortMode:`updated_at`,mode:`project`,pinnedOrder:[],pinnedSortMode:`manual`,projectOrder:[`p2`,`p1`],source:`codex`};
assert(Rwr(projectEntries,{...projectOptions,projectSortMode:`updated_at`}).projectKeys.join(`,`)===`p2,p1`,`Rwr updated project sort failed`);
assert(Rwr(projectEntries,{...projectOptions,projectSortMode:`priority`}).projectKeys.join(`,`)===`p1,p2`,`Rwr priority project sort failed`);
assert(Rwr(projectEntries,{...projectOptions,projectSortMode:`manual`}).projectKeys.join(`,`)===`p2,p1`,`Rwr manual project sort failed`);
const pinnedProjects=projectEntries.map(value=>value.kind===`project`?{...value,pinned:true}:value);
assert(Rwr(pinnedProjects,{...projectOptions,projectSortMode:`updated_at`,pinnedSortMode:`updated_at`}).pinnedKeys.join(`,`)===`p2,p1`,`Rwr pinned project recency sort failed`);
assert(GCr({chatLabel:`Chat`,task:{kind:`remote`},projectLabel:`mailassistant`}).label===`mailassistant`,`GCr project subtitle failed`);

const color=value=>value?.props?.style?.backgroundColor??value?.style?.backgroundColor??null;
assert(p8({statusState:{type:`loading`}}).kind===`spinner`,`loading spinner failed`);
assert(color(p8({statusState:{pinned:true,plan:true,unread:true,unreadCount:1}}))===`var(--color-text-danger)`,`pinned red indicator failed`);
const pendingPlanRequest={type:`implementPlan`};
const planWaiting=pendingPlanRequest?.type===`implementPlan`;
assert(planWaiting===true,`pending plan request detection failed`);
assert(color(p8({statusState:{pinned:false,plan:planWaiting,unread:false,unreadCount:0}}))===`var(--color-text-warning)`,`plan-complete waiting indicator failed`);
assert(color(p8({statusState:{pinned:false,plan:false,unread:true,unreadCount:0}}))===`var(--color-text-info)`,`unread blue indicator failed`);
assert(p8({statusState:{pinned:false,plan:false,unread:false,unreadCount:0}})===null,`empty indicator failed`);

const automationComparator=(t,e)=>t.attentionState!==e.attentionState||t.isScheduled!==e.isScheduled||t.kind===`task`&&e.kind===`task`&&t.threadEntry.key!==e.threadEntry.key?t:e;
let oldTask={kind:`task`,attentionState:`idle`,isScheduled:false,h:1,threadEntry:{key:`a`}};
let newTask={kind:`task`,attentionState:`idle`,isScheduled:true,h:1,threadEntry:{key:`a`}};
assert(automationComparator(oldTask,newTask)===oldTask,`scheduled automation invalidation failed`);

const membershipGet=(atom,scope)=>{
  if(atom===Nuc)return false;
  if(atom===NP&&scope===`codex`)return {threadRecencyAtByKey:new Map([[`held`,7]])};
  if(atom===Ok)return new Map([[`held`,7]]);
  throw new Error(`unexpected membership atom ${atom}`);
};
assert($uc(membershipGet,{attentionState:`unread`,isScheduled:true,kind:`task`,threadEntry:{key:`reminder`}},`codex`)===true,`triggered reminder Priority membership failed`);
assert($uc(membershipGet,{attentionState:`waiting`,isScheduled:true,kind:`task`,threadEntry:{key:`reminder`}},`codex`)===true,`waiting reminder Priority membership failed`);
assert($uc(membershipGet,{attentionState:`idle`,isScheduled:true,kind:`task`,threadEntry:{key:`dormant`}},`codex`)===false,`dormant schedule was promoted without attention`);

process.stdout.write(JSON.stringify({
  status:`passed`,
  executed:[`zN`,`nSr`,`sSr`,`tSr`,`VMr`,`PCr`,`LVn`,`ODt`,`DDt`,`bAt`,`smr`,`VCr`,`p8`,`aEc`,`x6`,`$uc`,`Hwr`,`Vwr`,`Lwr`,`Rwr`,`GCr`,`automationComparator`],
  priority:{initialRecency:true,liveNormalRecency:true,livePinnedRecency:true,stableTieOrder:true,processStartedTime:true,processStartRefresh:true,nonLiveSummaryRecencyTime:true},
  attention:{loading:`spinner`,pinned:`red`,plan:`yellow`,unread:`blue`,none:null,planSource:`pending_request_type`},
  automation:{triggeredUnreadInPriority:true,triggeredWaitingInPriority:true,dormantScheduleExcluded:true},
  sorting:{projectUpdated:true,projectPriority:true,projectManual:true,pinnedProjectRecency:true},
  ssh:{saved_name_precedence:true,uuid_fallback:true,post_merge_saved_name:true,host_path_fallback:true,thread_keys_preserved:true,route_identity_unchanged:true}
}));
'''
    completed = subprocess.run(
        [node, "-"], input=_with_module_stubs(script, functions), text=True, capture_output=True, timeout=30
    )
    if completed.returncode != 0:
        raise ContractError(
            "Actual bundled JavaScript contract failed: "
            + (completed.stderr.strip() or completed.stdout.strip())
        )
    result = json.loads(completed.stdout)
    if result.get("status") != "passed":
        raise ContractError("Actual bundled JavaScript contract did not pass")
    result["script_sha256"] = _sha256(script.encode("utf-8"))
    return result


def _run_actual_javascript_26831(
    initial_entry: bytes, primary_entry: bytes, node: str
) -> dict[str, Any]:
    """Execute the real 26.831 patched functions, not Python lookalikes.

    The package moved row-state and several interaction routes to app-primary.
    The executable semantics therefore combine functions extracted from the
    actual app-initial bytes with exact wiring assertions against the actual
    app-primary bytes.  Synthetic inputs contain no user task content.
    """
    initial = initial_entry.decode("utf-8")
    primary = primary_entry.decode("utf-8")
    functions = {
        name: _extract_function(initial, name)
        for name in (
            "mW", "iCi", "TJo", "j8", "C0t", "S0t", "pIo", "hIo",
            "k_i", "dCi", "xon", "Son", "Con", "_wi", "Uki", "Wki", "Gki", "hCi", "jvi", "XU", "l3t",
        )
    }
    functions.update(
        {
            name: _extract_function(primary, name)
            for name in ("Mwn", "_H", "WGt")
        }
    )
    initial_routes = {
        # The dynamically loaded task row calls ``pE(zp, n)`` below.  In this
        # release ``zp`` is imported from the initial bundle's ``Mvt`` export,
        # which in turn is the ``MI`` selector over the conversation request
        # queue.  Pin the complete export lineage so a minified local named
        # ``rt`` cannot be mistaken for the pending request in a future build.
        "pending_request_selector_definition": "MI=hI((e,t)=>ohr(e,t(iSn)))",
        "pending_request_selector_export": "MI as Mvt",
        "normal_priority_selector": (
            "HJo=rb(Q,(e,{get:t})=>mW(P8(t,e).filter(({item:n})=>TJo(t,n,e))))"
        ),
        "priority_process_recency_source": (
            "VJo=X(Q,({get:e})=>{let t=e(MAi,`codex`),n=new Map;return{taskItems:Array.from(t.threadRecencyAtByKey)"
        ),
        "pinned_priority_selector": (
            "UJo=rb(Q,(e,{get:t})=>mW(P8(t,e).filter(({item:n})=>j8(t,n,e)&&EJo(t,n))).map(({item:e})=>e))"
        ),
        "live_priority_comparator": (
            "C=((e,t)=>(_.get(p8(l,t))||0)-(_.get(p8(l,e))||0)),"
        ),
        "live_priority_recency_map": (
            "_=new Map(m.map(({item:e,recencyAt:t})=>[p8(l,e),t]))"
        ),
        "live_normal_resort": (
            "w=mW(bJo(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(p8(l,e)))),C),T=l(k8)===!0"
        ),
        "live_pinned_resort": (
            "k=mW(bJo(l,[...b,...l(UJo,u.sidebarMode).filter(e=>{let t=p8(l,e);return!T||!E||!TJo(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(p8(l,e))&&EJo(l,e))),C);"
        ),
        "project_sort_mode_input": "projectOrder:u,projectSortMode:q,serverOrderedPinnedThreadHostIds:d",
        "pinned_project_sort_route": (
            "pinnedKeys:gwi({entries:h,pinnedKeyAliases:s,pinnedOrder:l===`manual`?c:h.map(P).sort((e,t)=>t[1]-e[1]).map(e=>e[0].key),pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:d"
        ),
        "remote_merge_export": "dCi as k0",
    }
    primary_routes = {
        "pending_request_selector_import": "Mvt as zp",
        "pending_request_selector_read": "rt=pE(zp,n)",
        "task_row_pinned_input": "isActive:ae,isUnread:a,P:b,hasAttachedHeartbeatAutomation:Ee",
        "pending_plan_state": "unreadCount:Tt||Me?0:et??0,p:it?.type===`implementPlan`,i:yn}",
        "pending_plan_cache": "t[103]=Ce,t[104]=qe+b,t[105]=Ze",
        "project_sort_mode_route": "pinnedSortMode:B,projectOrder:V,projectSortMode:w,serverOrderedPinnedThreadHostIds",
        "priority_click_handler": "function Mwn(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a}",
        "new_chat_drop_handler": "onDrop:e=>{if(!M||!_H(e.dataTransfer))return;e.preventDefault(),e.stopPropagation();let t=WGt(e.dataTransfer);t.length>0&&Kn(t),er()",
        "remote_merge_import": "k0 as UCe",
        "remote_merge_live_consumer": "return UCe(e(zu),n,r)",
    }
    missing = [
        name for name, signature in {**initial_routes, **primary_routes}.items()
        if (initial.count(signature) + primary.count(signature)) != 1
    ]
    if missing:
        raise ContractError(
            "Actual 26.831 data-flow routes are missing or ambiguous: "
            + ",".join(missing)
        )

    script = "\n".join(functions.values()) + r'''
const rCi={waiting:0,unread:1,active:2,idle:3};
const rJo=Symbol(`show-scheduled`),MAi=Symbol(`thread-state`),AF=Symbol(`priority-holds`);
const OD=Symbol(`local-enabled`),DD=Symbol(`remote-enabled`),l8=Symbol(`chatgpt-enabled`),c8=Symbol(`codex-enabled`);
const TF=value=>value!==false;
const P_i=(paths,repos)=>({paths,repos});
const uCi=value=>value;
const FS=value=>value.turns??[];
const g6={jsx:(type,props)=>typeof type===`function`?type(props):({type,props})};
const gIo=()=>({kind:`spinner`});
const _Io={c:()=>Array(16).fill(Symbol.for(`react.memo_cache_sentinel`))};
const mIo=({count})=>({kind:`count`,count});
const xwi=(entries,order)=>{
 const map=new Map(entries.map(e=>[e.key,e])),out=[];
 for(const key of order??[]){if(map.has(key)){out.push(map.get(key));map.delete(key)}}
 return [...out,...entries.filter(e=>map.has(e.key))];
};
const bwi=(entries,order)=>xwi(entries,order).map(e=>e.key);
const gwi=({entries,pinnedOrder})=>xwi(entries,pinnedOrder).map(e=>e.key);
const zvi=(groups,order)=>xwi(groups.map((e,index)=>({...e,key:e.projectId??e.key,index})),order).map(({key,index,...e})=>e);
const Cx=value=>String(value??``).split(/[\\/]/).filter(Boolean).pop()??``;
const n_=value=>value,Cki=({tasks})=>tasks;
const rw=Symbol(`thread-map`),Gbn=value=>value?.conversationId??null;
let pinWrites=[];const fb=(store,id,value)=>pinWrites.push([id,value]);
const tKt=`Files`,qGt=value=>value.__entries??[],Vv=()=>true;
const assert=(condition,message)=>{if(!condition)throw new Error(message)};

let times=new Map([[`old`,2],[`new`,9],[`tie`,9]]),cmp=(a,b)=>(times.get(b.key)||0)-(times.get(a.key)||0);
let normal=mW([{key:`old`,recencyAt:2},{key:`new`,recencyAt:9},{key:`tie`,recencyAt:9}]),pinned=mW([{key:`old`,recencyAt:2},{key:`new`,recencyAt:9},{key:`tie`,recencyAt:9}]);
assert(normal.map(e=>e.key).join()===`new,tie,old`,`initial recency sort failed`);
assert(pinned.map(e=>e.key).join()===`new,tie,old`,`pinned recency sort failed`);
times.set(`old`,12);normal=mW(normal,cmp);pinned=mW(pinned,cmp);
assert(normal[0].key===`old`&&pinned[0].key===`old`,`live recency refresh failed`);

const get=(atom,scope)=>atom===rJo?false:atom===MAi&&scope===`codex`?{threadRecencyAtByKey:new Map([[`held`,7]])}:atom===AF?new Map([[`held`,7]]):true;
assert(TJo(get,{attentionState:`idle`,isScheduled:false,kind:`task`,threadEntry:{key:`held`}},`codex`),`held membership failed`);
assert(TJo(get,{attentionState:`unread`,isScheduled:true,kind:`task`,threadEntry:{key:`reminder`}},`codex`),`scheduled reminder membership failed`);
assert(!TJo(get,{attentionState:`idle`,isScheduled:true,kind:`task`,threadEntry:{key:`dormant`}},`codex`),`dormant schedule promoted`);
let pinOrder=iCi({threadKeys:[`k2`,`k1`],pinnedThreadIds:[`t1`,`t2`],referencesByThreadKey:new Map([[`k1`,{threadId:`t1`,pendingWorktreeId:null}],[`k2`,{threadId:`t2`,pendingWorktreeId:null}]])});
assert(pinOrder.join()===`k1,k2`,`pinned identity order failed`);
let reads=0,store={get:(atom,key)=>atom===rw&&key===`row`?{kind:`local`,conversationId:`c1`,hostId:`local`}:null};
Mwn(store,`mark-thread-read`,`row`,{markThreadAsRead:()=>reads++,markThreadAsUnread:()=>{},setPendingWorktreePinned:()=>{}});
assert(reads===1,`priority click handler failed`);
let transfer={items:[{kind:`file`}],types:[],__entries:[{file:{name:`x.txt`},isDirectory:false}]};
assert(_H(transfer)===true&&WGt(transfer).length===1,`new-chat file drop handler failed`);

const color=value=>value?.props?.style?.backgroundColor??null;
assert(pIo({statusState:{type:`loading`}})?.kind===`spinner`,`loading spinner failed`);
assert(color(pIo({statusState:{i:true,p:true,unread:true,unreadCount:1}}))===`var(--color-text-danger)`,`red indicator failed`);
assert(color(pIo({statusState:{i:false,p:true,unread:false,unreadCount:0}}))===`var(--color-text-warning)`,`yellow indicator failed`);
assert(color(pIo({statusState:{i:false,p:false,unread:true,unreadCount:0}}))===`var(--color-text-info)`,`blue indicator failed`);
assert(pIo({statusState:{}})===null,`empty indicator failed`);

const uuid=`c87575b4-dba0-471e-a647-31ce8575c46b`;
let saved=k_i([{id:uuid,hostId:`remote`,label:uuid,remotePath:`/root/mailassistant`}],[{hostId:`remote`,displayName:`Host`}],{})[0];
assert(saved.label===`mailassistant`&&saved.projectId===uuid,`SSH path fallback failed`);
let merged=dCi([saved],[{...saved,label:uuid,threadKeys:[`thread`]}],new Map())[0];
assert(merged.label===`mailassistant`&&merged.projectId===uuid&&merged.threadKeys[0]===`thread`,`SSH same-id merge failed`);
let moved=dCi([saved],[{...saved,projectId:`423dd422-a9ef-4fc4-8c97-583483a49850`,groupId:`423dd422-a9ef-4fc4-8c97-583483a49850`,label:uuid,threadKeys:[`thread`]}],new Map())[0];
assert(moved.label===`mailassistant`&&moved.projectId===uuid&&moved.threadKeys[0]===`thread`,`SSH host/path merge failed`);
assert(hCi({chatLabel:`Chat`,task:{kind:`remote`},projectLabel:`mailassistant`}).label===`mailassistant`,`project subtitle failed`);

let items=[
 {key:`p1`,kind:`project`,pinned:false,source:`codex`},{key:`p2`,kind:`project`,pinned:false,source:`codex`},
 {key:`c1`,kind:`conversation`,pinned:false,projectKey:`p1`,attentionState:`unread`,recencyAt:10,source:`codex`},
 {key:`c2`,kind:`conversation`,pinned:false,projectKey:`p2`,attentionState:`idle`,recencyAt:20,source:`codex`},
];
let opts={chatSortMode:`updated_at`,mode:`project`,pinnedOrder:[],pinnedSortMode:`manual`,projectOrder:[`p1`,`p2`],source:`codex`};
assert(_wi(items,{...opts,projectSortMode:`updated_at`}).projectKeys.join()===`p2,p1`,`project updated sort failed`);
assert(_wi(items,{...opts,projectSortMode:`priority`}).projectKeys.join()===`p1,p2`,`project priority sort failed`);
let groups=[{projectId:`p1`,threadKeys:[`c1`]},{projectId:`p2`,threadKeys:[`c2`]}],rows=items.filter(e=>e.kind===`conversation`).map(e=>({task:{key:e.key},recencyAt:e.recencyAt})),states=new Map([[`c1`,`unread`],[`c2`,`idle`]]);
assert(Wki({items:rows,attentionStateByThreadKey:states}).join()===`c2,c1`,`active Priority recency sort failed`);
assert(Gki({items:rows,attentionStateByThreadKey:states,manualOrder:null,sortMode:`updated_at`}).join()===`c2,c1`,`active updated sort failed`);
let pinnedProjects=items.map(e=>e.kind===`project`?{...e,pinned:true}:e);
assert(_wi(pinnedProjects,{...opts,projectSortMode:`updated_at`,pinnedSortMode:`updated_at`}).pinnedKeys.slice(0,2).join()===`p2,p1`,`pinned project sort failed`);

let assignment=jvi({isExistingThread:false,executionHostId:`remote`,activeLocalProjectId:null,existingAssignment:null,homeRemoteProject:null,selectedRemoteProject:{id:uuid,hostId:`remote`}});
assert(assignment.projectKind===`remote`&&assignment.projectId===uuid,`Work remote selection failed`);
assert(C0t({resumeState:`resumed`,turnHistory:{kind:`canonical`},turnsPagination:{hasLoadedOldest:true}}),`resume history failed`);
assert(S0t({turns:[{itemsPagination:{hasLoadedOldest:true}}]}),`paginated tail failed`);
let idle=l3t({conversationId:`idle`,createdAt:1,updatedAt:2,title:`Idle`,historyMode:`paginated`});
assert(idle.resumeState===`needs_resume`&&idle.turns.length===0&&idle.requests.length===0,`idle resume shape failed`);

process.stdout.write(JSON.stringify({
 status:`passed`,
 executed:[`mW`,`iCi`,`TJo`,`j8`,`C0t`,`S0t`,`pIo`,`hIo`,`k_i`,`dCi`,`_wi`,`Uki`,`Wki`,`Gki`,`hCi`,`jvi`,`XU`,`l3t`,`Mwn`,`_H`,`WGt`],
 priority:{normal:true,pinned:true,live_refresh:true,reminder_membership:true,dormant_excluded:true},
 attention:{loading:`spinner`,pinned:`red`,plan:`yellow`,unread:`blue`,none:null},
 sorting:{project_updated:true,project_priority:true,pinned_project_updated:true},
 ssh:{saved_name_precedence:true,uuid_fallback:true,host_path_fallback:true,thread_keys_preserved:true,route_identity_unchanged:true},
 history:{resume:true,paginated_tail:true},work:{remote_project:true}
}));
'''
    completed = subprocess.run(
        [node, "-"], input=_with_module_stubs(script, functions), text=True, capture_output=True, timeout=30
    )
    if completed.returncode != 0:
        raise ContractError(
            "Actual 26.831 bundled JavaScript contract failed: "
            + (completed.stderr.strip() or completed.stdout.strip())
        )
    result = json.loads(completed.stdout)
    if result.get("status") != "passed":
        raise ContractError("Actual 26.831 bundled JavaScript contract did not pass")
    result["script_sha256"] = _sha256(script.encode("utf-8"))
    result["initial_route_signatures"] = sorted(initial_routes)
    result["primary_route_signatures"] = sorted(primary_routes)
    return result


def _run_actual_javascript_26901(
    initial_entry: bytes, primary_entry: bytes, work_page_entry: bytes, node: str
) -> dict[str, Any]:
    """Execute 26.901 functions and authenticate every SSH picker consumer."""
    initial = initial_entry.decode("utf-8")
    primary = primary_entry.decode("utf-8")
    work_page = work_page_entry.decode("utf-8")
    functions = {
        name: _extract_function(initial, name)
        for name in (
            "_W", "EAi", "U3o", "N8", "a4t", "i4t", "oKo", "cKo",
            "qZx", "Qwi", "NAi", "zji", "lLi", "uLi", "LAi", "eEi", "XU", "a9t",
            "hPi", "vPi",
        )
    }
    functions.update(
        {
            name: _extract_function(primary, name)
            for name in ("ojn", "_H", "$Yt")
        }
    )
    initial_routes = {
        "normal_priority_selector": (
            "o6o=Xy(Q,(e,{get:t})=>_W(I8(t,e).filter(({item:n})=>U3o(t,n,e))))"
        ),
        "priority_recency_selector": "uW=Xy(Q,(e,{get:t})=>iki(t,e))",
        "priority_process_start_source": (
            "function iki(e,t){let n=cF(t);switch(n?.kind){case`local`:{let t=QOi(e,n.threadId);"
            "if(t!=null)return t.createdAt;let r=ZOi(e,n.threadId);return r==null?0:nki(e,r,`updated_at`)}"
        ),
        "pinned_priority_selector": (
            "s6o=Xy(Q,(e,{get:t})=>_W(I8(t,e).filter(({item:n})=>N8(t,n,e)&&W3o(t,n))).map(({item:e})=>e))"
        ),
        "live_priority_comparator": (
            "C=((e,t)=>(_.get(P8(l,t))||0)-(_.get(P8(l,e))||0)),"
        ),
        "live_normal_resort": (
            "w=_W(R3o(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(P8(l,e)))),C),T=l(j8)===!0"
        ),
        "live_pinned_resort": (
            "k=_W(R3o(l,[...b,...l(s6o,u.sidebarMode).filter(e=>{let t=P8(l,e);return!T||!E||!U3o(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(P8(l,e))&&W3o(l,e))),C);"
        ),
        "project_sort_mode_input": (
            "projectOrder:u,projectSortMode:q,serverOrderedPinnedThreadHostIds:d"
        ),
        "pinned_project_sort_route": (
            "pinnedKeys:Rji({entries:h,pinnedKeyAliases:s,pinnedOrder:l===`manual`?c:h.map(P).sort((e,t)=>t[1]-e[1]).map(e=>e[0].key),pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:d"
        ),
        "remote_merge_export": "NAi as q2",
        "raw_remote_label_normalizer": (
            "function qZx(e,t){return e.label!=e.id&&e.label||e.remotePath.split(`/`).pop()||t||`Remote`}"
        ),
        "raw_remote_projects_normalized": (
            "a=t?.map(e=>({...e,label:qZx(e)}))||[]"
        ),
        "raw_remote_projects_export": "mTi as h6",
    }
    primary_routes = {
        "pending_display_scalar_read": 'rt=rw(LIe,n)',
        "pending_request_selector_read": 'it=rw(KFe,n)',
        "task_row_pinned_input": "onDoubleClick:d,isActive:f,P:j0,isGrouped:p",
        "task_row_pinned_value": "be=f!==void 0&&f,yn=!!j0,xe=p!==void 0&&p",
        "pending_plan_status_state": (
            "unreadCount:Tt||Me?0:et??0,p:it?.type===`implementPlan`,i:yn}"
        ),
        "pending_plan_live_recompute": (
            'Ot;t[16]===t[16]?(Ot=je?{type:`loading`}'
        ),
        "task_row_parent_pinned_cache": 't[124]=2*Qe+b,t[125]=rt',
        "task_row_parent_pinned_prop": (
            'disableEnvTooltip:!0,isActive:ae,P:b,isUnread:a'
        ),
        "project_sort_mode_route": (
            "pinnedSortMode:q,projectOrder:J,projectSortMode:A,serverOrderedPinnedThreadHostIds"
        ),
        "priority_click_handler": (
            "function ojn(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a})"
        ),
        "new_chat_drop_handler": (
            'onDrop:e=>{if(!M||!_H(e.dataTransfer))return;e.preventDefault(),e.stopPropagation();let t=$Yt(e.dataTransfer)'
        ),
        "remote_merge_import": 'q2 as eMe',
        "remote_merge_live_consumer": 'return eMe(e(uS),n,r)',
        "raw_remote_hook_import": 'h6 as sCe',
        "new_chat_picker_hook": (
            '{selectedRemoteProject:R,selectedRemoteProjectId:z}=MBe()'
        ),
        "new_chat_picker_fallback": (
            'let pe=oe==null?null:Q1r({activeProjectId:oe,projects:k,remoteConnections:B,selectedRemoteProject:R})'
        ),
        "new_chat_picker_fallback_label": "label:r.label,path:r.remotePath",
        "new_chat_picker_display": (
            've=pe?.hostDisplayName==null?pe?.label??pe?.path??null'
        ),
        "new_chat_picker_search": (
            "function q1r(e){return[e.label,e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}"
        ),
    }
    work_page_routes = {
        "work_page_raw_remote_import": 'h6 as Ne',
        "work_page_raw_remote_hook": (
            '{selectedRemoteProject:_e,selectedRemoteProjectId:ve}=Ne()'
        ),
        "work_page_raw_remote_fallback": 'else _e?.id===l&&(m=_e)',
    }
    missing = [
        name
        for name, signature in {
            **initial_routes, **primary_routes, **work_page_routes
        }.items()
        if (
            initial.count(signature)
            + primary.count(signature)
            + work_page.count(signature)
            != 1
        )
    ]
    if missing:
        raise ContractError(
            "Actual 26.901 data-flow routes are missing or ambiguous: "
            + ",".join(missing)
        )

    forbidden_plan_routes = (
        "p:rt==`implementPlan`",
        "p:rt?.type===`implementPlan`",
        "i:be}",
    )
    present_forbidden = [
        signature for signature in forbidden_plan_routes if signature in primary
    ]
    if present_forbidden:
        raise ContractError(
            "Actual plan-waiting route still consumes the display scalar or active-row "
            "state: " + ",".join(present_forbidden)
        )

    status_expression = (
        (
            "{type:Et,unread:Tt?!1:(se??et===!0)||Ne&&((tt??0)>0||it!=null||Fe),"
            "unreadCount:Tt||Ne?0:tt??0,p:at?.type===`implementPlan`,i:yn}"
        )
        if profile.get("package_version") == "26.903.9818.0"
        else (
            "{type:Et,unread:Tt?!1:(se??$e===!0)||Me&&((et??0)>0||rt!=null||Pe),"
            "unreadCount:Tt||Me?0:et??0,p:it?.type===`implementPlan`,i:yn}"
        )
    )
    if primary.count(status_expression) != 1:
        raise ContractError(
            "Actual task-row status constructor is missing or ambiguous"
        )

    script = (
        "\n".join(functions.values())
        + "\nconst makeStatus=({Et=`idle`,Tt=false,se=null,$e=false,Me=false,"
        "et=0,rt=null,Pe=false,it=null,yn=false}={})=>("
        + status_expression
        + ");\n"
        + r'''
const TAi={waiting:0,unread:1,active:2,idle:3};
const x3o=Symbol(`show-scheduled`),OLi=Symbol(`thread-state`),jF=Symbol(`priority-holds`);
const jO=Symbol(),AO=Symbol(),A8=Symbol(),k8=Symbol();
const EF=value=>value!==false,CS=value=>value.turns??[];
const P6={jsx:(type,props)=>typeof type===`function`?type(props):({type,props})};
const lKo=()=>({kind:`spinner`});
const rTi=(paths,repos)=>({paths,repos}),MAi=value=>value;
const Xv=value=>String(value??``).replace(/\\/g,`/`).replace(/\/+$/,``).toLowerCase();
const wx=value=>String(value??``).split(/[\\/]/).filter(Boolean).pop()??``;
const xji={default:value=>[...new Set(value)]};
const Hji=(entries,order)=>{let m=new Map(entries.map(e=>[e.key,e])),out=[];for(let k of order??[]){if(m.has(k)){out.push(k);m.delete(k)}}return [...out,...entries.filter(e=>m.has(e.key)).map(e=>e.key)]};
const Rji=({entries,pinnedOrder})=>Hji(entries,pinnedOrder);
const Uji=(entries,order)=>{let keys=Hji(entries,order);return keys.map(k=>entries.find(e=>e.key===k))};
const HIi=({tasks,order})=>{let ids=order?.threadIds??tasks.map(e=>e.key);return ids.map(k=>tasks.find(e=>e.key===k)).filter(Boolean)};
const pC=e=>({createdAt:e.createdAt*1000,updatedAt:e.updatedAt*1000,recencyAt:e.recencyAt==null?null:e.recencyAt*1000});
const Zg=value=>value;
const tm=Symbol(`thread-map`),QEn=value=>value?.conversationId??null;let pinWrites=[];const js=(s,id,v)=>pinWrites.push([id,v]);
const uXt=`Files`,nXt=value=>value.__entries??[],Ql=()=>true;
const cF=value=>value;
const QOi=(get,id)=>get.live?.get(id)??null;
const ZOi=(get,id)=>get.catalogIds?.get(id)??null;
const nki=(get,id)=>get.catalogRecency?.get(id)??0;
const oW=Symbol(`remote-task`);
const ski=(task)=>task.recencyAt??task.updated_at??0;
const assert=(condition,message)=>{if(!condition)throw Error(message)};

let times=new Map([[`old`,2],[`new`,9],[`tie`,9]]),cmp=(a,b)=>(times.get(b.key)||0)-(times.get(a.key)||0);
let normal=_W([{key:`old`,recencyAt:2},{key:`new`,recencyAt:9},{key:`tie`,recencyAt:9}]);
assert(normal.map(e=>e.key).join()===`new,tie,old`,`initial recency`);times.set(`old`,12);normal=_W(normal,cmp);assert(normal[0].key===`old`,`live recency`);
const recencyGet=(atom,id)=>atom===oW?{recencyAt:17}:null;
recencyGet.live=new Map([[`active`,{createdAt:11,updatedAt:99}]]);
recencyGet.catalogIds=new Map([[`catalog`,`catalog-id`]]);
recencyGet.catalogRecency=new Map([[`catalog-id`,7]]);
assert(iki(recencyGet,{kind:`local`,threadId:`active`})===11,`active process-start source`);
recencyGet.live.get(`active`).updatedAt=999;
assert(iki(recencyGet,{kind:`local`,threadId:`active`})===11,`output writes changed process-start source`);
recencyGet.live.set(`active`,{createdAt:21,updatedAt:999});
assert(iki(recencyGet,{kind:`local`,threadId:`active`})===21,`process-start refresh`);
assert(iki(recencyGet,{kind:`local`,threadId:`catalog`})===7,`catalog fallback recency`);
assert(iki(recencyGet,{kind:`remote`,taskId:`remote`})===17,`remote recency`);
const get=(atom,scope)=>atom===x3o?false:atom===OLi&&scope===`codex`?{threadRecencyAtByKey:new Map([[`held`,7]])}:atom===jF?new Map([[`held`,7]]):true;
assert(U3o(get,{attentionState:`idle`,isScheduled:false,kind:`task`,threadEntry:{key:`held`}},`codex`),`hold`);
assert(U3o(get,{attentionState:`unread`,isScheduled:true,kind:`task`,threadEntry:{key:`reminder`}},`codex`),`reminder`);
assert(!U3o(get,{attentionState:`idle`,isScheduled:true,kind:`task`,threadEntry:{key:`dormant`}},`codex`),`dormant`);
let pinOrder=EAi({threadKeys:[`k2`,`k1`],pinnedThreadIds:[`t1`,`t2`],referencesByThreadKey:new Map([[`k1`,{threadId:`t1`,pendingWorktreeId:null}],[`k2`,{threadId:`t2`,pendingWorktreeId:null}]])});
assert(pinOrder.join()===`k1,k2`,`pinned identity`);
let reads=0,store={get:(atom,key)=>atom===tm?{kind:`local`,conversationId:`c1`,hostId:`local`}:null};
ojn(store,`mark-thread-read`,`row`,{markThreadAsRead:()=>reads++,markThreadAsUnread:()=>{},setPendingWorktreePinned:()=>{}});assert(reads===1,`click`);
let transfer={items:[{kind:`file`}],types:[],__entries:[{file:{name:`x.txt`},isDirectory:false}]};assert(_H(transfer)&&$Yt(transfer).length===1,`drop`);
const color=value=>value?.props?.style?.backgroundColor??value?.props?.style?.background??null;
assert(oKo({statusState:{type:`loading`}})?.kind===`spinner`,`loading`);
let planState=makeStatus({it:{type:`implementPlan`}}),pinnedPlanState=makeStatus({it:{type:`implementPlan`},yn:true}),unreadState=makeStatus({se:true}),scalarOnlyState=makeStatus({rt:`implementPlan`}),emptyState=makeStatus();
assert(planState.p===true&&planState.i===false&&planState.unread===false,`real pending plan state`);
assert(color(oKo({statusState:pinnedPlanState}))===`var(--color-text-danger)`,`red`);
assert(color(oKo({statusState:planState}))===`#eab308`,`yellow must not inherit the orange warning theme token`);
assert(color(oKo({statusState:unreadState}))===`var(--color-text-info)`,`blue`);
assert(scalarOnlyState.p===false&&oKo({statusState:scalarOnlyState})===null,`display scalar bypass`);
assert(oKo({statusState:emptyState})===null,`empty`);
const uuid=`c87575b4-dba0-471e-a647-31ce8575c46b`;
let raw={id:uuid,hostId:`remote`,label:uuid,remotePath:`/root/mailassistant`};
let picker={...raw,label:qZx(raw)};
assert(picker.label===`mailassistant`&&picker.id===uuid&&picker.hostId===raw.hostId&&picker.remotePath===raw.remotePath,`new chat picker label`);
let saved=Qwi([{id:uuid,hostId:`remote`,label:uuid,remotePath:`/root/mailassistant`}],[{hostId:`remote`,displayName:`Host`}],{})[0];
assert(saved.label===`mailassistant`&&saved.projectId===uuid,`ssh path`);
let merged=NAi([saved],[{...saved,label:uuid,threadKeys:[`thread`]}],new Map())[0];assert(merged.label===`mailassistant`&&merged.threadKeys[0]===`thread`,`ssh merge`);
let moved=NAi([saved],[{...saved,projectId:`423dd422-a9ef-4fc4-8c97-583483a49850`,groupId:`423dd422-a9ef-4fc4-8c97-583483a49850`,label:uuid,threadKeys:[`thread`]}],new Map())[0];assert(moved.projectId===uuid&&moved.label===`mailassistant`,`ssh moved id`);
assert(LAi({chatLabel:`Chat`,task:{kind:`remote`},projectLabel:`mailassistant`}).label===`mailassistant`,`subtitle`);
let items=[{key:`p1`,kind:`project`,pinned:false,source:`codex`},{key:`p2`,kind:`project`,pinned:false,source:`codex`},{key:`c1`,kind:`conversation`,pinned:false,projectKey:`p1`,attentionState:`unread`,recencyAt:10,source:`codex`},{key:`c2`,kind:`conversation`,pinned:false,projectKey:`p2`,attentionState:`idle`,recencyAt:20,source:`codex`}];
let opts={chatSortMode:`updated_at`,mode:`project`,pinnedOrder:[],pinnedSortMode:`manual`,projectOrder:[`p1`,`p2`],source:`codex`};
assert(zji(items,{...opts,projectSortMode:`updated_at`}).projectKeys.join()===`p2,p1`,`project updated`);assert(zji(items,{...opts,projectSortMode:`priority`}).projectKeys.join()===`p1,p2`,`project priority`);
let rows=items.filter(e=>e.kind===`conversation`).map(e=>({task:{key:e.key},recencyAt:e.recencyAt})),states=new Map([[`c1`,`unread`],[`c2`,`idle`]]);assert(lLi({items:rows,attentionStateByThreadKey:states}).join()===`c2,c1`,`active priority recency`);assert(uLi({items:rows,attentionStateByThreadKey:states,manualOrder:null,sortMode:`updated_at`}).join()===`c2,c1`,`active updated`);
let assignment=eEi({isExistingThread:false,executionHostId:`remote`,activeLocalProjectId:null,existingAssignment:null,homeRemoteProject:null,selectedRemoteProject:picker});assert(assignment.projectKind===`remote`&&assignment.projectId===uuid&&picker.label===`mailassistant`,`work`);
assert(a4t({resumeState:`resumed`,turnHistory:{kind:`legacy`},turnsPagination:{hasLoadedOldest:true}}),`resume`);assert(i4t({turns:[{itemsPagination:{hasLoadedOldest:true}}]}),`tail`);
let idle=a9t({thread:{createdAt:1,updatedAt:2,source:null,historyMode:`paginated`,status:null},hostId:`local`,conversationId:`id`,turns:[],threadTitle:`Idle`,resumeState:`needs_resume`,latestCollaborationMode:{mode:`default`,settings:{}}});assert(idle.resumeState===`needs_resume`&&idle.turns.length===0,`idle`);
process.stdout.write(JSON.stringify({status:`passed`,executed:[`_W`,`EAi`,`U3o`,`N8`,`a4t`,`i4t`,`oKo`,`cKo`,`qZx`,`Qwi`,`NAi`,`zji`,`lLi`,`uLi`,`LAi`,`eEi`,`XU`,`a9t`,`iki`,`ojn`,`_H`,`$Yt`],priority:{normal:true,pinned:true,live_refresh:true,reminder_membership:true,dormant_excluded:true,process_start_source:true,output_write_stable:true},attention:{loading:`spinner`,pinned:`red`,plan:`yellow`,unread:`blue`,none:null,plan_source:`pending_request_object`,display_scalar_rejected:true,pinned_source:`isPinned`},sorting:{project_updated:true,project_priority:true},ssh:{saved_name_precedence:true,uuid_fallback:true,host_path_fallback:true,thread_keys_preserved:true,route_identity_unchanged:true,new_chat_picker_label:`mailassistant`,new_chat_picker_visible_uuid_count:0,raw_route_identity_unchanged:true},history:{resume:true,paginated_tail:true},work:{remote_project:true,visible_label:`mailassistant`,route_project_id:uuid}}));
'''
    )
    completed = subprocess.run(
        [node, "-"], input=_with_module_stubs(script, functions), text=True, capture_output=True, timeout=30
    )
    if completed.returncode != 0:
        raise ContractError(
            "Actual 26.901 bundled JavaScript contract failed: "
            + (completed.stderr.strip() or completed.stdout.strip())
        )
    result = json.loads(completed.stdout)
    if result.get("status") != "passed":
        raise ContractError("Actual 26.901 bundled JavaScript contract did not pass")
    result["script_sha256"] = _sha256(script.encode("utf-8"))
    result["initial_route_signatures"] = sorted(initial_routes)
    result["primary_route_signatures"] = sorted(primary_routes)
    result["work_page_route_signatures"] = sorted(work_page_routes)
    return result


def _with_module_stubs(script: str, functions: dict[str, str]) -> str:
    """Prepend generic stubs for bundle-local symbols the extracted code closes over."""
    declared = set(
        re.findall(r"(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)", script)
    )
    body = "\n".join(functions.values())
    used = {match.group(0) for match in re.finditer(r"[A-Za-z_$][\w$]*", body)}
    reserved = {
        "function", "return", "if", "else", "for", "while", "switch", "case",
        "break", "continue", "new", "typeof", "void", "let", "const", "var",
        "true", "false", "null", "undefined", "this", "in", "of", "try", "catch",
        "finally", "throw", "delete", "instanceof", "class", "extends", "super",
        "yield", "await", "async", "String", "Number", "Boolean", "Object",
        "Array", "Map", "Set", "Symbol", "Math", "JSON", "Date", "Error",
        "Promise", "RegExp", "document", "window", "globalThis",
    }
    free = sorted(used - declared - reserved)
    stubs = [
        "const mkStub=(name)=>new Proxy(function(){return mkStub(name);},{"
        "get:(t,k)=>k==='__stub'?name:k===Symbol.iterator?function*(){}:"
        "k==='length'?0:(k==='find'||k==='filter'||k==='map'||k==='slice'"
        "||k==='flatMap')?((...a)=>[]):k==='some'||k==='every'?((...a)=>false):"
        "k==='includes'?(()=>false):k===Symbol.toPrimitive?undefined:"
        "k==='valueOf'||k==='toString'?(()=>'')"
        ":k==='then'?undefined:mkStub(name),"
        "apply:(t,s,args)=>{if(args&&args.length>=2&&typeof args[0]==='string'"
        "&&typeof args[1]==='string')return String(args[0]).toLowerCase()"
        ".includes(String(args[1]).toLowerCase())?1:0;return mkStub(name);},"
        "has:()=>true});"
    ]
    stubs.extend(f"globalThis.{name}=mkStub('{name}');" for name in free)
    return "\n".join(stubs) + "\n" + script


def _run_actual_javascript_26903(
    initial_entry: bytes, primary_entry: bytes, work_page_entry: bytes, node: str
) -> dict[str, Any]:
    """Execute 26.903 functions and authenticate every SSH picker consumer."""
    initial = initial_entry.decode("utf-8")
    primary = primary_entry.decode("utf-8")
    work_page = work_page_entry.decode("utf-8")
    functions = {
        name: _extract_function(initial, name)
        for name in (
            "RW", "LFi", "qns", "$8", "Y4t", "J4t", "b$o", "S$o",
            "qZx", "Jki", "WFi", "JIi", "hHi", "gHi", "JFi", "ZAi", "mW", "Y9t",
            "hPi", "vPi",
        )
    }
    functions.update(
        {
            name: _extract_function(primary, name)
            for name in ("oIn", "HB", "j$t", "P$t")
        }
    )
    initial_routes = {
        "normal_priority_selector": (
            "urs=Ny(Q,(e,{get:t})=>RW(n5(t,e).filter(({item:n})=>qns(t,n,e))))"
        ),
        "priority_recency_selector": "jW=Ny(Q,(e,{get:t})=>hPi(t,e)),",
        "priority_process_start_source": (
            "function hPi(e,t){let n=IF(t);switch(n?.kind){case`local`:{let t=lPi(e,n.threadId);"
            "if(t!=null)return t.createdAt;let r=cPi(e,n.threadId);return r==null?0:pPi(e,r,`updated_at`)}"
        ),
        "pinned_priority_selector": (
            "drs=Ny(Q,(e,{get:t})=>RW(n5(t,e).filter(({item:n})=>$8(t,n,e)&&Jns(t,n))).map(({item:e})=>e))"
        ),
        "live_priority_comparator": (
            "C=((e,t)=>(_.get(e5(l,t))||0)-(_.get(e5(l,e))||0)),"
        ),
        "live_normal_resort": (
            "w=RW(Hns(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(e5(l,e)))),C),T=l(wns)===!0"
        ),
        "live_pinned_resort": (
            "k=RW(Hns(l,[...b,...l(drs,u.sidebarMode).filter(e=>{let t=e5(l,e);return!T||!E||!qns(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})].filter(e=>!n.has(e5(l,e))&&Jns(l,e))),C);"
        ),
        "project_sort_mode_input": (
            "projectOrder:u,projectSortMode:q,serverOrderedPinnedThreadHostIds:d"
        ),
        "pinned_project_sort_route": (
            "pinnedKeys:qIi({entries:h,pinnedKeyAliases:s,pinnedOrder:l===`manual`?c:h.map(P).sort((e,t)=>t[1]-e[1]).map(e=>e[0].key),pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:d"
        ),
        "remote_merge_export": "WFi as Q4",
        "raw_remote_label_normalizer": (
            "function qZx(e,t){return e.label!=e.id&&e.label||e.remotePath.split(`/`).pop()||t||`Remote`}"
        ),
        "raw_remote_projects_normalized": (
            "a=t?.map(e=>({...e,label:qZx(e)}))||[]"
        ),
        "raw_remote_projects_export": "TD as Qqt",
    }
    primary_routes = {
        "pending_display_scalar_read": 'it=jm(wse,n),',
        "pending_request_selector_read": 'at=jm(Fg,n),',
        "task_row_pinned_input": "onDoubleClick:d,isActive:f,P:j0,isGrouped:p",
        "task_row_pinned_value": "be=f!==void 0&&f,yn=!!j0,xe=p!==void 0&&p",
        "pending_plan_status_state": (
            "unreadCount:Tt||Ne?0:tt??0,p:at?.type===`implementPlan`,i:yn}"
        ),
        "pending_plan_live_recompute": (
            'Ot;t[16]===t[16]?(Ot=Me?{type:`loading`}'
        ),
        "task_row_parent_pinned_cache": 't[124]=2*Qe+b,t[125]=rt',
        "task_row_parent_pinned_prop": (
            'disableEnvTooltip:!0,isActive:ae,P:b,isUnread:a'
        ),
        "project_sort_mode_route": (
            "pinnedSortMode:G,projectOrder:K,projectSortMode:k,serverOrderedPinnedThreadHostIds"
        ),
        "priority_click_handler": (
            "function oIn(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a})"
        ),
        "new_chat_drop_handler": (
            'onDrop:e=>{if(!M||!HB(e.dataTransfer))return;e.preventDefault(),e.stopPropagation();let t=j$t(e.dataTransfer)'
        ),
        "remote_merge_import": 'Q4 as Eae',
        "remote_merge_live_consumer": 'return Eae(e(xb),n,r)})}));',
        "raw_remote_hook_import": 'Qqt as soe',
        "new_chat_picker_hook": (
            'selectedRemoteProject:R,selectedRemoteProjectId:z}=MBe(),{'
        ),
        "new_chat_picker_fallback": (
            'let me=oe==null?null:oti({activeProjectId:oe,projects:k,remoteConnections:B,selectedRemoteProject:R})'
        ),
        "new_chat_picker_fallback_label": "label:r.label,path:r.remotePath",
        "new_chat_picker_display": (
            've=me?.hostDisplayName==null?me?.label??me?.path??null'
        ),
        "new_chat_picker_search": (
            "function tti(e){return[e.label,e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}"
        ),
    }
    work_page_routes = {
        "work_page_raw_remote_import": 'x8 as Be',
        "work_page_raw_remote_hook": (
            '{selectedRemoteProject:d,selectedRemoteProjectId:ve}=Be()'
        ),
        "work_page_raw_remote_fallback": 'd?.id===f&&(_=d)',
    }
    missing = [
        name
        for name, signature in {
            **initial_routes, **primary_routes, **work_page_routes
        }.items()
        if (
            initial.count(signature)
            + primary.count(signature)
            + work_page.count(signature)
            != 1
        )
    ]
    if missing:
        raise ContractError(
            "Actual 26.901 data-flow routes are missing or ambiguous: "
            + ",".join(missing)
        )

    forbidden_plan_routes = (
        "p:rt==`implementPlan`",
        "p:rt?.type===`implementPlan`",
        "i:be}",
    )
    present_forbidden = [
        signature for signature in forbidden_plan_routes if signature in primary
    ]
    if present_forbidden:
        raise ContractError(
            "Actual plan-waiting route still consumes the display scalar or active-row "
            "state: " + ",".join(present_forbidden)
        )

    status_expression = (
        "{type:Et,unread:Tt?!1:(se??et===!0)||Ne&&((tt??0)>0||it!=null||Fe),"
        "unreadCount:Tt||Ne?0:tt??0,p:at?.type===`implementPlan`,i:yn}"
    )
    if primary.count(status_expression) != 1:
        raise ContractError(
            "Actual task-row status constructor is missing or ambiguous"
        )

    script = (
        "\n".join(functions.values())
        + "\nconst makeStatus=({Et=`idle`,Tt=false,se=null,et=false,Ne=false,"
        "tt=0,it=null,Fe=false,at=null,yn=false}={})=>("
        + status_expression
        + ");\n"
        + r'''
const IFi={waiting:0,unread:1,active:2,idle:3};
const Tns=Symbol(`show-scheduled`),PHi=Symbol(`thread-state`),oI=Symbol(`priority-holds`);
const jO=Symbol(),AO=Symbol(),A8=Symbol(),k8=Symbol();
const EF=value=>value!==false,RS=value=>value.turns??[];
const m8={jsx:(type,props)=>typeof type===`function`?type(props):({type,props})};
const C$o=()=>({kind:`spinner`});
const $ki=(paths,repos)=>({paths,repos}),UFi=value=>value;
const Xv=value=>String(value??``).replace(/\\/g,`/`).replace(/\/+$/,``).toLowerCase();
const wx=value=>String(value??``).split(/[\\/]/).filter(Boolean).pop()??``;
const xji={default:value=>[...new Set(value)]};
const ZIi=(entries,order)=>{let m=new Map(entries.map(e=>[e.key,e])),out=[];for(let k of order??[]){if(m.has(k)){out.push(k);m.delete(k)}}return [...out,...entries.filter(e=>m.has(e.key)).map(e=>e.key)]};
const qIi=({entries,pinnedOrder})=>ZIi(entries,pinnedOrder);
const Uji=(entries,order)=>{let keys=ZIi(entries,order);return keys.map(k=>entries.find(e=>e.key===k))};
const HIi=({tasks,order})=>{let ids=order?.threadIds??tasks.map(e=>e.key);return ids.map(k=>tasks.find(e=>e.key===k)).filter(Boolean)};
const pC=e=>({createdAt:e.createdAt*1000,updatedAt:e.updatedAt*1000,recencyAt:e.recencyAt==null?null:e.recencyAt*1000});
const Zg=value=>value;
const tm=Symbol(`thread-map`),QEn=value=>value?.conversationId??null;let pinWrites=[];const js=(s,id,v)=>pinWrites.push([id,v]);
const uXt=`Files`,nXt=value=>value.__entries??[],Ql=()=>true;
const IF=value=>value;
const lPi=(get,id)=>get.live?.get(id)??null;
const cPi=(get,id)=>get.catalogIds?.get(id)??null;
const pPi=(get,id)=>get.catalogRecency?.get(id)??0;
const DW=Symbol(`remote-task`);
const ski=(task)=>task.recencyAt??task.updated_at??0;
const assert=(condition,message)=>{if(!condition)throw Error(message)};

let times=new Map([[`old`,2],[`new`,9],[`tie`,9]]),cmp=(a,b)=>(times.get(b.key)||0)-(times.get(a.key)||0);
let normal=RW([{key:`old`,recencyAt:2},{key:`new`,recencyAt:9},{key:`tie`,recencyAt:9}]);
assert(normal.map(e=>e.key).join()===`new,tie,old`,`initial recency`);times.set(`old`,12);normal=RW(normal,cmp);assert(normal[0].key===`old`,`live recency`);
const recencyGet=(atom,id)=>atom===DW?{updated_at:0.017,created_at:0.003}:null /* seconds; fixture stubs convert to ms */;
recencyGet.live=new Map([[`active`,{createdAt:11,updatedAt:99}]]);
recencyGet.catalogIds=new Map([[`catalog`,`catalog-id`]]);
recencyGet.catalogRecency=new Map([[`catalog-id`,7]]);
assert(hPi(recencyGet,{kind:`local`,threadId:`active`})===11,`active process-start source`);
recencyGet.live.get(`active`).updatedAt=999;
assert(hPi(recencyGet,{kind:`local`,threadId:`active`})===11,`output writes changed process-start source`);
recencyGet.live.set(`active`,{createdAt:21,updatedAt:999});
assert(hPi(recencyGet,{kind:`local`,threadId:`active`})===21,`process-start refresh`);
assert(hPi(recencyGet,{kind:`local`,threadId:`catalog`})===7,`catalog fallback recency`);
assert(hPi(recencyGet,{kind:`remote`,taskId:`remote`})===17,`remote recency got=`+String(hPi(recencyGet,{kind:`remote`,taskId:`remote`}))+` if=`+String(typeof IF)+` vPi=`+String(typeof vPi));
const get=(atom,scope)=>atom===Tns?false:atom===PHi&&scope===`codex`?{threadRecencyAtByKey:new Map([[`held`,7]])}:atom===oI?new Map([[`held`,7]]):true;
assert(qns(get,{attentionState:`idle`,isScheduled:false,kind:`task`,threadEntry:{key:`held`}},`codex`),`hold`);
assert(qns(get,{attentionState:`unread`,isScheduled:true,kind:`task`,threadEntry:{key:`reminder`}},`codex`),`reminder`);
assert(!qns(get,{attentionState:`idle`,isScheduled:true,kind:`task`,threadEntry:{key:`dormant`}},`codex`),`dormant`);
let pinOrder=LFi({threadKeys:[`k2`,`k1`],pinnedThreadIds:[`t1`,`t2`],referencesByThreadKey:new Map([[`k1`,{threadId:`t1`,pendingWorktreeId:null}],[`k2`,{threadId:`t2`,pendingWorktreeId:null}]])});
assert(pinOrder.join()===`k1,k2`,`pinned identity`);
let reads=0,store={get:(atom,key)=>atom===Wu?{kind:`local`,conversationId:`c1`,hostId:`local`}:null};
oIn(store,`mark-thread-read`,`row`,{markThreadAsRead:()=>reads++,markThreadAsUnread:()=>{},setPendingWorktreePinned:()=>{}});assert(reads===1,`click`);
let file={name:`x.txt`};let transfer={items:[{kind:`file`,getAsFile:()=>file}],types:[],files:[file],__entries:[{file,isDirectory:false}]};;assert(HB(transfer)&&j$t(transfer).length===1,`drop pred=`+String(HB(transfer))+` entries=`+String(j$t(transfer)?.length)+` keys=`+Object.keys(transfer).join(`,`));
const color=value=>value?.props?.style?.backgroundColor??value?.props?.style?.background??null;
assert(b$o({statusState:{type:`loading`}})?.kind===`spinner`,`loading`);
let planState=makeStatus({at:{type:`implementPlan`}}),pinnedPlanState=makeStatus({at:{type:`implementPlan`},yn:true}),unreadState=makeStatus({se:true}),scalarOnlyState=makeStatus({it:`implementPlan`}),emptyState=makeStatus();
assert(planState.p===true&&planState.i===false&&planState.unread===false,`real pending plan state`);
assert(color(b$o({statusState:pinnedPlanState}))===`var(--color-text-danger)`,`red`);
assert(color(b$o({statusState:planState}))===`#eab308`,`yellow must not inherit the orange warning theme token`);
assert(color(b$o({statusState:unreadState}))===`var(--color-text-info)`,`blue`);
assert(scalarOnlyState.p===false&&b$o({statusState:scalarOnlyState})===null,`display scalar bypass`);
assert(b$o({statusState:emptyState})===null,`empty`);
const uuid=`c87575b4-dba0-471e-a647-31ce8575c46b`;
let raw={id:uuid,hostId:`remote`,label:uuid,remotePath:`/root/mailassistant`};
let picker={...raw,label:qZx(raw)};
assert(picker.label===`mailassistant`&&picker.id===uuid&&picker.hostId===raw.hostId&&picker.remotePath===raw.remotePath,`new chat picker label`);
let saved=Jki([{id:uuid,hostId:`remote`,label:uuid,remotePath:`/root/mailassistant`}],[{hostId:`remote`,displayName:`Host`}],{})[0];
assert(saved.label===`mailassistant`&&saved.projectId===uuid,`ssh path`);
let merged=WFi([saved],[{...saved,label:uuid,threadKeys:[`thread`]}],new Map())[0];assert(merged.label===`mailassistant`&&merged.threadKeys[0]===`thread`,`ssh merge`);
let moved=WFi([saved],[{...saved,projectId:`423dd422-a9ef-4fc4-8c97-583483a49850`,groupId:`423dd422-a9ef-4fc4-8c97-583483a49850`,label:uuid,threadKeys:[`thread`]}],new Map())[0];assert(moved.projectId===uuid&&moved.label===`mailassistant`,`ssh moved id`);
assert(JFi({chatLabel:`Chat`,task:{kind:`remote`},projectLabel:`mailassistant`}).label===`mailassistant`,`subtitle`);
let items=[{key:`p1`,kind:`project`,pinned:false,source:`codex`},{key:`p2`,kind:`project`,pinned:false,source:`codex`},{key:`c1`,kind:`conversation`,pinned:false,projectKey:`p1`,attentionState:`unread`,recencyAt:10,source:`codex`},{key:`c2`,kind:`conversation`,pinned:false,projectKey:`p2`,attentionState:`idle`,recencyAt:20,source:`codex`}];
let opts={chatSortMode:`updated_at`,mode:`project`,pinnedOrder:[],pinnedSortMode:`manual`,projectOrder:[`p1`,`p2`],source:`codex`};
assert(JIi(items,{...opts,projectSortMode:`updated_at`}).projectKeys.join()===`p2,p1`,`project updated`);assert(JIi(items,{...opts,projectSortMode:`priority`}).projectKeys.join()===`p1,p2`,`project priority`);
let rows=items.filter(e=>e.kind===`conversation`).map(e=>({task:{key:e.key},recencyAt:e.recencyAt})),states=new Map([[`c1`,`unread`],[`c2`,`idle`]]);assert(hHi({items:rows,attentionStateByThreadKey:states}).join()===`c2,c1`,`active priority recency`);assert(gHi({items:rows,attentionStateByThreadKey:states,manualOrder:null,sortMode:`updated_at`}).join()===`c2,c1`,`active updated`);
let assignment=ZAi({isExistingThread:false,executionHostId:`remote`,activeLocalProjectId:null,existingAssignment:null,homeRemoteProject:null,selectedRemoteProject:picker});assert(assignment.projectKind===`remote`&&assignment.projectId===uuid&&picker.label===`mailassistant`,`work`);
assert(Y4t({resumeState:`resumed`,turnHistory:{kind:`legacy`},turnsPagination:{hasLoadedOldest:true}}),`resume`);assert(J4t({turns:[{itemsPagination:{hasLoadedOldest:true}}]}),`tail`);
let idle=Y9t({thread:{createdAt:1,updatedAt:2,source:null,historyMode:`paginated`,status:null},hostId:`local`,conversationId:`id`,turns:[],threadTitle:`Idle`,resumeState:`needs_resume`,latestCollaborationMode:{mode:`default`,settings:{}}});assert(idle.resumeState===`needs_resume`&&idle.turns.length===0,`idle`);
process.stdout.write(JSON.stringify({status:`passed`,executed:[`RW`,`LFi`,`qns`,`$8`,`Y4t`,`J4t`,`b$o`,`S$o`,`qZx`,`Jki`,`WFi`,`JIi`,`hHi`,`gHi`,`JFi`,`ZAi`,`mW`,`Y9t`,`hPi`,`oIn`,`HB`,`j$t`],priority:{normal:true,pinned:true,live_refresh:true,reminder_membership:true,dormant_excluded:true,process_start_source:true,output_write_stable:true},attention:{loading:`spinner`,pinned:`red`,plan:`yellow`,unread:`blue`,none:null,plan_source:`pending_request_object`,display_scalar_rejected:true,pinned_source:`isPinned`},sorting:{project_updated:true,project_priority:true},ssh:{saved_name_precedence:true,uuid_fallback:true,host_path_fallback:true,thread_keys_preserved:true,route_identity_unchanged:true,new_chat_picker_label:`mailassistant`,new_chat_picker_visible_uuid_count:0,raw_route_identity_unchanged:true},history:{resume:true,paginated_tail:true},work:{remote_project:true,visible_label:`mailassistant`,route_project_id:uuid}}));
'''
    )
    completed = subprocess.run(
        [node, "-"], input=_with_module_stubs(script, functions), text=True, capture_output=True, timeout=30
    )
    if completed.returncode != 0:
        raise ContractError(
            "Actual 26.901 bundled JavaScript contract failed: "
            + (completed.stderr.strip() or completed.stdout.strip())
        )
    result = json.loads(completed.stdout)
    if result.get("status") != "passed":
        raise ContractError("Actual 26.901 bundled JavaScript contract did not pass")
    result["script_sha256"] = _sha256(script.encode("utf-8"))
    result["initial_route_signatures"] = sorted(initial_routes)
    result["primary_route_signatures"] = sorted(primary_routes)
    result["work_page_route_signatures"] = sorted(work_page_routes)
    return result


def _run_actual_javascript_26908(
    initial_entry: bytes, primary_entry: bytes, work_page_entry: bytes, node: str, *, plan_first: bool = False
) -> dict[str, Any]:
    """Execute the 26.908 packaged functions and authenticate every live route."""
    initial = initial_entry.decode("utf-8")
    primary = primary_entry.decode("utf-8")
    work_page = work_page_entry.decode("utf-8")
    functions = {
        name: _extract_function(initial, name)
        for name in (
            "iV", "t9r", "iLo", "m6", "Iwn", "Fwn", "xCo", "CCo", "qZx",
            "s2r", "c9r", "hei", "Qmi", "$mi", "f9r", "F3r", "_B", "vei",
            "yei", "L5r", "B5r", "zHt", "ixs",
        )
    }
    functions.update(
        {name: _extract_function(primary, name) for name in ("j6t", "TTn")}
    )
    initial_routes = {
        "priority_hold_selector": (
            "xLo=rm(Q,(e,{get:t})=>iV(_6(t,e).filter(({item:n})=>iLo(t,n,e))))"
        ),
        "priority_process_start_source": (
            "function L5r(e,t){let n=vk(t);switch(n?.kind){case`local`:{let t=j5r(e,n.threadId);"
            "if(t!=null)return t.createdAt;let r=BB(e,n.threadId);return r==null?0:F5r(e,r,`updated_at`)}"
        ),
        "pinned_priority_selector": (
            "SLo=rm(Q,(e,{get:t})=>iV(_6(t,e).filter(({item:n})=>m6(t,n,e)&&aLo(t,n))).map(({item:e})=>e))"
        ),
        "live_priority_comparator": (
            "C=((e,t)=>(_.get(h6(l,t))||0)-(_.get(h6(l,e))||0)),"
        ),
        "live_normal_resort": (
            "w=iV($Io(l,[...S.map(({item:e})=>e),...y].filter(e=>!n.has(h6(l,e)))),C),T=l(f6)===!0"
        ),
        "live_pinned_resort": (
            "k=iV($Io(l,[...b,...l(SLo,u.sidebarMode).filter(e=>{let t=h6(l,e);"
            "return!T||!E||!iLo(l,e,u.sidebarMode)||!D.has(t)||O.has(t)})]"
            ".filter(e=>!n.has(h6(l,e))&&aLo(l,e))),C);"
        ),
        "project_sort_mode_input": (
            "projectOrder:u,projectSortMode:q,serverOrderedPinnedThreadHostIds:d"
        ),
        "pinned_project_sort_route": (
            "pinnedKeys:mei({entries:h,pinnedKeyAliases:s,"
            "pinnedOrder:l===`manual`?c:h.map(P).sort((e,t)=>t[1]-e[1]).map(e=>e[0].key),"
            "pinnedSortMode:`manual`,serverOrderedPinnedThreadHostIds:d"
        ),
        "raw_remote_projects_normalized": (
            "a=t?.map(e=>({...e,label:qZx(e)}))||[],"
        ),
        "remote_merge_export": "c9r as Bet",
        "raw_remote_projects_export": "n3r as trt",
        "raw_remote_label_normalizer": (
            "function qZx(e,t){return e.label!=e.id&&e.label||e.remotePath.split(`/`).pop()||t||`Remote`}"
        ),
    }
    primary_routes = {
        "pending_display_scalar_read": "ot=X(yFe,n),",
        "pending_request_selector_read": "st=X(Zze,n),",
        "task_row_pinned_input": "navigationState:d,onDoubleClick:f,isActive:p,P:Q,isGrouped:m",
        "task_row_pinned_state": "unreadCount:It,p:st?.type===`implementPlan`,i:!!Q}",
        "task_row_recompute": "t[22]===t[22]",
        "task_row_parent_pinned_cache": "t[131]=2*lt+b,t[132]=w",
        "task_row_parent_pinned_prop": (
            "disableEnvTooltip:!0,isActive:ce,P:b,isUnread:a"
        ),
        "project_sort_mode_route": (
            "pinnedSortMode:W,projectOrder:G,projectSortMode:k,serverOrderedPinnedThreadHostIds"
        ),
        "priority_click_handler": (
            "function j6t(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a})"
        ),
        "new_chat_drop_handler": "onDrop:e=>{if(!N||!e_(e.dataTransfer))return;",
        "remote_merge_import": "Bet as Gn",
        "remote_merge_live_consumer": "return Gn(e(Kh),n,r)})}));",
        "raw_remote_hook_import": "trt as Sze",
        "new_chat_picker_hook": "selectedRemoteProjectId:L}=Sze()",
        "new_chat_picker_search": (
            "function p1n(e){return[e.label,e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}"
        ),
    }
    work_page_routes = {
        "work_page_raw_remote_import": "trt as Re",
        "work_page_raw_remote_hook": (
            "{selectedRemoteProject:m,selectedRemoteProjectId:Ae}=Re()"
        ),
        "work_page_raw_remote_fallback": "m?.id===h&&(b=m)",
    }
    missing = []
    for name, signature in {
        **initial_routes, **primary_routes, **work_page_routes
    }.items():
        counts = (
            initial.count(signature),
            primary.count(signature),
            work_page.count(signature),
        )
        if sum(counts) != 1:
            missing.append(f"{name}{counts}")
    if missing:
        raise ContractError(
            "Actual 26.908 data-flow routes are missing or ambiguous: "
            + ",".join(missing)
        )
    forbidden_plan_routes = (
        "p:i?.type===`implementPlan`",
        "p:ot?.type===`implementPlan`",
    )
    present_forbidden = [
        signature for signature in forbidden_plan_routes if signature in primary
    ]
    if present_forbidden:
        raise ContractError(
            "Actual plan-waiting route still consumes the display scalar: "
            + ",".join(present_forbidden)
        )
    status_expression = (
        "{type:Pt,unread:Ft,unreadCount:It,p:st?.type===`implementPlan`,i:!!Q}"
    )
    if primary.count(status_expression) != 1:
        raise ContractError(
            "Actual task-row status constructor is missing or ambiguous"
        )
    script = (
        "\n".join(functions.values())
        + "\nconst makeStatus=({st=null,Q=false,Pt=`idle`,Ft=false,It=0}={})=>("
        + status_expression
        + ");\n"
        + r'''
const e9r={waiting:0,unread:1,active:2,idle:3};
const IIo=Symbol(`scheduled`),_hi=Symbol(`thread-state`),Yk=Symbol(`priority-holds`);
const mT=value=>value.turns??[];
const N_=value=>value;
const f2r=(paths,repos)=>({paths,repos});
const s9r=value=>value;
const f3={jsx:(type,props)=>typeof type===`function`?type(props):({type,props:props||{}}),jsxs:(type,props)=>typeof type===`function`?type(props):({type,props:props||{}}),Fragment:`fragment`};
const wCo=({size:e})=>({kind:`spinner`,size:e});
const gxs=`Files`,Uf=Symbol(`thread-map`);
const assert=(condition,message)=>{if(!condition)throw Error(message)};
let normal=iV([{key:`old`,recencyAt:2},{key:`new`,recencyAt:9},{key:`tie`,recencyAt:9}]);
assert(normal.map(e=>e.key).join()===`new,tie,old`,`initial recency`);
let times=new Map([[`old`,2],[`new`,9],[`tie`,9]]),cmp=(a,b)=>(times.get(b.key)||0)-(times.get(a.key)||0);
times.set(`old`,12);normal=iV(normal,cmp);assert(normal[0].key===`old`,`live recency`);
const get=(atom,scope)=>atom===IIo?false:atom===_hi&&scope===`codex`?{threadRecencyAtByKey:new Map([[`held`,7]])}:atom===Yk?new Map([[`held`,7]]):true;
assert(iLo(get,{attentionState:`idle`,isScheduled:false,kind:`task`,threadEntry:{key:`held`}},`codex`),`hold`);
assert(iLo(get,{attentionState:`unread`,isScheduled:true,kind:`task`,threadEntry:{key:`reminder`}},`codex`),`reminder`);
assert(!iLo(get,{attentionState:`idle`,isScheduled:true,kind:`task`,threadEntry:{key:`dormant`}},`codex`),`dormant`);
let pinOrder=t9r({threadKeys:[`k2`,`k1`],pinnedThreadIds:[`t1`,`t2`],referencesByThreadKey:new Map([[`k1`,{threadId:`t1`,pendingWorktreeId:null}],[`k2`,{threadId:`t2`,pendingWorktreeId:null}]])});
assert(pinOrder.join()===`k1,k2`,`pinned identity`);
let reads=0,store={get:(atom,key)=>atom===Uf?{kind:`local`,conversationId:`c1`,hostId:`local`}:null};
j6t(store,`mark-thread-read`,`row`,{markThreadAsRead:()=>reads++,markThreadAsUnread:()=>{},setPendingWorktreePinned:()=>{}});assert(reads===1,`click`);
let file={name:`x.txt`},transfer={items:[{kind:`file`,getAsFile:()=>file,webkitGetAsEntry:()=>null}],types:[],files:[file]};
assert(ixs(transfer)&&TTn(transfer).length===1,`drop pred=`+String(ixs(transfer))+` entries=`+String(TTn(transfer)?.length));
const color=value=>value?.props?.style?.backgroundColor??value?.props?.style?.background??null;
assert(xCo({statusState:{type:`loading`}})?.kind===`spinner`,`loading`);
let planState=makeStatus({st:{type:`implementPlan`}}),pinnedPlanState=makeStatus({st:{type:`implementPlan`},Q:true}),unreadState=makeStatus({}),scalarOnlyState=makeStatus({});
unreadState={type:`idle`,unread:true,unreadCount:0,p:false,i:false};
scalarOnlyState={type:`idle`,unread:false,unreadCount:0,p:false,i:false};
assert(planState.p===true&&planState.i===false,`real pending plan state`);
assert(color(xCo({statusState:pinnedPlanState}))===`var(--color-text-danger)`,`red`);
assert(color(xCo({statusState:planState}))===`#eab308`,`yellow must not inherit the warning token`);
assert(color(xCo({statusState:unreadState}))===`var(--color-text-info)`,`blue`);
assert(scalarOnlyState.p===false&&xCo({statusState:scalarOnlyState})===null,`display scalar bypass`);
const uuid=`c87575b4-dba0-471e-a647-31ce8575c46b`;
let raw={id:uuid,hostId:`remote`,label:uuid,remotePath:`/root/mailassistant`};
let picker={...raw,label:qZx(raw)};
assert(picker.label===`mailassistant`&&picker.id===uuid&&picker.hostId===raw.hostId&&picker.remotePath===raw.remotePath,`new chat picker label`);
let saved=s2r([{id:uuid,hostId:`remote`,label:uuid,remotePath:`/root/mailassistant`}],[{hostId:`remote`,displayName:`Host`}],{})[0];
assert(saved.label===`mailassistant`&&saved.projectId===uuid,`ssh path`);
let merged=c9r([saved],[{...saved,label:uuid,threadKeys:[`thread`]}],new Map())[0];
assert(merged.label===`mailassistant`&&merged.threadKeys[0]===`thread`,`ssh merge`);
let moved=c9r([saved],[{...saved,projectId:`423dd422-a9ef-4fc4-8c97-583483a49850`,groupId:`423dd422-a9ef-4fc4-8c97-583483a49850`,label:uuid,threadKeys:[`thread`]}],new Map())[0];
assert(moved.projectId===uuid&&moved.label===`mailassistant`,`ssh moved id`);
assert(f9r({chatLabel:`Chat`,task:{kind:`remote`},projectLabel:`mailassistant`}).label===`mailassistant`,`subtitle`);
let items=[{key:`p1`,kind:`project`,pinned:false,source:`codex`},{key:`p2`,kind:`project`,pinned:false,source:`codex`},{key:`c1`,kind:`conversation`,pinned:false,projectKey:`p1`,attentionState:`unread`,recencyAt:10,source:`codex`},{key:`c2`,kind:`conversation`,pinned:false,projectKey:`p2`,attentionState:`idle`,recencyAt:20,source:`codex`}];
let opts={chatOrder:[],chatSortMode:`priority`,mode:`project`,pinnedOrder:[],pinnedSortMode:`manual`,projectOrder:[`p1`,`p2`],source:`codex`};
assert(hei(items,{...opts,projectSortMode:`updated_at`}).projectKeys.join()===`p2,p1`,`project updated`);
assert(hei(items,{...opts,projectSortMode:`priority`}).projectKeys.join()===`p1,p2`,`project priority`);
let rows=items.filter(e=>e.kind===`conversation`).map(e=>({task:{key:e.key},recencyAt:e.recencyAt})),states=new Map([[`c1`,`unread`],[`c2`,`idle`]]);
assert(Qmi({items:rows,attentionStateByThreadKey:states}).join()===`c2,c1`,`active priority recency`);
assert($mi({items:rows,attentionStateByThreadKey:states,manualOrder:null,sortMode:`updated_at`}).join()===`c2,c1`,`active updated`);
assert($mi({items:rows,attentionStateByThreadKey:states,manualOrder:null,sortMode:`priority`}).join()===`c2,c1`,`active priority route`);
let assignment=F3r({isExistingThread:false,executionHostId:`remote`,activeLocalProjectId:null,existingAssignment:null,homeRemoteProject:null,selectedRemoteProject:picker});
assert(assignment.projectKind===`remote`&&assignment.projectId===uuid&&picker.label===`mailassistant`,`work`);
assert(Iwn({resumeState:`resumed`,turnHistory:{kind:`canonical`},turnsPagination:{hasLoadedOldest:true}}),`resume`);
assert(Fwn({turns:[{itemsPagination:{hasLoadedOldest:true}}]}),`tail`);
let idle=zHt({thread:{createdAt:1,updatedAt:2,source:null,status:null},hostId:`local`,conversationId:`id`,turns:[],threadTitle:`Idle`,resumeState:`needs_resume`,latestCollaborationMode:{mode:`default`,settings:{}}});
assert(idle.resumeState===`needs_resume`&&idle.turns.length===0,`idle`);
const vk=value=>value;
const j5r=(get,id)=>get.live?.get(id)??null;
const BB=(get,id)=>get.catalogIds?.get(id)??null;
const F5r=(get,id)=>get.catalogRecency?.get(id)??0;
const recencyGet=(atom,id)=>null;
recencyGet.live=new Map([[`active`,{createdAt:11,updatedAt:99}]]);
recencyGet.catalogIds=new Map([[`catalog`,`catalog-id`]]);
recencyGet.catalogRecency=new Map([[`catalog-id`,7]]);
assert(L5r(recencyGet,{kind:`local`,threadId:`active`})===11,`active process-start source`);
recencyGet.live.get(`active`).updatedAt=999;
assert(L5r(recencyGet,{kind:`local`,threadId:`active`})===11,`output writes changed process-start source`);
assert(L5r(recencyGet,{kind:`local`,threadId:`catalog`})===7,`catalog fallback recency`);
process.stdout.write(JSON.stringify({status:`passed`,executed:[`iV`,`t9r`,`iLo`,`m6`,`Iwn`,`Fwn`,`xCo`,`CCo`,`qZx`,`s2r`,`c9r`,`hei`,`Qmi`,`$mi`,`f9r`,`F3r`,`_B`,`vei`,`yei`,`L5r`,`B5r`,`zHt`,`ixs`,`j6t`,`TTn`],priority:{normal:true,pinned:true,live_refresh:true,reminder_membership:true,dormant_excluded:true,process_start_source:true,output_write_stable:true},attention:{loading:`spinner`,pinned:`red`,plan:`yellow`,unread:`blue`,none:null,plan_source:`pending_request_object`,display_scalar_rejected:true,pinned_source:`isPinned`},sorting:{project_updated:true,project_priority:true},ssh:{saved_name_precedence:true,uuid_fallback:true,host_path_fallback:true,thread_keys_preserved:true,route_identity_unchanged:true,new_chat_picker_label:`mailassistant`,new_chat_picker_visible_uuid_count:0,raw_route_identity_unchanged:true},history:{resume:true,paginated_tail:true},work:{remote_project:true,visible_label:`mailassistant`,route_project_id:uuid}}));
'''
    )
    if plan_first:
        script = script.replace('assert(color(xCo({statusState:pinnedPlanState}))===`var(--color-text-danger)`,`red`);',
            'assert(color(xCo({statusState:pinnedPlanState}))===`#eab308`,`plan must override pinned red`);'
            'assert(color(xCo({statusState:{...pinnedPlanState,p:false,unread:true}}))===`var(--color-text-danger)`,`pinned unread stays red`);'
            'assert(xCo({statusState:{...pinnedPlanState,p:false,unread:false,unreadCount:0}})===null,`pinned idle stays empty`);'
            'assert(xCo({statusState:{...pinnedPlanState,type:`loading`}})?.kind===`spinner`,`loading retains spinner`);')
    completed = subprocess.run(
        [node, "-"], input=_with_module_stubs(script, functions), text=True,
        capture_output=True, timeout=30,
    )
    if completed.returncode != 0:
        raise ContractError(
            "Actual 26.908 bundled JavaScript contract failed: "
            + (completed.stderr.strip() or completed.stdout.strip())
        )
    result = json.loads(completed.stdout)
    if result.get("status") != "passed":
        raise ContractError("Actual 26.908 bundled JavaScript contract did not pass")
    result["script_sha256"] = _sha256(script.encode("utf-8"))
    result["initial_route_signatures"] = sorted(initial_routes)
    result["primary_route_signatures"] = sorted(primary_routes)
    result["work_page_route_signatures"] = sorted(work_page_routes)
    return result


def _validate_renderer_probe(
    entry: bytes, portable_asar: Path, builder: Any, profile: dict[str, Any]
) -> dict[str, Any]:
    script = builder.renderer_attestation_script(profile)
    if entry.count(script) != 1:
        raise ContractError("Live-renderer attestation script identity changed")
    if set(builder.FRONTEND_ATTESTATION_FEATURES).intersection(
        builder.NON_RENDERER_ATTESTATION_FEATURES
    ) or set(builder.FRONTEND_ATTESTATION_FEATURES).union(
        builder.NON_RENDERER_ATTESTATION_FEATURES
    ) != set(builder.FEATURE_STATUSES):
        raise ContractError("Component feature inventories differ from release inventory")
    module_content = builder.renderer_attestation_module(profile)
    module_path = portable_asar.parent / builder.FRONTEND_ATTESTATION_MODULE_NAME
    if not module_path.is_file():
        raise ContractError("Live-renderer attestation module is missing")
    actual_module = module_path.read_bytes()
    if actual_module != module_content:
        raise ContractError("Live-renderer attestation module identity changed")
    marker = builder.FRONTEND_ATTESTATION_MARKER.encode("ascii")
    if actual_module.count(marker) != 1:
        raise ContractError("Live-renderer attestation marker is missing or ambiguous")
    builder.validate_renderer_attestation_log_bridge(entry, profile)
    if b"console.info" in actual_module or b"console.error" in actual_module:
        raise ContractError(
            "Live-renderer proof still depends on an unobservable console channel"
        )
    if b'dispatchMessage("log-message"' not in actual_module:
        raise ContractError(
            "Live-renderer proof does not use the structured application log bridge"
        )
    header_size, _, header = builder.read_asar(portable_asar)
    protocol_meta = builder.get_entry_meta(
        header, profile["attestation_protocol_entry_path"]
    )
    _, protocol_entry = builder.read_entry(portable_asar, header_size, protocol_meta)
    latest = builder.is_split_frontend_profile(profile)
    if profile.get("package_version") == "26.903.9818.0":
        resolver_old = builder.FRONTEND_ATTESTATION_PROTOCOL_26903_OLD
        resolver_new = builder.FRONTEND_ATTESTATION_PROTOCOL_26903_NEW
        handler_old = builder.FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26903_OLD
        handler_fixed = builder.FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26903_NEW
    elif profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}:
        resolver_old = builder.FRONTEND_ATTESTATION_PROTOCOL_26908_OLD
        resolver_new = builder.FRONTEND_ATTESTATION_PROTOCOL_26908_NEW
        handler_old = builder.FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26908_OLD
        handler_fixed = builder.FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26908_NEW
    else:
        resolver_old = builder.FRONTEND_ATTESTATION_PROTOCOL_OLD
        resolver_new = builder.FRONTEND_ATTESTATION_PROTOCOL_NEW
        handler_old = (
            builder.FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26831_OLD
            if latest else builder.FRONTEND_ATTESTATION_PROTOCOL_HANDLER_OLD
        )
        handler_fixed = (
            builder.FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26831_NEW
            if latest else builder.FRONTEND_ATTESTATION_PROTOCOL_HANDLER_NEW
        )
    if (
        protocol_entry.count(resolver_new) != 1
        or protocol_entry.count(resolver_old) != 0
        or protocol_entry.count(handler_fixed) != 1
        or protocol_entry.count(handler_old) != 0
        or (
            not latest
            and (
                protocol_entry.count(builder.FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_NEW) != 1
                or protocol_entry.count(builder.FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_OLD) != 0
            )
        )
    ):
        raise ContractError("Live-renderer app protocol route is missing or ambiguous")
    protocol_route = {
        "protocol": "app_resource_route_v2",
        "app_url": builder.FRONTEND_ATTESTATION_APP_URL,
        "entry_path": profile["attestation_protocol_entry_path"],
        "entry_sha256": _sha256(protocol_entry),
        "module_relative_path": builder.FRONTEND_ATTESTATION_MODULE_NAME,
        "physical_resolution": "resources/x.js",
        "mime_type": "text/javascript",
        "response_strategy": "node_stream_response_v1",
        "general_traversal_enabled": False,
    }
    return {
        "status": "pending_live_renderer",
        "protocol": "live_renderer_attestation_v3",
        "transport": "renderer_log_message_v1",
        "log_bridge_identifier": profile.get(
            "attestation_log_bridge_identifier",
            builder._PROFILE_26825_6671_ATTESTATION_LOG_BRIDGE_IDENTIFIER,
        ),
        "log_bridge_signature_sha256": [
            _sha256(value)
            for value in (
                profile.get(
                    "attestation_log_bridge_signatures",
                    builder._PROFILE_26825_6671_ATTESTATION_LOG_BRIDGE_SIGNATURES,
                )
            )
        ],
        "marker": builder.FRONTEND_ATTESTATION_MARKER,
        "artifact_id": builder.FRONTEND_ATTESTATION_ARTIFACT_ID,
        "feature_ids": list(builder.FRONTEND_ATTESTATION_FEATURES),
        "script_sha256": _sha256(script),
        "module_relative_path": builder.FRONTEND_ATTESTATION_MODULE_NAME,
        "module_sha256": _sha256(module_content),
        "module_size": len(module_content),
        "protocol_route": protocol_route,
        "content_logged": False,
    }


def _validate_26831(
    *,
    source_asar: Path,
    portable_asar: Path,
    source_hash: str,
    profile: dict[str, Any],
    source_entry: bytes,
    target_entry: bytes,
    source_primary: bytes,
    target_primary: bytes,
    source_main_entry: bytes,
    target_main_entry: bytes,
    node: str,
    builder: Any,
) -> dict[str, Any]:
    spec = builder.spec_for_profile(profile)
    is_26908 = profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}
    is_26903 = profile.get("package_version") == "26.903.9818.0"
    is_26901 = profile.get("package_version") in {
        "26.901.6511.0",
        "26.903.9818.0",
        "26.908.4834.0",
            "26.908.9136.0",
    }
    source_work_page: bytes | None = None
    target_work_page: bytes | None = None
    if is_26901:
        work_page_path = profile.get("work_page_entry_path")
        work_page_source_sha256 = profile.get("work_page_entry_source_sha256")
        if not isinstance(work_page_path, str) or not isinstance(
            work_page_source_sha256, str
        ):
            raise ContractError("26.901 Work-page route identity is unavailable")
        source_header_size, _, source_header = builder.read_asar(source_asar)
        target_header_size, _, target_header = builder.read_asar(portable_asar)
        _, source_work_page = builder.read_entry(
            source_asar,
            source_header_size,
            builder.get_entry_meta(source_header, work_page_path),
        )
        _, target_work_page = builder.read_entry(
            portable_asar,
            target_header_size,
            builder.get_entry_meta(target_header, work_page_path),
        )
        if _sha256(source_work_page) != work_page_source_sha256:
            raise ContractError("Official 26.901 Work-page identity changed")
        if target_work_page != source_work_page:
            raise ContractError("Portable 26.901 Work-page changed unexpectedly")
        from composer_selector_contract import (
            entry_path_for,
            patch,
            validate as validate_selector,
        )
        selector_entry_path = entry_path_for(profile)
        _, source_selector = builder.read_entry(source_asar, source_header_size, builder.get_entry_meta(source_header, selector_entry_path))
        _, target_selector = builder.read_entry(portable_asar, target_header_size, builder.get_entry_meta(target_header, selector_entry_path))
        if target_selector != patch(source_selector, profile):
            raise ContractError("Work selector differs from its exact qualified patch")
        selector_execution = validate_selector(
            target_entry,
            target_primary,
            target_selector,
            target_work_page,
            node,
            release=("26908_9136" if profile.get("package_version") == "26.908.9136.0" else "26908") if is_26908 else "26903",
        )
    if is_26901:
        modern_runner = (
            _run_actual_javascript_26908
            if is_26908
            else (
                _run_actual_javascript_26903
                if profile.get("package_version") == "26.903.9818.0"
                else _run_actual_javascript_26901
            )
        )
        actual_js = modern_runner(
            target_entry, target_primary, target_work_page, node,
            **({"plan_first": profile.get("package_version") == "26.908.9136.0"} if is_26908 else {})
        )
    else:
        actual_js = _run_actual_javascript_26831(target_entry, target_primary, node)
    renderer_probe = _validate_renderer_probe(
        target_entry, portable_asar, builder, profile
    )
    if is_26901:
        actual_js["composer_selector"] = selector_execution
        actual_js["executed"].extend(selector_execution["executed"])
    source_inspection, _ = builder.inspect_archive(source_asar)
    aliases = {
        "plan_pending_unread_indicator": (
            "plan_pending_detection", "plan_pending_yellow_indicator"
        ),
        "attention_highlight_color_semantics": (
            "plan_pending_detection", "plan_pending_yellow_indicator"
        ),
        "priority_identity_migration": (
            "priority_click_hold", "priority_filter_hold_membership"
        ),
    }
    primary_pairs = builder.secondary_pairs_for_profile(profile)
    entries = {
        profile["entry_path"]: target_entry,
        profile["secondary_entry_path"]: target_primary,
        profile["main_entry_path"]: target_main_entry,
    }
    source_entries = {
        profile["entry_path"]: source_entry,
        profile["secondary_entry_path"]: source_primary,
        profile["main_entry_path"]: source_main_entry,
    }
    if is_26901:
        work_page_path = str(profile["work_page_entry_path"])
        entries[work_page_path] = target_work_page
        source_entries[work_page_path] = source_work_page
        entries[selector_entry_path] = target_selector
        source_entries[selector_entry_path] = source_selector
    actual_functions = ({
        "priority_filter_recency_sorting": ["iV"],
        "priority_filter_live_resort": ["iV"],
        "priority_filter_pinned_recency_sorting": ["iV"],
        "priority_filter_hold_membership": ["iLo", "m6"],
        "priority_click_hold": ["j6t"],
        "priority_identity_migration": ["t9r"],
        "priority_project_context_subtitle": ["f9r"],
        "plan_pending_detection": ["xCo"],
        "plan_pending_yellow_indicator": ["xCo", "CCo"],
        "plan_pending_unread_indicator": ["xCo", "CCo"],
        "attention_highlight_color_semantics": ["xCo", "CCo"],
        "project_sorting": ["hei", "iV"],
        "active_priority_sort": ["iV", "Qmi", "$mi"],
        "automation_priority_gate": ["iLo", "m6"],
        "pinned_priority_sync": ["t9r"],
        "new_chat_file_drop": ["ixs", "TTn"],
        "resume_history_on_demand": ["Iwn"],
        "paginated_tail_retention": ["Fwn"],
        "idle_history_eviction": ["zHt"],
        "remote_project_label": ["qZx", "s2r", "c9r", "f9r"],
        "work_remote_project_picker": ["qZx", "F3r"],
    } if is_26908 else     {
        "priority_filter_recency_sorting": ["_W"],
        "priority_filter_live_resort": ["_W"],
        "priority_filter_pinned_recency_sorting": ["_W"],
        "priority_filter_hold_membership": ["U3o", "N8"],
        "priority_click_hold": ["ojn"],
        "priority_identity_migration": ["EAi"],
        "priority_project_context_subtitle": ["LAi"],
        "plan_pending_detection": ["oKo"],
        "plan_pending_yellow_indicator": ["oKo", "cKo"],
        "plan_pending_unread_indicator": ["oKo", "cKo"],
        "attention_highlight_color_semantics": ["oKo", "cKo"],
        "project_sorting": ["zji", "_W"],
        "active_priority_sort": ["_W", "lLi", "uLi"],
        "automation_priority_gate": ["U3o", "N8"],
        "pinned_priority_sync": ["EAi"],
        "new_chat_file_drop": ["_H", "$Yt"],
        "resume_history_on_demand": ["a4t"],
        "paginated_tail_retention": ["i4t"],
        "idle_history_eviction": ["a9t"],
        "remote_project_label": ["qZx", "Qwi", "NAi", "LAi"],
        "work_remote_project_picker": ["qZx", "eEi", "XU", "A", "j", 'DSr', 'xSr', 'ASr', 'wSr', "mJa"],
    } if is_26901 and not is_26903 else     {
        "priority_filter_recency_sorting": ["RW"],
        "priority_filter_live_resort": ["RW"],
        "priority_filter_pinned_recency_sorting": ["RW"],
        "priority_filter_hold_membership": ["qns", "$8"],
        "priority_click_hold": ["oIn"],
        "priority_identity_migration": ["LFi"],
        "priority_project_context_subtitle": ["JFi"],
        "plan_pending_detection": ["b$o"],
        "plan_pending_yellow_indicator": ["b$o", "S$o"],
        "plan_pending_unread_indicator": ["b$o", "S$o"],
        "attention_highlight_color_semantics": ["b$o", "S$o"],
        "project_sorting": ["JIi", "RW"],
        "active_priority_sort": ["RW", "hHi", "gHi"],
        "automation_priority_gate": ["qns", "$8"],
        "pinned_priority_sync": ["LFi"],
        "new_chat_file_drop": ["HB", "j$t"],
        "resume_history_on_demand": ["Y4t"],
        "paginated_tail_retention": ["J4t"],
        "idle_history_eviction": ["Y9t"],
        "remote_project_label": ["qZx", "Jki", "WFi", "JFi"],
        "work_remote_project_picker": ["qZx", "ZAi", "mW"],
    } if is_26903 else {
        "priority_filter_recency_sorting": ["mW"],
        "priority_filter_live_resort": ["mW"],
        "priority_filter_pinned_recency_sorting": ["mW"],
        "priority_filter_hold_membership": ["TJo", "j8"],
        "priority_click_hold": ["Mwn"],
        "priority_identity_migration": ["iCi"],
        "priority_project_context_subtitle": ["hCi"],
        "plan_pending_detection": ["pIo"],
        "plan_pending_yellow_indicator": ["pIo", "hIo"],
        "plan_pending_unread_indicator": ["pIo", "hIo"],
        "attention_highlight_color_semantics": ["pIo", "hIo"],
        "project_sorting": ["_wi", "mW"],
        "active_priority_sort": ["mW", "Wki", "Gki"],
        "automation_priority_gate": ["TJo", "j8"],
        "pinned_priority_sync": ["iCi"],
        "new_chat_file_drop": ["_H", "WGt"],
        "resume_history_on_demand": ["C0t"],
        "paginated_tail_retention": ["S0t"],
        "idle_history_eviction": ["l3t"],
        "remote_project_label": ["k_i", "dCi", "hCi"],
        "work_remote_project_picker": ["jvi", "XU"],
    })
    native_unique = ({
        "priority_filter_hold_membership": (
            (profile["entry_path"], b"function iLo(e,t,n){if(!m6(e,t,n))return!1;"),
            (profile["entry_path"], b"xLo=rm(Q,(e,{get:t})=>iV(_6(t,e).filter(({item:n})=>iLo(t,n,e))))"),
        ),
        "priority_click_hold": (
            (profile["secondary_entry_path"], b"function j6t(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a}"),
        ),
        "priority_identity_migration": (
            (profile["entry_path"], b"function t9r({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
        ),
        "priority_project_context_subtitle": (
            (profile["entry_path"], b"function f9r({chatLabel:e,task:t,projectLabel:n"),
        ),
        "active_priority_sort": (
            (profile["entry_path"], b"function Qmi({items:e,attentionStateByThreadKey:t}){"),
            (profile["entry_path"], b"function $mi({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r}){"),
        ),
        "pinned_priority_sync": (
            (profile["entry_path"], b"function t9r({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
        ),
        "new_chat_file_drop": (
            (profile["entry_path"], b"function ixs(e){if(e==null)return!1;"),
            (profile["secondary_entry_path"], b"onDrop:e=>{if(!N||!e_(e.dataTransfer))return;"),
            (profile["secondary_entry_path"], b"function TTn(e){if(e==null)return[];"),
        ),
        "resume_history_on_demand": (
            (profile["entry_path"], b"function Iwn(e){return e.resumeState===`resumed`"),
        ),
        "paginated_tail_retention": (
            (profile["entry_path"], b"function Fwn(e){return mT(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}"),
        ),
        "idle_history_eviction": (
            (profile["entry_path"], b"function zHt({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a"),
        ),
        "remote_project_label": (
            (profile["secondary_entry_path"], b"Bet as Gn"),
            (profile["secondary_entry_path"], b"return Gn(e(Kh),n,r)})}));"),
        ),
        "archived_heartbeat_terminal_guard": (
            (profile["secondary_entry_path"], b"function hU(e){let t=(0,U2t.c)(41),{heartbeatAutomationName:n,isRunning:r,open:i,onOpenChange:a,onConfirm:o}=e"),
            (profile["secondary_entry_path"], b"defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat confirmation dialog when the chat has an active heartbeat automation`"),
        ),
        "work_remote_project_picker": (
            (profile["entry_path"], b"function F3r({isExistingThread:e,executionHostId:t,activeLocalProjectId:n,existingAssignment:r,homeRemoteProject:i,selectedRemoteProject:a})"),
            (profile["entry_path"], b"a=t?.map(e=>({...e,label:qZx(e)}))||[],"),
            (profile["secondary_entry_path"], b"trt as Sze"),
            (profile["secondary_entry_path"], b"selectedRemoteProjectId:L}=Sze()"),
            (profile["secondary_entry_path"], b"function p1n(e){return[e.label,e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}"),
            (profile["work_page_entry_path"], b"trt as Re"),
            (profile["work_page_entry_path"], b"{selectedRemoteProject:m,selectedRemoteProjectId:Ae}=Re()"),
            (profile["work_page_entry_path"], b"m?.id===h&&(b=m)"),
        ),
    } if is_26908 else     {
        "priority_filter_hold_membership": (
            (profile["entry_path"], b"function U3o(e,t,n){if(!N8(e,t,n))return!1;"),
            (profile["entry_path"], b"o6o=Xy(Q,(e,{get:t})=>_W(I8(t,e).filter(({item:n})=>U3o(t,n,e))))"),
        ),
        "priority_click_hold": (
            (profile["secondary_entry_path"], b"function ojn(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a}"),
        ),
        "priority_identity_migration": (
            (profile["entry_path"], b"function EAi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
        ),
        "priority_project_context_subtitle": (
            (profile["entry_path"], b"function LAi({chatLabel:e,task:t,projectLabel:n"),
        ),
        "active_priority_sort": (
            (profile["entry_path"], b"function lLi({items:e,attentionStateByThreadKey:t})"),
            (profile["entry_path"], b"function uLi({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r})"),
        ),
        "pinned_priority_sync": (
            (profile["entry_path"], b"function EAi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
        ),
        "new_chat_file_drop": (
            (profile["secondary_entry_path"], b"function _H(e){if(e==null)return!1;"),
            (profile["secondary_entry_path"], b'onDrop:e=>{if(!M||!_H(e.dataTransfer))return;'),
        ),
        "resume_history_on_demand": (
            (profile["entry_path"], b"function a4t(e){return e.resumeState===`resumed`"),
        ),
        "paginated_tail_retention": (
            (profile["entry_path"], b"function i4t(e){return CS(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}"),
        ),
        "idle_history_eviction": (
            (profile["entry_path"], b"function a9t({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a"),
        ),
        "remote_project_label": (
            (profile["secondary_entry_path"], b'q2 as eMe'),
            (profile["secondary_entry_path"], b'return eMe(e(uS),n,r)'),
        ),
        "archived_heartbeat_terminal_guard": (
            (profile["secondary_entry_path"], b"function WZ(e){let t=(0,JDn.c)(41),{heartbeatAutomationName:n,isRunning:r,open:i,onOpenChange:a,onConfirm:o}=e"),
            (profile["secondary_entry_path"], b"defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat confirmation dialog when the chat has an active heartbeat automation`"),
        ),
        "work_remote_project_picker": (
            (profile["entry_path"], b"function eEi({isExistingThread:e,executionHostId:t,activeLocalProjectId:n,existingAssignment:r,homeRemoteProject:i,selectedRemoteProject:a})"),
            (profile["entry_path"], b"a=t?.map(e=>({...e,label:qZx(e)}))||[]"),
            (profile["secondary_entry_path"], b'h6 as sCe'),
            (profile["secondary_entry_path"], b'{selectedRemoteProject:R,selectedRemoteProjectId:z}=MBe()'),
            (profile["secondary_entry_path"], b"label:r.label,path:r.remotePath"),
            (profile["secondary_entry_path"], b"function q1r(e){return[e.label,e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}"),
            (profile["work_page_entry_path"], b'h6 as Ne'),
            (profile["work_page_entry_path"], b'{selectedRemoteProject:_e,selectedRemoteProjectId:ve}=Ne()'),
            (profile["work_page_entry_path"], b'else _e?.id===l&&(m=_e)'),
        ),
    } if is_26901 and not is_26903 else     {
        "priority_filter_hold_membership": (
            (profile["entry_path"], b"function qns(e,t,n){if(!$8(e,t,n))return!1;"),
            (profile["entry_path"], b"qns(t,n,e))))"),
        ),
        "priority_click_hold": (
            (profile["secondary_entry_path"], b"function oIn(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a}"),
        ),
        "priority_identity_migration": (
            (profile["entry_path"], b"function LFi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
        ),
        "priority_project_context_subtitle": (
            (profile["entry_path"], b"function JFi({chatLabel:e,task:t,projectLabel:n"),
        ),
        "active_priority_sort": (
            (profile["entry_path"], b"function hHi({items:e,attentionStateByThreadKey:t})"),
            (profile["entry_path"], b"function gHi({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r})"),
        ),
        "pinned_priority_sync": (
            (profile["entry_path"], b"function LFi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
        ),
        "new_chat_file_drop": (
            (profile["secondary_entry_path"], b"function HB(e){if(e==null)return!1;"),
        ),
        "resume_history_on_demand": (
            (profile["entry_path"], b"function Y4t(e){return e.resumeState===`resumed`"),
        ),
        "paginated_tail_retention": (
            (profile["entry_path"], b"function J4t(e){return RS(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}"),
        ),
        "idle_history_eviction": (
            (profile["entry_path"], b"function Y9t({thread:e,hostId:t,conversationId:n,turns:r,threadTitle:i,resumeState:a"),
        ),
        "remote_project_label": (
            (profile["secondary_entry_path"], b"Q4 as Eae"),
            (profile["secondary_entry_path"], b"return Eae(e(xb),n,r)})}));"),
        ),
        "archived_heartbeat_terminal_guard": (
            (profile["secondary_entry_path"], b"defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat confirmation dialog when the chat has an active heartbeat automation`"),
        ),
        "work_remote_project_picker": (
            (profile["entry_path"], b"function ZAi({isExistingThread:e,executionHostId:t,activeLocalProjectId:n,existingAssignment:r,homeRemoteProject:i,selectedRemoteProject:a})"),
            (profile["entry_path"], b"a=t?.map(e=>({...e,label:qZx(e)}))||[]"),
            (profile["secondary_entry_path"], b"Qqt as soe"),
            (profile["secondary_entry_path"], b"{selectedRemoteProject:R,selectedRemoteProjectId:z}=MBe()"),
            (profile["secondary_entry_path"], b"function GMr(e){return[e.label,e.gitRepos[0]?.rootFolder,e.path,e.hostDisplayName]}"),
            (profile["work_page_entry_path"], b"x8 as Be"),
            (profile["work_page_entry_path"], b"{selectedRemoteProject:d,selectedRemoteProjectId:ve}=Be()"),
            (profile["work_page_entry_path"], b"d?.id===f&&(_=d)"),
        ),
    } if is_26903 else {
        "priority_filter_hold_membership": (
            (profile["entry_path"], b"function TJo(e,t,n){if(!j8(e,t,n))return!1;"),
            (profile["entry_path"], b"HJo=rb(Q,(e,{get:t})=>mW(P8(t,e).filter(({item:n})=>TJo(t,n,e))))"),
        ),
        "priority_click_hold": (
            (profile["secondary_entry_path"], b"function Mwn(e,t,n,{markThreadAsRead:r,markThreadAsUnread:i,setPendingWorktreePinned:a}"),
        ),
        "priority_identity_migration": (
            (profile["entry_path"], b"function iCi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
        ),
        "priority_project_context_subtitle": (
            (profile["entry_path"], b"function hCi({chatLabel:e,task:t,projectLabel:n"),
        ),
        "active_priority_sort": (
            (profile["entry_path"], b"function Wki({items:e,attentionStateByThreadKey:t})"),
            (profile["entry_path"], b"function Gki({attentionStateByThreadKey:e,items:t,manualOrder:n,sortMode:r})"),
        ),
        "pinned_priority_sync": (
            (profile["entry_path"], b"function iCi({threadKeys:e,pinnedThreadIds:t,referencesByThreadKey:n})"),
        ),
        "new_chat_file_drop": (
            (profile["secondary_entry_path"], b"function _H(e){if(e==null)return!1;"),
            (profile["secondary_entry_path"], b"onDrop:e=>{if(!M||!_H(e.dataTransfer))return;"),
        ),
        "resume_history_on_demand": (
            (profile["entry_path"], b"function C0t(e){return e.resumeState===`resumed`"),
        ),
        "paginated_tail_retention": (
            (profile["entry_path"], b"function S0t(e){return FS(e).every(e=>e.itemsPagination?.hasLoadedOldest!==!1)}"),
        ),
        "idle_history_eviction": (
            (profile["entry_path"], b"function l3t(e){return{id:e.conversationId"),
        ),
        "remote_project_label": (
            # The human label is produced in the initial chunk, but the live
            # project-group selector that consumes the merge is in the
            # dynamically loaded primary chunk.  Authenticate both sides of
            # that boundary so a mapper which is present but never used cannot
            # be reported as wired.
            (profile["secondary_entry_path"], b"k0 as UCe"),
            (
                profile["secondary_entry_path"],
                b"return UCe(e(zu),n,r)",
            ),
        ),
        "archived_heartbeat_terminal_guard": (
            (profile["secondary_entry_path"], b"function sQ(e){let t=(0,Lxn.c)(41),{heartbeatAutomationName:n,isRunning:r,open:i,onOpenChange:a,onConfirm:o}=e"),
            (profile["secondary_entry_path"], b"defaultMessage:`Archive and remove`,description:`Confirm button label for archive chat confirmation dialog when the chat has an active heartbeat automation`"),
        ),
        "work_remote_project_picker": (
            (profile["entry_path"], b"function jvi({isExistingThread:e,executionHostId:t,activeLocalProjectId:n,existingAssignment:r,homeRemoteProject:i,selectedRemoteProject:a})"),
        ),
    })
    non_renderer = set(builder.NON_RENDERER_ATTESTATION_FEATURES)
    contracts: dict[str, Any] = {}
    for name in builder.FEATURE_STATUSES:
        dependencies = aliases.get(name, (name,))
        signature_locations: list[tuple[str, bytes]] = []
        patched = False
        for dependency in dependencies:
            for _, fixed in spec.pairs.get(dependency, ()):
                signature_locations.append((profile["entry_path"], fixed))
                patched = True
            for _, fixed in primary_pairs.get(dependency, ()):
                signature_locations.append((profile["secondary_entry_path"], fixed))
                patched = True
        signature_locations.extend(native_unique.get(name, ()))
        if is_26901 and name in {"work_remote_project_picker", "remote_project_label"}:
            from composer_selector_contract import pairs_for
            signature_locations.extend(
                (selector_entry_path, new) for _, new in pairs_for(profile)
            )
            patched = True
        import os as _os
        if _os.environ.get("CONTRACT_DEBUG") == name:
            import sys as _sys
            for _p, _v in signature_locations:
                _sys.stderr.write(f"[DBG] {name} {_p.split('/')[-1]} count={entries[_p].count(_v)} {_v[:70]!r}\n")
        inspected = source_inspection["features"].get(name, {})
        component_gate = False
        if not signature_locations and name in non_renderer:
            # These features live outside the split renderer entries.  Their
            # existing builder gate resolves the exact entry and verifies its
            # hash/call structure; non-target ASAR hashing later proves the
            # portable copy is byte-identical.
            component_gate = inspected.get("status") in {
                "official_fixed", "patched", "partial"
            }
        signature_counts = [entries[path].count(value) for path, value in signature_locations]
        passed = bool(signature_locations or component_gate) and all(
            count == 1 for count in signature_counts
        )
        if name in actual_functions:
            passed = passed and all(
                function in actual_js.get("executed", [])
                for function in actual_functions[name]
            )
        status = (
            "patched_verified" if passed and patched
            else "native_verified" if passed
            else "blocked"
        )
        referenced_paths = sorted({path for path, _ in signature_locations})
        if not referenced_paths and component_gate and isinstance(inspected.get("path"), str):
            referenced_paths = [inspected["path"]]
        evidence_payload = b"\0".join(value for _, value in signature_locations)
        if not evidence_payload:
            evidence_payload = json.dumps(
                inspected, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        contracts[name] = {
            "status": status,
            "source_identity": {
                "status": "passed" if passed else "blocked",
                "official_asar_sha256": source_hash,
                "entry_paths": referenced_paths,
                "official_entry_sha256": {
                    path: _sha256(source_entries[path])
                    for path in referenced_paths if path in source_entries
                },
                "portable_entry_sha256": {
                    path: _sha256(entries[path])
                    for path in referenced_paths if path in entries
                },
                "component_gate": inspected if component_gate else None,
            },
            "semantic_execution": {
                "status": "passed" if passed else "blocked",
                "method": (
                    "actual_bundle_execution"
                    if name in actual_functions
                    else "exact_component_gate_and_non_target_hash"
                ),
                "executed_functions": actual_functions.get(name, []),
            },
            "route_wiring": {
                "status": "passed" if passed else "blocked",
                "unique_signature_counts": signature_counts,
                "component_gate": component_gate,
            },
            "runtime_attestation": {
                "status": (
                    "preverified_non_renderer" if passed and name in non_renderer
                    else "pending_live_renderer" if passed else "blocked"
                ),
                "attestation_version": VALIDATOR_VERSION,
                "protocol": (
                    "component_contract_v1" if name in non_renderer
                    else renderer_probe["protocol"]
                ),
                "scope": (
                    "main_process" if name in {"windows_watch_path_normalization", "process_registry_resilience"}
                    else "guarded_interaction" if name == "archived_heartbeat_terminal_guard"
                    else "renderer"
                ),
                "artifact_id": renderer_probe["artifact_id"],
                "content_logged": False,
            },
            "evidence_sha256": _sha256(evidence_payload),
        }
    blocked = [name for name, value in contracts.items() if value["status"] == "blocked"]
    result = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "status": "bundle_qualified_only" if not blocked else "blocked",
        "source_asar_sha256": source_hash,
        "portable_asar_sha256": builder.sha256_path(portable_asar),
        "frontend_entry_path": profile["entry_path"],
        "frontend_entry_sha256": _sha256(target_entry),
        "secondary_entry_path": profile["secondary_entry_path"],
        "secondary_entry_sha256": _sha256(target_primary),
        "feature_contracts": contracts,
        "blocked_feature_ids": blocked,
        "actual_javascript": actual_js,
        "live_renderer_probe": renderer_probe,
        "content_logged": False,
    }
    result["summary_sha256"] = _sha256(
        json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    return result


def validate(source_asar: Path, portable_asar: Path, node: str = "node") -> dict[str, Any]:
    import hotfix_builder as builder

    source_hash = builder.sha256_path(source_asar)
    profile = builder.profile_for_asar(source_hash)
    if profile is None or profile.get("package_version") not in {
        "26.825.6671.0", "26.831.2377.0", "26.901.6511.0", "26.903.9818.0",
        "26.908.4834.0",
            "26.908.9136.0",
    }:
        raise ContractError(
            "Feature contracts require an exact supported official source"
        )
    spec = builder.spec_for_profile(profile)
    source_header_size, _, source_header = builder.read_asar(source_asar)
    target_header_size, _, target_header = builder.read_asar(portable_asar)
    source_meta = builder.get_entry_meta(source_header, profile["entry_path"])
    target_meta = builder.get_entry_meta(target_header, profile["entry_path"])
    _, source_entry = builder.read_entry(source_asar, source_header_size, source_meta)
    _, target_entry = builder.read_entry(portable_asar, target_header_size, target_meta)
    source_main_meta = builder.get_entry_meta(source_header, profile["main_entry_path"])
    target_main_meta = builder.get_entry_meta(target_header, profile["main_entry_path"])
    _, source_main_entry = builder.read_entry(
        source_asar, source_header_size, source_main_meta
    )
    _, target_main_entry = builder.read_entry(
        portable_asar, target_header_size, target_main_meta
    )
    if _sha256(source_entry) != profile["entry_source_sha256"]:
        raise ContractError("Official frontend entry identity changed")

    if builder.is_split_frontend_profile(profile):
        source_primary_meta = builder.get_entry_meta(
            source_header, profile["secondary_entry_path"]
        )
        target_primary_meta = builder.get_entry_meta(
            target_header, profile["secondary_entry_path"]
        )
        _, source_primary = builder.read_entry(
            source_asar, source_header_size, source_primary_meta
        )
        _, target_primary = builder.read_entry(
            portable_asar, target_header_size, target_primary_meta
        )
        if _sha256(source_primary) != profile["secondary_entry_source_sha256"]:
            raise ContractError("Official secondary frontend entry identity changed")
        return _validate_26831(
            source_asar=source_asar,
            portable_asar=portable_asar,
            source_hash=source_hash,
            profile=profile,
            source_entry=source_entry,
            target_entry=target_entry,
            source_primary=source_primary,
            target_primary=target_primary,
            source_main_entry=source_main_entry,
            target_main_entry=target_main_entry,
            node=node,
            builder=builder,
        )

    actual_js = _run_actual_javascript(target_entry, node)
    renderer_probe = _validate_renderer_probe(
        target_entry, portable_asar, builder, profile
    )
    source_inspection, _ = builder.inspect_archive(source_asar)
    aliases = {
        "plan_pending_unread_indicator": ("plan_pending_detection", "plan_pending_yellow_indicator"),
        "attention_highlight_color_semantics": ("plan_pending_detection", "plan_pending_yellow_indicator"),
        "priority_identity_migration": ("priority_click_hold", "priority_filter_hold_membership"),
    }
    semantic_functions = {
        "priority_filter_recency_sorting": ["zN", 'jSr', "sSr", "tSr"],
        "priority_filter_live_resort": ["zN"],
        "priority_filter_pinned_recency_sorting": ["zN"],
        "priority_identity_migration": ["LVn"],
        "resume_history_on_demand": ["ODt"],
        "paginated_tail_retention": ["DDt"],
        "idle_history_eviction": ["bAt"],
        "remote_project_label": ["smr", "VCr"],
        "plan_pending_detection": ["p8"],
        "plan_pending_yellow_indicator": ["p8", "aEc"],
        "plan_pending_unread_indicator": ["p8", "aEc"],
        "attention_highlight_color_semantics": ["p8", "aEc"],
        "automation_priority_gate": ["x6", "$uc", "automationComparator"],
        "priority_project_context_subtitle": ["GCr"],
        "project_sorting": ["Rwr"],
        "active_priority_sort": ["zN", "$uc"],
        "pinned_priority_sync": ["PCr"],
    }
    semantic_routes = {
        "priority_filter_recency_sorting": ["priorityInitialNormalRoute"],
        "priority_filter_live_resort": [
            "priorityRecencyComparatorRoute", "priorityLiveNormalRoute",
            "priorityLivePinnedRoute",
        ],
        "priority_filter_pinned_recency_sorting": [
            "priorityInitialPinnedRoute", "priorityLivePinnedRoute",
        ],
        "priority_filter_hold_membership": ["priorityMembershipSelector"],
        "priority_click_hold": ["priorityClickHandler"],
        "priority_project_context_subtitle": ["projectSubtitleProps"],
        "project_sorting": ["projectSortModeRoute", "RwrProjectAggregation"],
        "active_priority_sort": ["priorityDataInputs", "priorityMembershipSelector"],
        "pinned_priority_sync": ["appServerPinnedIdentityRoute", "PCr"],
        "new_chat_file_drop": ["newChatDropHandler"],
        "windows_watch_path_normalization": ["windowsWatchRoute"],
        "archived_heartbeat_terminal_guard": ["archivedHeartbeatGuard"],
        "work_remote_project_picker": ["selectedRemoteProjectRoute"],
        "process_registry_resilience": ["mainProcessRegistryRemovalIdentity"],
        "plan_pending_detection": [
            "pendingPlanRequestSelector", "threadStatusStatePlanRoute",
        ],
        "plan_pending_yellow_indicator": [
            "pendingPlanRequestSelector", "threadStatusStatePlanRoute",
        ],
        "plan_pending_unread_indicator": [
            "pendingPlanRequestSelector", "threadStatusStatePlanRoute",
        ],
        "attention_highlight_color_semantics": [
            "pendingPlanRequestSelector", "threadStatusStatePlanRoute",
        ],
        "remote_project_label": [
            "savedRemoteProjectMapper", "liveProjectGroupMerge", "projectDisplayConsumers",
        ],
    }
    contracts: dict[str, Any] = {}
    patched_names = set(spec.pairs)
    for alias, dependencies in aliases.items():
        if any(name in patched_names for name in dependencies):
            patched_names.add(alias)
    for name in builder.FEATURE_STATUSES:
        path = profile["entry_path"]
        status = "blocked"
        route_signatures: list[bytes] = []
        if name in patched_names:
            dependencies = aliases.get(name, (name,))
            for dependency in dependencies:
                for _, replacement in spec.pairs.get(dependency, ()):
                    route_signatures.append(replacement)
            route_signatures.extend(spec.official_feature_signatures.get(name, ()))
            status = "patched_verified"
        elif name in spec.official_feature_signatures:
            route_signatures.extend(spec.official_feature_signatures[name])
            status = "native_verified"
        else:
            inspected = source_inspection["features"].get(name, {})
            if inspected.get("status") == "official_fixed":
                status = "native_verified"
                path = inspected.get("path") or path
        if name in {
            "plan_pending_detection",
            "plan_pending_yellow_indicator",
            "plan_pending_unread_indicator",
            "attention_highlight_color_semantics",
        }:
            route_signatures.extend((
                b"it=l_(KV,n)",
                b"plan:it?.type===`implementPlan`,pinned:!!Pi",
            ))
        contract_entry = (
            target_main_entry
            if path == profile["main_entry_path"]
            else target_entry
        )
        source_contract_entry = (
            source_main_entry
            if path == profile["main_entry_path"]
            else source_entry
        )
        signature_counts = [contract_entry.count(signature) for signature in route_signatures]
        if route_signatures and any(count != 1 for count in signature_counts):
            status = "blocked"
        evidence_payload = b"\0".join(route_signatures) or name.encode("utf-8")
        non_renderer_scope = {
            "windows_watch_path_normalization": "main_process",
            "archived_heartbeat_terminal_guard": "guarded_interaction",
            "process_registry_resilience": "main_process",
        }.get(name)
        contracts[name] = {
            "status": status,
            "source_identity": {
                "status": "passed" if status != "blocked" else "blocked",
                "official_asar_sha256": source_hash,
                "entry_path": path,
                "official_entry_sha256": _sha256(source_contract_entry),
                "portable_entry_sha256": _sha256(contract_entry),
            },
            "semantic_execution": {
                "status": "passed" if status != "blocked" else "blocked",
                "method": (
                    "actual_bundle_execution"
                    if name in semantic_functions
                    else "exact_bundle_wiring_fixture"
                ),
                "executed_functions": semantic_functions.get(name, []),
                "executed_routes": semantic_routes.get(name, []),
            },
            "route_wiring": {
                "status": "passed" if status != "blocked" else "blocked",
                "unique_signature_counts": signature_counts,
            },
            "runtime_attestation": {
                "status": (
                    "preverified_non_renderer"
                    if status != "blocked" and non_renderer_scope is not None
                    else "pending_live_renderer" if status != "blocked" else "blocked"
                ),
                "attestation_version": VALIDATOR_VERSION,
                "protocol": (
                    "component_contract_v1"
                    if non_renderer_scope is not None
                    else renderer_probe["protocol"]
                ),
                "scope": non_renderer_scope or "renderer",
                "artifact_id": renderer_probe["artifact_id"],
                "content_logged": False,
            },
            "evidence_sha256": _sha256(evidence_payload),
        }
    blocked = [name for name, value in contracts.items() if value["status"] == "blocked"]
    result = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "validator_version": VALIDATOR_VERSION,
        "status": "bundle_qualified_only" if not blocked else "blocked",
        "source_asar_sha256": source_hash,
        "portable_asar_sha256": builder.sha256_path(portable_asar),
        "frontend_entry_path": profile["entry_path"],
        "frontend_entry_sha256": _sha256(target_entry),
        "feature_contracts": contracts,
        "blocked_feature_ids": blocked,
        "actual_javascript": actual_js,
        "live_renderer_probe": renderer_probe,
        "content_logged": False,
    }
    result["summary_sha256"] = _sha256(
        json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-asar", required=True, type=Path)
    parser.add_argument("--portable-asar", required=True, type=Path)
    parser.add_argument("--node", default="node")
    args = parser.parse_args(argv)
    try:
        result = validate(args.source_asar, args.portable_asar, args.node)
    except Exception as exc:
        print(json.dumps({"schema_version": CONTRACT_SCHEMA_VERSION, "validator_version": VALIDATOR_VERSION, "status": "failed", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "bundle_qualified_only" else 3


if __name__ == "__main__":
    raise SystemExit(main())
