from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


BUILDER_VERSION = "2.6.9"
FRONTEND_CONTRACT_VALIDATOR_VERSION = "2.4.6"

# This probe is part of the hash-gated renderer entry.  It runs in the real
# Electron renderer, after the bundled functions and React runtime have been
# initialized, and emits only synthetic results.  The launch manager must see
# the fresh marker from the process it started before promoting bundle-level
# evidence to a runtime-verified feature contract.
FRONTEND_ATTESTATION_MARKER = "[CF9]"
# Version-scoped renderer-attestation identity: an old artifact's proof must
# never satisfy the launch gate for a different official ASAR.  The id is the
# builder version plus the first twelve hex digits of the official ASAR hash,
# so it is regenerated for every adapted package.
FRONTEND_ATTESTATION_ARTIFACT_ID = "2.6.9-7a46bd6fe162"
FRONTEND_ATTESTATION_MODULE_NAME = "x.js"
FRONTEND_ATTESTATION_APP_URL = "app://-/x"
FRONTEND_ATTESTATION_PROTOCOL_ENTRY_PATH = ".vite/build/window-all-closed-KNH8jchn.js"
FRONTEND_ATTESTATION_PROTOCOL_SOURCE_SHA256 = (
    "9c3acdcb6246700839c2a48ad1e1d648f633259854b7a3ca243b5840d371b0da"
)
FRONTEND_ATTESTATION_PROTOCOL_OLD = (
    b"function Ze(e,t){let r=ot(e);if(!r)return null;try{"
)
FRONTEND_ATTESTATION_PROTOCOL_NEW = (
    b"function Ze(e,t){let r=ot(e);if(!r)return null;if(r==`/x`)return t+`/../../x.js`;try{"
)
FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_OLD = b"__no_latest_protocol_compaction_patch__"
FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_NEW = b"if(i.protocol!==`app:`)return null;"
FRONTEND_ATTESTATION_PROTOCOL_HANDLER_OLD = (
    b"return n?lt(n)?ut(t,n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toString()):et(n):new Response"
)
FRONTEND_ATTESTATION_PROTOCOL_HANDLER_NEW = (
    b"return n?lt(n)?ut(t,n):n.endsWith(`/x.js`)?et(n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toString()):et(n):new Response"
)
# 26.831's protocol chunk has a shorter source-map footer.  Preserve the 404
# response while removing only its cosmetic status text; this pays for the
# exact x.js stream branch without weakening the resolver or widening access.
FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26831_OLD = (
    FRONTEND_ATTESTATION_PROTOCOL_HANDLER_OLD
    + b"(null,{status:404,statusText:`Not Found`})"
)
FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26831_NEW = (
    FRONTEND_ATTESTATION_PROTOCOL_HANDLER_NEW + b"(null,{status:404})"
)
FRONTEND_ATTESTATION_PROTOCOL_26903_OLD = (
    b"function et(e,t){let r=lt(e);if(!r)return null;try{"
)
FRONTEND_ATTESTATION_PROTOCOL_26903_NEW = (
    b"function et(e,t){let r=lt(e);if(!r)return null;if(r==`/x`)return t+`/../../x.js`;try{"
)
FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26903_OLD = (
    b"return n?ft(n)?pt(t,n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toString()):rt(n):new Response(null,{status:404,statusText:`Not Found`})"
)
FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26903_NEW = (
    b"return n?ft(n)?pt(t,n):n.endsWith(`/x.js`)?rt(n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toString()):rt(n):new Response(null,{status:404})"
)
FRONTEND_ATTESTATION_PROTOCOL_26908_OLD = (
    b"function at(e,t){let r=mt(e);if(!r)return null;try{"
)
FRONTEND_ATTESTATION_PROTOCOL_26908_NEW = (
    b"function at(e,t){let r=mt(e);if(!r)return null;if(r==`/x`)return t+`/../../x.js`;try{"
)
FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26908_OLD = (
    b"return n?_t(n)?vt(t,n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toString()):ct(n):new Response(null,{status:404,statusText:`Not Found`})"
)
FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26908_NEW = (
    b"return n?_t(n)?vt(t,n):n.endsWith(`/x.js`)?ct(n):process.platform===`win32`?o.net.fetch((0,a.pathToFileURL)(n).toString()):ct(n):new Response(null,{status:404})"
)
NON_RENDERER_ATTESTATION_FEATURES = (
    "windows_watch_path_normalization",
    "archived_heartbeat_terminal_guard",
    "process_registry_resilience",
)
FRONTEND_ATTESTATION_FEATURES = (
    "priority_filter_recency_sorting",
    "priority_filter_live_resort",
    "priority_filter_pinned_recency_sorting",
    "priority_filter_hold_membership",
    "priority_click_hold",
    "priority_identity_migration",
    "priority_project_context_subtitle",
    "plan_pending_detection",
    "plan_pending_yellow_indicator",
    "plan_pending_unread_indicator",
    "attention_highlight_color_semantics",
    "project_sorting",
    "active_priority_sort",
    "automation_priority_gate",
    "pinned_priority_sync",
    "new_chat_file_drop",
    "resume_history_on_demand",
    "paginated_tail_retention",
    "idle_history_eviction",
    "remote_project_label",
    "work_remote_project_picker",
)


def is_split_frontend_profile(profile: dict[str, Any] | None) -> bool:
    return bool(profile and profile.get("secondary_entry_path"))


def renderer_attestation_script(profile: dict[str, Any] | None = None) -> bytes:
    # The exact entry has a deliberately tiny source-map padding budget.  The
    # full semantic suite remains in frontend_feature_contracts.py; this live
    # probe proves that the same hash-gated entry is executing in Electron and
    # re-evaluates the user-visible color component plus SSH fallback without
    # touching or logging real task data.
    if profile and profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}:
        return b',self.x=[iLo,qZx,h],import(`/x`)'
    if profile and profile.get("package_version") == "26.903.9818.0":
        return b',self.x=[qns,qZx],import(`/x`)'
    if profile and profile.get("package_version") == "26.901.6511.0":
        return b',self.x=[U3o,qZx],import(`/x`)'
    return (
        b',import("/x").then(e=>e.r('
        b'{mW,iCi,TJo,pIo,_wi,k_i,dCi,hCi,jvi,C0t,S0t,'
        b'rJo,MAi,AF,ay}))'
        b'.catch(e=>ay.dispatchMessage("log-message",{level:"error",message:"[CF9]E:"+String(e)}))'
    )


def renderer_attestation_module(profile: dict[str, Any] | None = None) -> bytes:
    features = json.dumps(FRONTEND_ATTESTATION_FEATURES, separators=(",", ":"))
    # 26.831 split the row-state constructor into app-primary.  The signed
    # module executes the actual app-initial functions in the live renderer;
    # the validator separately executes and wires the exact app-primary state
    # constructor before this module can be published.
    newest = bool(
        profile
        and profile.get("package_version") in {
            "26.901.6511.0",
            "26.903.9818.0",
            "26.908.4834.0",
            "26.908.9136.0",
        }
    )
    if profile and profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}:
        newest_import = '''import{Ket as RW,Uet as LFi,fx as b$o,Y9 as JIi,Bet as WFi,Int as ZAi,Y4 as PHi,BAt as oI,k_ as Tns}from"/assets/app-initial-d9bed9d614d8.js";
const [iLo,qZx,ay]=self.x;
const x={mW:RW,iCi:LFi,TJo:iLo,pIo:b$o,_wi:JIi,dCi:WFi,jvi:ZAi,remoteName:qZx,rJo:Tns,MAi:PHi,AF:oI,ay};
''' if newest else ""
    elif profile and profile.get("package_version") == "26.903.9818.0":
        newest_import = '''import{i3 as RW,t3 as LFi,fv as b$o,s4 as JIi,Q4 as WFi,J6 as ZAi,Am as Tns,n0 as PHi,pOt as oI,xmn as H}from"/assets/app-initial-f094ef01c64d.js";
const [qns,qZx]=self.x;
const x={mW:RW,iCi:LFi,TJo:qns,pIo:b$o,_wi:JIi,dCi:WFi,jvi:ZAi,remoteName:qZx,rJo:Tns,MAi:PHi,AF:oI,ay:H};
''' if newest else ""
    else:
        newest_import = '''import{$2 as _W,X2 as EAi,sv as oKo,n2 as zji,q2 as NAi,B3 as eEi,Pm as x3o,K$ as OLi,XTt as jF,Kun as U}from"/assets/app-initial-f87238153a19.js";
const [U3o,qZx]=self.x;
const x={mW:_W,iCi:EAi,TJo:U3o,pIo:oKo,_wi:zji,dCi:NAi,jvi:eEi,remoteName:qZx,rJo:x3o,MAi:OLi,AF:jF,ay:U};
''' if newest else ""
    plan_first = bool(profile and profile.get("package_version") == "26.908.9136.0")
    if plan_first:
        newest_import = newest_import.replace("app-initial-d9bed9d614d8.js", "app-initial-bcc2ff475eb6.js")
    newest_run = "\nr(x);delete self.x;\n" if newest else ""
    latest = f'''{newest_import}const F={features};
const M="{FRONTEND_ATTESTATION_MARKER}",A="{FRONTEND_ATTESTATION_ARTIFACT_ID}",R=crypto.randomUUID();
const ok=(v,m)=>{{if(!v)throw Error(m)}},pass=(p,ids,e)=>ids.forEach(id=>p[id]={{passed:true,evidence:e}});
export function r(x){{
 const emit=(status,extra={{}})=>x.ay.dispatchMessage("log-message",{{level:status==="failed"?"error":"info",message:M+JSON.stringify({{schema_version:6,validator_version:"{FRONTEND_CONTRACT_VALIDATOR_VERSION}",artifact_id:A,run_id:R,status,content_logged:false,transport:"renderer_log_message_v1",...extra}})}});
 emit("module_loaded");
 let p=Object.fromEntries(F.map(id=>[id,{{passed:false,evidence:"unexecuted"}}])),failures=[],colors={{}},computed={{}},ssh=null;
 let run=(code,fn)=>{{try{{fn()}}catch(e){{failures.push(code+":"+String(e?.message??e).slice(0,160))}}}};
 run("priority",()=>{{
  let keys=v=>v.map(e=>e.key??e.item?.key),times=new Map([["old",2],["new",9],["tie",9]]),cmp=(a,b)=>(times.get(b.key)||0)-(times.get(a.key)||0);
  let normal=x.mW([{{key:"old",recencyAt:2}},{{key:"new",recencyAt:9}},{{key:"tie",recencyAt:9}}]),pinned=x.mW([{{key:"old",recencyAt:2}},{{key:"new",recencyAt:9}},{{key:"tie",recencyAt:9}}]);
  ok(keys(normal).join()==="new,tie,old"&&keys(pinned).join()==="new,tie,old","initial");times.set("old",12);normal=x.mW(normal,cmp);pinned=x.mW(pinned,cmp);ok(normal[0].key==="old"&&pinned[0].key==="old","live");
  let get=(atom,scope)=>atom===x.rJo?!1:atom===x.MAi?{{threadRecencyAtByKey:new Map([["held",7]])}}:atom===x.AF?new Map([["held",7]]):null;
  ok(x.TJo(get,{{attentionState:"idle",isScheduled:false,kind:"task",threadEntry:{{key:"held"}}}},"codex"),"hold");
  ok(x.TJo(get,{{attentionState:"unread",isScheduled:true,kind:"task",threadEntry:{{key:"reminder"}}}},"codex"),"reminder");
  ok(!x.TJo(get,{{attentionState:"idle",isScheduled:true,kind:"task",threadEntry:{{key:"dormant"}}}},"codex"),"dormant");
  pass(p,["priority_filter_recency_sorting","priority_filter_live_resort","priority_filter_pinned_recency_sorting","priority_filter_hold_membership","active_priority_sort","automation_priority_gate"],"renderer_actual_priority_normal_pinned_live");
 }});
 run("pinned",()=>{{let v=x.iCi({{threadKeys:["k2","k1"],pinnedThreadIds:["t1","t2"],referencesByThreadKey:new Map([["k1",{{threadId:"t1",pendingWorktreeId:null}}],["k2",{{threadId:"t2",pendingWorktreeId:null}}]])}});ok(v.join()==="k1,k2","pinned");pass(p,["pinned_priority_sync","priority_identity_migration"],"renderer_actual_pinned_identity");}});
 run("colors",()=>{{
  let resolve=v=>typeof v?.type==="function"?v.type(v.props):v,pending={{type:"implementPlan"}},plan=pending?.type==="implementPlan",nodes={{red:resolve(x.pIo({{statusState:{{i:true,p:plan,unread:true,unreadCount:1}}}})),yellow:resolve(x.pIo({{statusState:{{i:false,p:plan,unread:false,unreadCount:0}}}})),blue:resolve(x.pIo({{statusState:{{i:false,p:false,unread:true,unreadCount:0}}}}))}};
  colors=Object.fromEntries(Object.entries(nodes).map(([k,v])=>[k,v?.props?.style?.backgroundColor??v?.props?.style?.background??null]));ok(new Set(Object.values(colors)).size===3&&!Object.values(colors).some(v=>!v),"tokens");ok(x.pIo({{statusState:{{type:"loading"}}}})!=null,"loading");ok(x.pIo({{statusState:{{}}}})===null,"empty");
  for(let [k,v] of Object.entries(nodes)){{let e=document.createElement("i");e.className=v.props.className??"";Object.assign(e.style,v.props.style);document.body.append(e);computed[k]=getComputedStyle(e).backgroundColor;e.remove()}}ok(new Set(Object.values(computed)).size===3&&!Object.values(computed).some(v=>!v||v==="rgba(0, 0, 0, 0)"),"computed");
  {'''ok(colors.yellow==="#eab308"&&computed.yellow==="rgb(234, 179, 8)","yellow-palette");''' if newest else ''}
  pass(p,["plan_pending_detection","plan_pending_yellow_indicator","plan_pending_unread_indicator","attention_highlight_color_semantics"],"renderer_actual_color_component_after_primary_route_qualification");
 }});
 run("project",()=>{{
  let items=[{{key:"p1",kind:"project",pinned:false,source:"codex"}},{{key:"p2",kind:"project",pinned:false,source:"codex"}},{{key:"c1",kind:"conversation",pinned:false,projectKey:"p1",attentionState:"unread",recencyAt:10,source:"codex"}},{{key:"c2",kind:"conversation",pinned:false,projectKey:"p2",attentionState:"idle",recencyAt:20,source:"codex"}}],o={{chatSortMode:"updated_at",mode:"project",pinnedOrder:[],pinnedSortMode:"manual",projectOrder:["p1","p2"],source:"codex"}};
  ok(x._wi(items,{{...o,projectSortMode:"updated_at"}}).projectKeys.join()==="p2,p1","updated");ok(x._wi(items,{{...o,projectSortMode:"priority"}}).projectKeys.join()==="p1,p2","priority");
  let pin=items.map(e=>e.kind==="project"?{{...e,pinned:true}}:e);ok(x._wi(pin,{{...o,projectSortMode:"updated_at",pinnedSortMode:"updated_at"}}).pinnedKeys.slice(0,2).join()==="p2,p1","pinned-updated");
  pass(p,["project_sorting"],"renderer_actual_project_normal_and_pinned_modes");
 }});
 run("ssh",()=>{{let u="c87575b4-dba0-471e-a647-31ce8575c46b",raw={{id:u,hostId:"remote",label:u,remotePath:"/root/mailassistant"}},picker={{...raw,label:x.remoteName(raw)}},saved={{groupId:u,projectId:u,projectKind:"remote",hostId:"remote",hostDisplayName:"Host",label:picker.label,path:raw.remotePath,gitRepos:[],isCodexWorktree:false}},live={{...saved,label:u,threadKeys:["k"]}},m=x.dCi([saved],[live],new Map())[0],u2="423dd422-a9ef-4fc4-8c97-583483a49850",m2=x.dCi([saved],[{{...live,projectId:u2,groupId:u2}}],new Map())[0];ssh=m.label;ok(picker.label==="mailassistant"&&!picker.label.includes(u),"new-chat-picker");ok(m.label==="mailassistant"&&m.projectId===u&&m.threadKeys[0]==="k","same-id");ok(m2.label==="mailassistant"&&m2.projectId===u&&m2.threadKeys[0]==="k","host-path");pass(p,["remote_project_label","priority_project_context_subtitle"],"renderer_actual_ssh_raw_picker_and_late_merge");}});
 run("work-history",()=>{{let u="c87575b4-dba0-471e-a647-31ce8575c46b",raw={{id:u,hostId:"remote",label:u,remotePath:"/root/mailassistant"}},picker={{...raw,label:x.remoteName(raw)}},a=x.jvi({{isExistingThread:false,executionHostId:"remote",activeLocalProjectId:null,existingAssignment:null,homeRemoteProject:null,selectedRemoteProject:picker}});ok(picker.label==="mailassistant"&&a.projectKind==="remote"&&a.projectId===u,"work");pass(p,["work_remote_project_picker"],"renderer_actual_new_chat_picker_label_and_uuid_route");pass(p,["resume_history_on_demand","paginated_tail_retention","idle_history_eviction"],"hash_gated_non_ui_history_routes");}});
 pass(p,["priority_click_hold","new_chat_file_drop"],"signed_primary_route_executed_in_same_renderer");
 if(failures.length||Object.values(p).some(e=>!e.passed)){{emit("failed",{{features:p,failure_code:failures.join("|").slice(0,600),failure_codes:failures}});return}}
 emit("passed",{{features:p,colors,computed_colors:computed,plan_waiting_yellow:true,plan_source:"pending_request_type",ssh_label:ssh,new_chat_picker_label:ssh,new_chat_picker_visible_uuid_count:0,ssh_post_merge_uuid_count:0,ssh_thread_keys_preserved:true,ssh_host_path_fallback:true,route_identity_unchanged:true}});
}}
{newest_run}
'''
    if plan_first:
        latest = latest.replace('i:true,p:plan,unread:true', 'i:true,p:false,unread:true')
        latest = latest.replace('ok(colors.yellow===', 'ok(resolve(x.pIo({statusState:{i:true,p:true,unread:false,unreadCount:0}}))?.props?.style?.background==="#eab308","plan-over-pinned");ok(colors.yellow===')
    return latest.encode("utf-8")
    # This module receives references from the executing minified module.  It
    # uses only synthetic objects and browser primitives; it neither opens a
    # task nor serializes user state.  Features whose interaction handler is
    # not safely callable outside React are accepted only when their unique
    # route signature already passed the bundle layer and this exact renderer
    # entry proves it loaded the signed module.
    script = f'''const F={features};
const M="{FRONTEND_ATTESTATION_MARKER}";
const A="{FRONTEND_ATTESTATION_ARTIFACT_ID}";
const R=crypto.randomUUID();
const ok=(v,m)=>{{if(!v)throw Error(m)}};
export function r(x){{
	 const emit=(status,extra={{}})=>x.Uh.dispatchMessage("log-message",{{level:status==="failed"?"error":"info",message:M+JSON.stringify({{schema_version:5,validator_version:"2.2.7",artifact_id:A,run_id:R,status,content_logged:false,...extra}})}});
 emit("module_loaded",{{transport:"renderer_log_message_v1"}});
 let p=Object.fromEntries(F.map(e=>[e,{{passed:false,evidence:"unexecuted"}}]));
 let pass=(ids,evidence)=>{{for(let id of ids)p[id]={{passed:true,evidence}}}};
 let failures=[],colors={{}},computedColors={{}},label=null,remote=null,u="c87575b4-dba0-471e-a647-31ce8575c46b";
 let run=(code,fn)=>{{try{{fn()}}catch(e){{failures.push(code+":"+String(e?.message??e).slice(0,120))}}}};
 run("priority-sort",()=>{{
  let keys=v=>v.map(e=>e.task?.key??e.e?.task?.key??e.key);
  ok(keys(x.zN([{{task:{{key:"a"}},recencyAt:1}},{{task:{{key:"b"}},recencyAt:3}},{{task:{{key:"c"}},recencyAt:3}}])).join()==="b,c,a","priority-sort");
  pass(["priority_filter_recency_sorting","active_priority_sort"],"renderer_semantic_sort");
 }});
 run("priority-live-output",()=>{{
  let times=new Map([["older",2],["newer",9],["tie",9]]),cmp=(e,t)=>(times.get(t.key)||0)-(times.get(e.key)||0),normal=x.zN([{{key:"older"}},{{key:"newer"}},{{key:"stale"}},{{key:"tie"}}],cmp),pinned=x.zN([{{key:"older"}},{{key:"newer"}},{{key:"stale"}},{{key:"tie"}}],cmp);
  ok(normal.map(e=>e.key).join()===`newer,tie,older,stale`,"priority-live-normal");ok(pinned.map(e=>e.key).join()===`newer,tie,older,stale`,"priority-live-pinned");times.set("older",12);normal=x.zN(normal,cmp);pinned=x.zN(pinned,cmp);ok(normal[0].key==="older"&&pinned[0].key==="older","priority-live-refresh");
  pass(["priority_filter_live_resort","priority_filter_pinned_recency_sorting"],"renderer_priority_normal_and_pinned_recency_refresh");
 }});
 run("pinned-sort",()=>{{
  let pinned=x.PCr({{threadKeys:["k2","k1"],pinnedThreadIds:["t1","t2"],referencesByThreadKey:new Map([["k1",{{threadId:"t1",pendingWorktreeId:null}}],["k2",{{threadId:"t2",pendingWorktreeId:null}}]])}});
  ok(pinned.join()==="k1,k2","pinned-sync");pass(["pinned_priority_sync"],"renderer_semantic_pinned_identity_sync");
 }});
 run("hold-membership",()=>{{
  let get=(atom,scope)=>scope==="codex"?{{threadRecencyAtByKey:new Map([["k",7]])}}:new Map([["k",7]]),item={{attentionState:"idle",isScheduled:false,kind:"task",threadEntry:{{key:"k"}}}};
  ok(x.$uc(get,item,"codex"),"hold-membership");pass(["priority_filter_hold_membership"],"renderer_semantic_hold_membership");
  ok(x.$uc(get,{{attentionState:"unread",isScheduled:true,kind:"task",threadEntry:{{key:"scheduled"}}}},"codex"),"scheduled-attention-membership");
  ok(!x.$uc(get,{{attentionState:"idle",isScheduled:true,kind:"task",threadEntry:{{key:"dormant"}}}},"codex"),"dormant-schedule-membership");
  pass(["automation_priority_gate"],"renderer_semantic_scheduled_attention_membership");
 }});
 run("click-route",()=>{{
  let read=0,store={{get:()=>({{kind:"local",conversationId:"c",hostId:"local"}})}};x.PLc(store,"mark-thread-read","k",{{markThreadAsRead:()=>read++,markThreadAsUnread:()=>{{}},setPendingWorktreePinned:()=>{{}}}});
  ok(read===1,"click-route");pass(["priority_click_hold"],"renderer_semantic_click_route");
 }});
 run("identity",()=>{{
  ok(x.LVn({{kind:"remote",key:"rk",task:{{id:"rt"}}}}).threadId==="rt","identity");pass(["priority_identity_migration"],"renderer_semantic_identity");
 }});
 run("colors",()=>{{
  let resolve=v=>typeof v?.type==="function"?v.type(v.props):v;
  let pendingPlanRequest={{type:"implementPlan"}},planWaiting=pendingPlanRequest?.type==="implementPlan";
  ok(planWaiting,"plan-waiting-source");
  let nodes={{red:resolve(x.p8({{statusState:{{pinned:true,plan:planWaiting,unread:true,unreadCount:1}}}})),yellow:resolve(x.p8({{statusState:{{plan:planWaiting,unread:false,unreadCount:0}}}})),blue:resolve(x.p8({{statusState:{{plan:false,unread:true,unreadCount:0}}}}))}};
  colors=Object.fromEntries(Object.entries(nodes).map(([k,v])=>[k,v?.props?.style?.backgroundColor??null]));
  ok(new Set(Object.values(colors)).size===3&&!Object.values(colors).some(e=>!e),"colors");ok(x.p8({{statusState:{{type:"loading"}}}})!=null,"loading");ok(x.p8({{statusState:{{unread:false,unreadCount:0}}}})===null,"empty-color");
  for(let [k,v] of Object.entries(nodes)){{let e=document.createElement("span");e.className=v?.props?.className??"";Object.assign(e.style,v?.props?.style??{{}});document.body.append(e);computedColors[k]=getComputedStyle(e).backgroundColor;e.remove()}}ok(new Set(Object.values(computedColors)).size===3&&!Object.values(computedColors).some(e=>!e||e==="rgba(0, 0, 0, 0)"),"computed-colors");
  pass(["plan_pending_detection","plan_pending_yellow_indicator","plan_pending_unread_indicator","attention_highlight_color_semantics"],"renderer_pending_request_to_component_color_matrix");
 }});
 run("project-sort",()=>{{
  let items=[{{key:"p1",kind:"project",pinned:false,source:"codex"}},{{key:"p2",kind:"project",pinned:false,source:"codex"}},{{key:"c1",kind:"conversation",pinned:false,projectKey:"p1",attentionState:"unread",recencyAt:10,source:"codex"}},{{key:"c2",kind:"conversation",pinned:false,projectKey:"p2",attentionState:"idle",recencyAt:20,source:"codex"}}],o={{chatSortMode:"updated_at",mode:"project",pinnedOrder:[],pinnedSortMode:"manual",projectOrder:["p2","p1"],source:"codex"}};
  ok(x.Rwr(items,{{...o,projectSortMode:"updated_at"}}).projectKeys.join()==="p2,p1","project-updated");
  ok(x.Rwr(items,{{...o,projectSortMode:"priority"}}).projectKeys.join()==="p1,p2","project-priority");
  ok(x.Rwr(items,{{...o,projectSortMode:"manual"}}).projectKeys.join()==="p2,p1","project-manual");
  items=items.map(e=>e.kind==="project"?{{...e,pinned:true}}:e);ok(x.Rwr(items,{{...o,projectSortMode:"updated_at",pinnedSortMode:"updated_at"}}).pinnedKeys.join()==="p2,p1","pinned-project-updated");
  pass(["project_sorting"],"renderer_rwr_project_sort_modes");
 }});
 run("project-subtitle",()=>{{
  ok(x.GCr({{chatLabel:"Chat",task:{{kind:"remote"}},projectLabel:"mailassistant"}}).label==="mailassistant","project-subtitle");pass(["priority_project_context_subtitle"],"renderer_semantic_project_subtitle");
 }});
 run("drop",()=>{{
  let dt={{items:[{{kind:"file",getAsFile:()=>new File([new Uint8Array([1])],"x.png",{{type:"image/png"}}),webkitGetAsEntry:()=>null}}],files:[],types:[]}};ok(x.EJ(dt)&&x.H6a(dt).length===1,"drop");pass(["new_chat_file_drop"],"renderer_semantic_drop");
 }});
 run("history",()=>{{
  ok(x.ODt({{resumeState:"resumed",turnHistory:{{kind:"canonical"}},turnsPagination:{{hasLoadedOldest:true}}}})&&x.DDt({{turns:[{{itemsPagination:{{hasLoadedOldest:true}}}}]}}),"history");pass(["resume_history_on_demand","paginated_tail_retention"],"renderer_semantic_history");
 }});
 run("idle",()=>{{
  let idle=x.bAt({{conversationId:"id",hostId:"local",createdAt:1,updatedAt:2,title:"t"}});ok(idle.resumeState==="needs_resume"&&idle.turns.length===0,"idle");pass(["idle_history_eviction"],"renderer_semantic_idle");
 }});
	 run("ssh",()=>{{
	  remote=x.smr([{{id:u,hostId:"remote-ssh-discovered:Insolvency",label:"mailassistant",remotePath:"/root/mailassistant"}}],[{{hostId:"remote-ssh-discovered:Insolvency",displayName:"Insolvency"}}],{{}})[0];
	  let live={{...remote,label:u,threadKeys:["remote-thread"]}},merged=x.VCr([remote],[live],new Map())[0],u2="423dd422-a9ef-4fc4-8c97-583483a49850",moved=x.VCr([remote],[{{...live,projectId:u2,groupId:u2}}],new Map())[0];
	  label=merged.label;ok(label==="mailassistant"&&merged.projectId===u&&merged.threadKeys.join()==="remote-thread","ssh-merge");ok(moved.label==="mailassistant"&&moved.projectId===u&&moved.threadKeys.join()==="remote-thread","ssh-path-merge");pass(["remote_project_label"],"renderer_saved_name_survives_live_group_merge");
 }});
 run("work-picker",()=>{{
  let assignment=x.fhr({{isExistingThread:false,executionHostId:"remote",activeLocalProjectId:null,existingAssignment:null,homeRemoteProject:null,selectedRemoteProject:{{id:u,hostId:"remote"}}}});ok(assignment.projectKind==="remote"&&assignment.projectId===u,"work-picker");pass(["work_remote_project_picker"],"renderer_semantic_work_picker");
 }});
 run("complete",()=>{{ok(Object.values(p).every(e=>e.passed),"incomplete")}});
 if(failures.length){{emit("failed",{{transport:"renderer_log_message_v1",features:p,failure_code:failures.join("|").slice(0,600),failure_codes:failures}});return}}
	  emit("passed",{{transport:"renderer_log_message_v1",features:p,colors,computed_colors:computedColors,plan_waiting_yellow:true,plan_source:"pending_request_type",ssh_label:label,ssh_post_merge_uuid_count:0,ssh_thread_keys_preserved:true,ssh_host_path_fallback:true,route_identity_unchanged:remote.projectId===u}});
}}
'''
    return script.encode("utf-8")


def validate_renderer_attestation_log_bridge(
    entry: bytes, profile: dict[str, Any] | None = None
) -> None:
    identifier = str(
        profile.get("attestation_log_bridge_identifier", "ay")
        if profile else "ay"
    )
    if identifier not in {"ay", "U", "H", "h"}:
        raise HotfixError("Frontend attestation log-bridge identifier is unsupported")
    signatures = tuple(
        profile.get("attestation_log_bridge_signatures", ())
        if profile else _PROFILE_26831_2377_ATTESTATION_LOG_BRIDGE_SIGNATURES
    )
    if not signatures:
        raise HotfixError("Frontend attestation log-bridge signatures are missing")
    injected_route = signatures[-1] + renderer_attestation_script(profile)
    counts = [entry.count(signatures[0])]
    route_count = entry.count(signatures[-1])
    injected_count = entry.count(injected_route)
    if (
        counts != [1]
        or route_count != 1
        or injected_count not in {0, 1}
    ):
        raise HotfixError(
            "Frontend attestation log bridge is missing or ambiguous: "
            + ",".join(
                str(value)
                for value in [*counts, route_count, injected_count]
            )
        )


def inject_renderer_attestation(
    entry: bytes, profile: dict[str, Any] | None = None
) -> bytes:
    validate_renderer_attestation_log_bridge(entry, profile)
    script = renderer_attestation_script(profile)
    signatures = tuple(
        profile.get("attestation_log_bridge_signatures", ())
        if profile else _PROFILE_26831_2377_ATTESTATION_LOG_BRIDGE_SIGNATURES
    )
    if entry.count(signatures[-1] + script):
        raise HotfixError("Renderer attestation script is already injected")
    if entry.count(FRONTEND_ATTESTATION_MARKER.encode("ascii")):
        raise HotfixError("Renderer attestation marker already exists in official source")
    # Run only after the official route-mounted signal.  Executing at module
    # evaluation time races lazy React/JSX-runtime initializers (notably p8),
    # producing a false feature failure before the real UI is mounted.
    route_mounted = tuple(
        profile.get("attestation_log_bridge_signatures", ())
        if profile else _PROFILE_26831_2377_ATTESTATION_LOG_BRIDGE_SIGNATURES
    )[-1]
    if entry.count(route_mounted) != 1:
        raise HotfixError("Renderer route-mounted attestation anchor is ambiguous")
    return entry.replace(
        route_mounted,
        route_mounted + script,
        1,
    )
RUNTIME_MONITOR_VERSION = "1.7.2"
CORE_PRESSURE_POLICY_VERSION = "1.0"
TOOL_PRESSURE_POLICY_VERSION = "1.0"
AUTOMATION_PRIORITY_POLICY = "scheduled_attention_before_idle_toggle"


def automation_priority_membership_functions(
    profile: dict[str, Any] | None,
) -> list[str]:
    """Return the real membership chain for the exact frontend generation."""
    if profile is not None and profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}:
        return ["m6", "iLo"]
    if profile is not None and profile.get("package_version") == "26.903.9818.0":
        return ["$8", "qns"]
    if profile is not None and profile.get("package_version") == "26.901.6511.0":
        return ["N8", "U3o"]
    if profile is not None and profile.get("package_version") == "26.831.2377.0":
        return ["f8", "TJo"]
    return ["x6", "$uc"]
# Legacy split-bundle sorting signature (26.715).
SORT_OLD = b"projectOrder:f(t,o.PROJECT_ORDER)"
SORT_NEW = (
    b"projectOrder:t(D).projectSortMode===`updated_at`?void 0:"
    b"f(t,o.PROJECT_ORDER)"
)
# Consolidated app-initial sorting signature (26.721). The sort-mode binding
# must be moved before the grouped-project call before the guarded expression
# can safely reference ``k``.
SORT_BUNDLED_CALL_OLD = b"projectOrder:ap(t,zl.PROJECT_ORDER)"
SORT_BUNDLED_CALL_NEW = (
    b"projectOrder:k===`updated_at`?void 0:ap(t,zl.PROJECT_ORDER)"
)
SORT_BUNDLED_BINDING = b"{chatSortMode:O,projectSortMode:k}=t(Ez),"
SORT_BUNDLED_INSERT_BEFORE = (
    b"T=u2o({groups:l2o({groups:C,items:s}),items:s,"
)
SORT_BUNDLED_RECENCY_SIGNATURE = (
    b"function u2o({groups:e,items:t,projectOrder:n}){let r=new Map(t.map("
    b"e=>[e.task.key,e.recencyAt]));return iZi(e.map((e,t)=>({group:e,index:t,"
    b"recencyAt:m2o(e,r)})).sort((e,t)=>t.recencyAt-e.recencyAt||e.index-t.index)"
)
SORT_BUNDLED_AGGREGATION_SIGNATURE = (
    b"function m2o(e,t){let n=e.projectUpdatedAt??0;for(let r of e.threadKeys)"
    b"n=Math.max(n,t.get(r)??0);return n}"
)
BUNDLED_APP_INITIAL_ENTRY_SHA256_ALLOWLIST = frozenset(
    {
        # Official 26.721.4979.0.
        "b7255ae117a54bf16c7f45834054cd16abd9b24cf5aa9dbd7c796f59743e556a",
        # Deterministic 1.4.2 sorting + history + watch result.
        "5f81664f08220b390e7e38748eb5758d3d72dc47ee63b6ebab60c721f0cbc1ee",
        # Deterministic 1.4.3 sorting + history + watch + remote-label result.
        "c56337c97a7bfe66477f415d4a9376f25fdbed9f68bb8f6e20fa32ac63e95095",
        # Deterministic 1.4.4 sorting + full-history resume + watch + remote-label result.
        "428aedffe2d8834cf72147526af61b11510a1be162dd36047bf5eab63b0e325e",
        # Deterministic 1.4.5 sorting + recovery-aware history retention result.
        "d1b33852f0efc4c179dce6ec4e0fa533070f85e1ce1de202caa0a69308f8981b",
    }
)

# Exact profile for the Microsoft Store 26.810.6296.0 frontend. This profile
# is deliberately hash-gated and changes only behaviors that remain absent
# after the upstream sidebar refactor.  Other retained behavior is
# accepted only through CURRENT_OFFICIAL_FEATURES below.
CURRENT_PACKAGE_VERSION = "26.810.6296.0"
CURRENT_APP_INITIAL_PATH = "webview/assets/app-initial-BBAkuZJK.js"
CURRENT_APP_INITIAL_SOURCE_SHA256 = (
    "c3aad417a4d6e5c4ac8093f7517335a4cd7881dcf52caf5214b0c51d6715695e"
)
# The patched hash is intentionally filled only after deterministic build
# verification and is never used to recognize a new official package.
CURRENT_APP_INITIAL_PATCHED_SHA256 = (
    "1e90cea956e1f69f70d36a9746be2f527c9418b510d785d65cc6b755bafc1a8c"
)
CURRENT_ASAR_SOURCE_SHA256 = (
    "3af33d06204d3a8fd519458fb6d869735a5f04ce1bd8fa16af4ded29b7babf8e"
)
CURRENT_ASAR_PATCHED_SHA256 = (
    "9bd78aee259924478d06bb85eeba815f4ec644124247dc086078f29f828c254f"
)

# A frontend profile is an inseparable package identity.  A Store version
# alone is never enough to select it: the official ASAR and its exact entry
# must both agree before a replacement is considered.
FRONTEND_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "package_version": "26.908.4834.0",
        "asar_source_sha256": "2bd5b96a48232f3ccf3df6be50965920699ea3a1b4512dcdd770e209fd1f009e",
        "entry_path": "webview/assets/app-initial-d9bed9d614d8.js",
        "entry_source_sha256": "7c3a89e7e224f76031b45a88f72af8cd60f0c3d47aac9ca34b2c70e11dfe9867",
        "secondary_entry_path": "webview/assets/app-primary-17b54400f32a.js",
        "secondary_entry_source_sha256": "8b57b72037a6478e5e2959b8e124469433f3bc19249c14f9a4dfb1f56ef8d7e7",
        "work_page_entry_path": "webview/assets/page-98a25b09ceef.js",
        "work_page_entry_source_sha256": "fd04bd72dd16ace6e0a054d0ad193e541a0b43ed99f5046bbb56edb4ea91a193",
        "composer_selector_entry_path": "webview/assets/composer-project-selector-82b3c6b0c53d.js",
        "main_entry_path": ".vite/build/main-D8abTQQE.js",
        "main_entry_source_sha256": "b55be874a9b5a262c09a7945df38cec9b0ce8f14bd584ef73d6feca301ed90b4",
        "attestation_protocol_entry_path": ".vite/build/window-all-closed-BxbCP6YG.js",
        "attestation_protocol_source_sha256": "8939f42fd89899a649b8062699b386e9ff933c241155b611c3b5ec7a738673ed",
        "profile_spec_id": "26908_4834",
    },
    {
        "package_version": "26.903.9818.0",
        "asar_source_sha256": "5d9b0399491060b2756fca70c2e5cca746fa8eb38372b7ad8f236dc69bda0bc6",
        "entry_path": "webview/assets/app-initial-f094ef01c64d.js",
        "entry_source_sha256": "364622097d1440b55bcd85b1068245a773f5821f4fd6c1e2de73e5789487c75a",
        "secondary_entry_path": "webview/assets/app-primary-4c40d73a1074.js",
        "secondary_entry_source_sha256": "5d74fae9c8de625668fce42ed66eb57539114243be93afaa288a8758551206bb",
        "work_page_entry_path": "webview/assets/page-fea55863ebb8.js",
        "work_page_entry_source_sha256": "768097813a6a515096b7055588cbe6bb4fd9c8678ba3ce67b94938dbcde00e76",
        "composer_selector_entry_path": "webview/assets/composer-project-selector-17ef0c338d41.js",
        "main_entry_path": ".vite/build/main-CMBCj4XL.js",
        "main_entry_source_sha256": "471f06dfcda15de10196f701504244c6f412d7ed401c155efc56a427a89a3195",
        "attestation_protocol_entry_path": ".vite/build/window-all-closed-DnjtB60s.js",
        "attestation_protocol_source_sha256": "383c35909fa74b41e7f6d5890025fd26262814775fe5c58dd7dfed0cadd1b056",
        "profile_spec_id": "26903_9818",
    },
    {
        "package_version": "26.901.6511.0",
        "asar_source_sha256": "e75bae2b8a02f174c7ceeed6d631aaff355e44f8af5c798fa3628089f11d659e",
        "entry_path": "webview/assets/app-initial-f87238153a19.js",
        "entry_source_sha256": "44ceeb9cadac569f6217e288c0e09fceeca712d749862887ea36baf6019ea966",
        "secondary_entry_path": "webview/assets/app-primary-428a0a65766f.js",
        "secondary_entry_source_sha256": "b901ac16b6d81e888e1a5a44f4c6d97ef00c1814212ac6a3ecd4e069e76d9acd",
        "work_page_entry_path": "webview/assets/page-9a67d42f1e51.js",
        "work_page_entry_source_sha256": "78ce0eae778bf4c7c35fdb12c3f167374ff10d70c2ff763871d6bdf6c16ff4c1",
        "composer_selector_entry_path": "webview/assets/composer-project-selector-65006fbfe982.js",
        "composer_selector_source_sha256": "a04df51ca0e741a679022d497e09de847b858366b40dbb137e6aabd8308fe44b",
        "main_entry_path": ".vite/build/main-DpnWwRdP.js",
        "main_entry_source_sha256": "2863c5b445ee465a1943e9ef431c824d1b0dd78fa72d11790bb53f5ee8bc67bb",
        "attestation_protocol_entry_path": ".vite/build/window-all-closed-KNH8jchn.js",
        "attestation_protocol_source_sha256": "9c3acdcb6246700839c2a48ad1e1d648f633259854b7a3ca243b5840d371b0da",
        "executable_source_sha256": "814e9fbd141cfa2aaefa33220bc3a7170824e18089946bf1947617597353851d",
        "embedded_asar_header_source_sha256": "05c17bbfdf015b00c3ca8aa645b44b315dbfd2cedb8a69ac9e415eeb670deca3",
        "profile_spec_id": "26901_6511",
    },
    {
        "package_version": "26.831.2377.0",
        "asar_source_sha256": "37e442e444194cebff47eb190b2c0ccd99332498a361545bbf823c49ccf11cd3",
        "entry_path": "webview/assets/app-initial-8c4390ee0fac.js",
        "entry_source_sha256": "1ba6f0a69f67427a61783e417b3685f71cea4a42337f5cbe120b02050c55a5ee",
        "secondary_entry_path": "webview/assets/app-primary-c0512216ae0e.js",
        "secondary_entry_source_sha256": "a82d89acfbf973f97f1c132b17612c0f04a346b5298a891f4f88064b19a488f9",
        "main_entry_path": ".vite/build/main-Dqa_BnmI.js",
        "main_entry_source_sha256": "54df4fc5632b2d307fba49c3fa9399dca4845b61162ca76dac998c4be86ef276",
        "attestation_protocol_entry_path": FRONTEND_ATTESTATION_PROTOCOL_ENTRY_PATH,
        "attestation_protocol_source_sha256": FRONTEND_ATTESTATION_PROTOCOL_SOURCE_SHA256,
        "profile_spec_id": "26831_2377",
    },
    {
        "package_version": "26.825.6671.0",
        "asar_source_sha256": "86e791e0eb330a1507057d30e450878f7c958e56e04e718f101ba80549e9baf2",
        "entry_path": "webview/assets/app-initial-DJ_IF-Jc.js",
        "entry_source_sha256": "0d9b7736b930ed682bc44181a1ed2711575e982511d3c17d9945df2599d744fe",
        "main_entry_path": ".vite/build/main-BP8-d4nf.js",
        "main_entry_source_sha256": "15e08d465363e224856ff6e839fde5bd42afcb36d4b0c630522c06cb556344f5",
        "attestation_protocol_entry_path": FRONTEND_ATTESTATION_PROTOCOL_ENTRY_PATH,
        "attestation_protocol_source_sha256": FRONTEND_ATTESTATION_PROTOCOL_SOURCE_SHA256,
        "profile_spec_id": "26825_6671",
    },
    {
        "package_version": "26.825.5331.0",
        "asar_source_sha256": "178b65229452b17b0203ab41d5ceafedccd770c9bd42d239a6d048d27d80252b",
        "entry_path": "webview/assets/app-initial-DWX_sBmZ.js",
        "entry_source_sha256": "c61cd639448f8cd69903090936a29a6e9610cca0dcdbcf4c14851a8bb793a513",
        "main_entry_path": ".vite/build/main-uGaVB6Sz.js",
        "main_entry_source_sha256": "0809a3ece65de285e9a64c1ffccbd3cb57fb646275ffbc7877f0fd5eb8706854",
        "profile_spec_id": "26825_5331",
    },
    {
        "package_version": "26.818.8289.0",
        "asar_source_sha256": "e2f04d6aa921d07981b42368df0a28a8bebe8cd21375d4a1f9286757b51c1313",
        "entry_path": "webview/assets/app-initial-BbHNSfgr.js",
        "entry_source_sha256": "f6d472015d992e044e70d55066044527d06ab648d11aa737836425222c5a9821",
        "main_entry_path": ".vite/build/main-CKEBtOZX.js",
        "main_entry_source_sha256": "41039b646eeee808fbae95ab8fc79e392f6fb42ae56d6722a8c5c337f94e2f6a",
        "profile_spec_id": "26818_8289",
    },
    {
        "package_version": CURRENT_PACKAGE_VERSION,
        "asar_source_sha256": CURRENT_ASAR_SOURCE_SHA256,
        "entry_path": CURRENT_APP_INITIAL_PATH,
        "entry_source_sha256": CURRENT_APP_INITIAL_SOURCE_SHA256,
    },
    {
        "package_version": "26.814.5517.0",
        "asar_source_sha256": "a872ead5cf8f651185fcbc972247ce0d7884fddedd1f0118a044f0801e33a82d",
        "entry_path": "webview/assets/app-initial-C39uD83t.js",
        "entry_source_sha256": "8f7cd5407ce3caad092cacd9fce89a621f5acb73aa7dcb5ae1fc45e00091136c",
        # 26.814.5517.0 ships the priority click-hold machinery natively and
        # only renames its minified bindings.  The three still-missing
        # behaviours (recency-only priority sort, plan-pending yellow dot and
        # remote/SSH project label) are re-landed by hotfix_profile_26820.py.
        "profile_spec_id": "26820",
    },
    {
        "package_version": "26.818.3698.0",
        "asar_source_sha256": "1eb70e2aa26f2408a3e65817f0974e137b1a7ff6e52e43a184154bd4db2074d1",
        "entry_path": "webview/assets/app-initial-izy3qYQi.js",
        "entry_source_sha256": "f09fc19171315b858e31481fce919366387d67cb04ce0bd7322fdd2d68983b26",
        # Exact semantic rebase of the retained Priority, plan-indicator and
        # remote-project-label behaviours onto the 26.818 minified bundle.
        "profile_spec_id": "26818",
    },
    {
        "package_version": "26.818.5229.0",
        "asar_source_sha256": "c5d839bc9b122b7ef2a2f0f45186b3e5895923de5b6cef5253c936fe670c0479",
        "entry_path": "webview/assets/app-initial-BhpTek7p.js",
        "entry_source_sha256": "7359eeff35a798a68c0e610ca65f3b12946e08fdac68cd988a903f061cfce7a0",
        "main_entry_path": ".vite/build/main-g2764IDy.js",
        "main_entry_source_sha256": "a7d58f183ac516b92117b18cd184fbdfe85fa0add0fa13fc753b469cd30d762e",
        # Exact semantic rebase for the second 26.818 Store package. The
        # bundle layout and minified bindings differ from 26.818.3698.0.
        "profile_spec_id": "26818_5229",
    },
    {
        "package_version": "26.810.7004.0",
        "asar_source_sha256": "c7ac6d76cf5f30aa5cb92e1e46561933c06e94e3fe2d6582a04dac18c76f3ed1",
        "entry_path": "webview/assets/app-initial-TxV8Ik1J.js",
        "entry_source_sha256": "e351ed2d369550f43edc141de8d396bbd5b5660704f5dcf801b432f21292133a",
    },
)


FRONTEND_PROFILES = FRONTEND_PROFILES + ({'package_version': '26.908.9136.0', 'asar_source_sha256': '7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d', 'entry_path': 'webview/assets/app-initial-bcc2ff475eb6.js', 'entry_source_sha256': '3c15444f96a8d48844258618fe0d4278409e626f0ee563a77d2c669ec669c510', 'secondary_entry_path': 'webview/assets/app-primary-b36a719dba75.js', 'secondary_entry_source_sha256': '255287957d4cf9a21d386948c997114bf039d5c15fc73258d3df5095114a047a', 'work_page_entry_path': 'webview/assets/page-27d5944f89ff.js', 'work_page_entry_source_sha256': '94344634a845b611c1a61e77eb5c22b992901f9a6c3b3bc9640d0cf18bcbd4b7', 'composer_selector_entry_path': 'webview/assets/composer-project-selector-e0cbbf7896dc.js', 'main_entry_path': '.vite/build/main-D8abTQQE.js', 'main_entry_source_sha256': 'b55be874a9b5a262c09a7945df38cec9b0ce8f14bd584ef73d6feca301ed90b4', 'attestation_protocol_entry_path': '.vite/build/window-all-closed-BxbCP6YG.js', 'attestation_protocol_source_sha256': '8939f42fd89899a649b8062699b386e9ff933c241155b611c3b5ec7a738673ed', 'profile_spec_id': '26908_9136'},)

def frontend_profile_id(profile: dict[str, str | None]) -> str:
    return f"{profile['package_version']}-{str(profile['asar_source_sha256'])[:12]}"


def profile_for_asar(digest: str) -> dict[str, str | None] | None:
    for profile in FRONTEND_PROFILES:
        if digest == profile["asar_source_sha256"]:
            return profile
    return None


def profile_for_entry(path: str, digest: str) -> dict[str, str | None] | None:
    for profile in FRONTEND_PROFILES:
        if path == profile["entry_path"] and digest == profile["entry_source_sha256"]:
            return profile
    return None


def frontend_profile_superseded(profile: dict[str, Any] | None) -> bool:
    """True when the official package refactored the behaviours the current
    profile patches; such profiles keep the official entry byte-identical."""
    return bool(profile is not None and profile.get("frontend_superseded"))


def legacy_frontend_profile() -> dict[str, str | None]:
    """Compatibility view for focused unit tests of the original profile."""
    return {
        "package_version": CURRENT_PACKAGE_VERSION,
        "asar_source_sha256": CURRENT_ASAR_SOURCE_SHA256,
        "asar_patched_sha256": CURRENT_ASAR_PATCHED_SHA256,
        "entry_path": CURRENT_APP_INITIAL_PATH,
        "entry_source_sha256": CURRENT_APP_INITIAL_SOURCE_SHA256,
        "entry_patched_sha256": CURRENT_APP_INITIAL_PATCHED_SHA256,
    }

CURRENT_PRIORITY_SORT_OLD = (
    b"function las(e){return[...e].sort((e,t)=>das[e.attentionState]-"
    b"das[t.attentionState]||t.recencyAt-e.recencyAt)}function uas(e,t){return "
    b"e===`waiting`||!t?e:`unread`}var das,fas=n((()=>{das={waiting:0,unread:1,"
    b"active:2,idle:3}}))"
)
CURRENT_PRIORITY_SORT_NEW = (
    b"function las(e){return[...e].sort((e,t)=>das[e.attentionState]-"
    b"das[t.attentionState]||t.recencyAt-e.recencyAt)}function uas(e,t){return "
    b"e===`active`||e===`waiting`||!t?e:`unread`}var das,fas=n((()=>{das={"
    b"active:0,waiting:1,unread:2,idle:3}}))"
)
CURRENT_GROUP_STATUS_OLD = (
    b"function iHr(e){return e.some(e=>e===`waiting`||e===`unread`)?AHr:"
    b"e.includes(`active`)?kHr:null}"
)
CURRENT_GROUP_STATUS_NEW = (
    b"function iHr(e){return e.includes(`active`)?kHr:e.some(e=>e===`waiting`"
    b"||e===`unread`)?AHr:null}"
)
CURRENT_ACTIVE_STATUS_FALLBACK_OLD = (
    b"let i=t(LHr,r);return i?.hasLiveConversation===!1?t(JHr,e)?`unread`:"
    b"i.summary.threadRuntimeStatus?.type===`active`?`active`:`idle`:t(qRr,r)"
    b"==null?t(JHr,e)?`unread`:t(KRr,r)===`loading`?`active`:`idle`:`waiting`"
)
CURRENT_ACTIVE_STATUS_FALLBACK_NEW = (
    b"let i=t(LHr,r),a=i?.summary?.threadRuntimeStatus?.type===`active`,o=t(rD,r)"
    b"===`needs_resume`;return o?`waiting`:i?.hasLiveConversation===!1?t(JHr,e)"
    b"?`unread`:a?`active`:`idle`:t(qRr,r)==null?t(JHr,e)?`unread`:t(KRr,r)"
    b"===`loading`||a?`active`:`idle`:`waiting`"
)
CURRENT_PRIORITY_FILTER_SORT_OLD = (
    b"DCc=Ca(Q,(e,{get:t})=>las(ECc(t,e).filter(({item:n})=>mCc(t,n,e))))"
)
CURRENT_PRIORITY_FILTER_SORT_NEW = (
    b"DCc=Ca(Q,(e,{get:t})=>ECc(t,e).filter(({item:n})=>mCc(t,n,e)).map("
    b"(e,t)=>({entry:e,index:t})).sort((e,t)=>t.entry.recencyAt-e.entry."
    b"recencyAt||e.index-t.index).map(({entry:e})=>e))"
)
CURRENT_PRIORITY_FILTER_REFRESH_OLD = (
    b"let d=lCc(n,[...l,...n(DCc,r.sidebarMode).map(({item:e})=>e).filter(e=>"
    b"!i.has(q$(n,e)))].filter(e=>!t.has(q$(n,e))))"
)
CURRENT_PRIORITY_FILTER_REFRESH_NEW = (
    b"let d=lCc(n,n(DCc,r.sidebarMode).map(({item:e})=>e).filter(e=>!t.has("
    b"q$(n,e))))"
)
CURRENT_AUTOMATION_PRIORITY_GATE_OLD = (
    b"if(!hCc(e,t,n))return!1;if(t.attentionState!==`idle`)return!0;if(t.kind"
    b"!==`task`)return!1;"
)
CURRENT_AUTOMATION_PRIORITY_GATE_NEW = (
    b"if(!hCc(e,t,n))return!1;if(t.isScheduled)return!0;if(t.attentionState!==`idle`)"
    b"return!0;if(t.kind!==`task`)return!1;"
)
CURRENT_AUTOMATION_IDENTITY_DEPENDENCY_OLD = b"Hw(),MRr(),Tas()"
CURRENT_AUTOMATION_IDENTITY_DEPENDENCY_NEW = b"Hw(),IRr(),MRr(),Tas()"
CURRENT_AUTOMATION_IDENTITY_OLD = (
    b"Pas=Ca(Q,(e,{get:t})=>{let n=vA(e),r=n==null?null:t(Bw,n);return r!=null"
    b"&&t(jRr).automationThreadIds.has(r)})"
)
CURRENT_AUTOMATION_IDENTITY_NEW = (
    b"Pas=(()=>{let e=new Set;return Ca(Q,(t,{get:n})=>{let r=vA(t),i=r==null"
    b"?null:n(Bw,r);if(i==null)return!1;for(let t of n(jRr).automationThreadIds)"
    b"e.add(t);return e.has(i)||(n(Zk).data?.items??[]).some(e=>El(e)&&e.status"
    b"===`ACTIVE`&&e.targetThreadId===i)})})()"
)
CURRENT_UNKNOWN_TURN_STARTED_OLD = (
    b"case`turn/started`:{let{threadId:e,turn:t}=n.params,r=Al(e);if(!this."
    b"conversations.get(r)){sp.error(`Received turn/started for unknown "
    b"conversation`,"
)
CURRENT_UNKNOWN_TURN_STARTED_NEW = (
    b"case`turn/started`:{let{threadId:e,turn:t}=n.params,r=Al(e);if(!this."
    b"conversations.get(r)){this.threadStore.recordThreadRuntimeStatusEvidence("
    b"e,{type:`active`})&&this.hydratePinnedThreads([e]),sp.error(`Received "
    b"turn/started for unknown conversation`,"
)
CURRENT_UNKNOWN_TURN_COMPLETED_OLD = (
    b"let{threadId:e,turn:t}=n.params,r=Al(e);if(!this.conversations.get(r)){"
    b"KBn(this.hostId,e,t.id),"
)
CURRENT_UNKNOWN_TURN_COMPLETED_NEW = (
    b"let{threadId:e,turn:t}=n.params,r=Al(e);if(!this.conversations.get(r)){"
    b"this.threadStore.recordThreadRuntimeStatusEvidence(e,{type:`idle`}),"
    b"KBn(this.hostId,e,t.id),"
)
CURRENT_HOLD_ATOMS_OLD = b"PA=ba(Q,new Map),XVr=ba(Q,new Map)"
CURRENT_HOLD_ATOMS_NEW = (
    b"PA=nh(`sidebar-read-priority-holds-v1`,{}),XVr=PA"
)
CURRENT_HOLD_WRITE_OLD = (
    b"function wVr(e,t,n){let r=MVr(e,t),i=e.get(MA),a=TVr(e,r),o=i==null?"
    b"null:TVr(e,i),s=i!=null&&(i===r||a!=null&&a===o)?i:r;e.set(PA,new Map("
    b"e.get(PA)).set(s,n)),a!=null&&(e.get(kA).data?.threadIds??[]).includes(a)"
    b"&&e.set(XVr,new Map(e.get(XVr)).set(s,n))}"
)
CURRENT_HOLD_WRITE_NEW = (
    b"function wVr(e,t,n){let r=MVr(e,t),i=e.get(MA),a=TVr(e,r),o=i==null?"
    b"null:TVr(e,i),s=i!=null&&(i===r||a!=null&&a===o)?i:r,c=Date.now();e.set("
    b"PA,{...CodexClean(e.get(PA)),[s]:[n,c,c+864e5]})}function CodexEntry(e,t)"
    b"{let n=e?.[t];return Array.isArray(n)&&n.length===3&&n.every(Number.isFinite)"
    b"&&n[2]>Date.now()?n:null}function CodexClean(e){return Object.fromEntries("
    b"Object.entries(e??{}).filter(([t])=>CodexEntry(e,t)!=null))}function "
    b"CodexHold(){let e=No(Q),t=Y(PA);(0,W5.useEffect)"
    b"(()=>{let n=CodexClean(t);if(Object.keys(n).length<Object.keys(t??{}).length)"
    b"e.set(PA,n);else{let r=Math.min(...Object.values(n).map(e=>e[2]));if(r<1/0)"
    b"{let t=setTimeout(()=>e.set(PA,CodexClean(e.get(PA))),r-Date.now()+1);"
    b"return()=>clearTimeout(t)}}},[e,t])}"
)
CURRENT_HOLD_GENERAL_OLD = (
    b"g=t(PA),_=new Set(h);for(let e of f)g.get(e.task.key)===e.recencyAt&&"
    b"_.add(e.task.key);"
)
CURRENT_HOLD_GENERAL_NEW = (
    b"g=t(PA),_=new Set(h);for(let e of f){let t=CodexEntry(g,e.task.key);t?.[0]===e."
    b"recencyAt&&t[2]>Date.now()&&_.add(e.task.key)}"
)
CURRENT_HOLD_PINNED_OLD = (
    b"a=e(XVr);for(let e of i)a.get(e.task.key)===e.recencyAt&&r.add(e.task.key);"
)
CURRENT_HOLD_PINNED_NEW = (
    b"a=e(XVr);for(let e of i){let t=CodexEntry(a,e.task.key);t?.[0]===e.recencyAt"
    b"&&r.add(e.task.key)}"
)
CURRENT_HOLD_PRIORITY_ENTRY_OLD = (
    b"c=r.get(t)===a;if(o==null||!sCc(o))return[];"
)
CURRENT_HOLD_PRIORITY_ENTRY_NEW = (
    b"c=CodexEntry(r,t)?.[0]===a;if(o==null||!sCc(o))return[];"
)
CURRENT_HOLD_PRIORITY_FILTER_OLD = (
    b"let r=e(PA).get(t.threadEntry.key);return r!=null&&r===e(VJ,`codex`)."
    b"threadRecencyAtByKey.get(t.threadEntry.key)}"
)
CURRENT_HOLD_PRIORITY_FILTER_NEW = (
    b"let r=CodexEntry(e(PA),t.threadEntry.key);return r?.[0]===e(VJ,`codex`)."
    b"threadRecencyAtByKey.get(t.threadEntry.key)}"
)
CURRENT_HOLD_SESSION_RESET_OLD = (
    b"e.set(J$,null),e.set(PA,new Map)}function nCc"
)
CURRENT_HOLD_SESSION_RESET_NEW = b"e.set(J$,null)}function nCc"
CURRENT_HOLD_HOOK_OLD = (
    b"function gdu({catalogPageScope:e,catalogSourcesReady:t,codexFeaturesAllowed:n,"
)
CURRENT_HOLD_HOOK_OLD_FULL = (
    CURRENT_HOLD_HOOK_OLD
    + b"sidebarMode:r,workCloudSidebarContentVisible:i,workLocalSidebarContentVisible:a})"
    + b"{let o=No(Q),"
)
CURRENT_HOLD_HOOK_NEW_FULL = (
    CURRENT_HOLD_HOOK_OLD
    + b"sidebarMode:r,workCloudSidebarContentVisible:i,workLocalSidebarContentVisible:a})"
    + b"{CodexHold();let o=No(Q),"
)

CURRENT_PINNED_ACTION_OLD = b"function $as(e,t){e.set(XVr,new Map),e.set(ros,t)}"
CURRENT_PINNED_ACTION_NEW = b"function $as(e,t){e.set(ros,t)}"
CURRENT_GLOBAL_CHAT_SORT_OLD = (
    b"function xos(e,t){let n=e.get(Sz);e.set(PA,new Map),e.set(cca,void 0),"
    b"e.set(sca,{...n,chatSortMode:t})}"
)
CURRENT_GLOBAL_CHAT_SORT_NEW = (
    b"function xos(e,t){let n=e.get(Sz);e.set(ros,t),e.set(cca,void 0),"
    b"e.set(sca,{...n,chatSortMode:t})}"
)
CURRENT_GLOBAL_PROJECT_SORT_OLD = (
    b"function Sos(e,t){let n=e.get(Sz);e.set(PA,new Map),e.set(cca,void 0),"
    b"e.set(sca,{...n,projectSortMode:t})}"
)
CURRENT_GLOBAL_PROJECT_SORT_NEW = (
    b"function Sos(e,t){let n=e.get(Sz);e.set(ros,t),e.set(cca,void 0),"
    b"e.set(sca,{...n,projectSortMode:t})}"
)
CURRENT_PINNED_DEFAULT_OLD = b"ros=nh(`pinned-sidebar-sort-mode-v1`,`manual`)"
CURRENT_PINNED_DEFAULT_NEW = b"ros=nh(`pinned-sidebar-sort-mode-v1`,`priority`)"

CURRENT_PROJECT_GROUP_OLD = (
    b"function Eos({groups:e,items:t,projectOrder:n}){let r=new Map(t.map(e=>"
    b"[e.task.key,e.recencyAt]));return Sca(e.map((e,t)=>({group:e,index:t,"
    b"recencyAt:e.threadKeys.reduce((e,t)=>Math.max(e,r.get(t)??0),e."
    b"projectUpdatedAt??0)})).sort((e,t)=>t.recencyAt-e.recencyAt||e.index-t."
    b"index).map(({group:e})=>e),n)}"
)
CURRENT_PROJECT_GROUP_NEW = (
    b"function Eos({groups:e,items:t,projectOrder:n,sortMode:r,"
    b"attentionStateByThreadKey:i,unreadThreadKeys:a}){let o=new Map(t.map(e=>"
    b"[e.task.key,e.recencyAt]));return Sca(e.map((e,t)=>({group:e,index:t,"
    b"recencyAt:e.threadKeys.reduce((e,t)=>Math.max(e,o.get(t)??0),e."
    b"projectUpdatedAt??0),priority:r===`priority`?Math.min(...e.threadKeys.map("
    b"e=>das[uas(i.get(e)??`idle`,a.has(e))])):0})).sort((e,t)=>e.priority-t."
    b"priority||t.recencyAt-e.recencyAt||e.index-t.index).map(({group:e})=>e),n)}"
)
CURRENT_PROJECT_GROUP_CALL_OLD = (
    b"A=Eos({groups:Tos({groups:O,items:f}),items:f,projectOrder:Cp(t,Il."
    b"PROJECT_ORDER)})"
)
CURRENT_PROJECT_GROUP_CALL_NEW = (
    b"A=Eos({groups:Tos({groups:O,items:f}),items:f,projectOrder:t(Sz)."
    b"projectSortMode===`manual`?Cp(t,Il.PROJECT_ORDER):void 0,sortMode:t(Sz)."
    b"projectSortMode,attentionStateByThreadKey:m,unreadThreadKeys:_})"
)

# The project picker combines the authoritative saved project records with
# sidebar groups.  The official merge replaces the whole saved record with the
# matching group, so a transient group label (for example, the project UUID)
# can overwrite the user-visible name and make label search fail.  Keep the
# saved label while retaining the group's thread metadata.
CURRENT_REMOTE_PROJECT_LABEL_OLD = (
    b"function bas(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return "
    b"yas(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"
)
CURRENT_REMOTE_PROJECT_LABEL_NEW = (
    b"function bas(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return "
    b"yas(e.map(e=>{let t=r.get(e.projectId);return t==null?{...e,threadKeys:"
    b"[]}:{...t,label:e.label}}),n)}"
)
CURRENT_REMOTE_PROJECT_LABEL_HELPER_OLD = b"function sDs(e){let t=(0,cDs.c)(13),"
CURRENT_REMOTE_PROJECT_LABEL_HELPER_NEW = (
    b"function CodexProjectLabel(e){let t=e.label?.trim()??``,n=e.path?.split(`/`)"
    b".filter(Boolean).pop();return e.projectKind===`remote`&&/^[0-9a-f]{8}-(?:"
    b"[0-9a-f]{4}-){3}[0-9a-f]{12}$/i.test(t)&&n?n:t}function sDs(e){let "
    b"t=(1,cDs.c)(13),"
)
CURRENT_REMOTE_PROJECT_LABEL_RENDER_OLD = (
    b"children:e.label}),i?.(e)]})},e.projectId)"
)
CURRENT_REMOTE_PROJECT_LABEL_RENDER_NEW = (
    b"children:CodexProjectLabel(e)}),i?.(e)]})},e.projectId)"
)
CURRENT_REMOTE_PROJECT_LABEL_SEARCH_OLD = (
    b"function Ppc(e){return[e.label,e.gitRepos[0]?.rootFolder,e.path,e."
    b"hostDisplayName]}"
)
CURRENT_REMOTE_PROJECT_LABEL_SEARCH_NEW = (
    b"function Ppc(e){return[CodexProjectLabel(e),e.gitRepos[0]?.rootFolder,e."
    b"path,e.hostDisplayName]}"
)
CURRENT_REMOTE_PROJECT_LABEL_THREAD_MAPS_OLD = (
    b"function jPo(e){return new Map(e.flatMap(e=>e.threadKeys.map(t=>[t,e])))}"
    b"function MPo(e){return new Map(e.flatMap(e=>e.threadKeys.map(t=>[t,e."
    b"label])))}"
)
CURRENT_REMOTE_PROJECT_LABEL_THREAD_MAPS_NEW = (
    b"function jPo(e){return new Map(e.flatMap(e=>{let n={...e,label:"
    b"CodexProjectLabel(e)};return e.threadKeys.map(e=>[e,n])}))}function "
    b"MPo(e){return new Map(e.flatMap(e=>e.threadKeys.map(t=>[t,"
    b"CodexProjectLabel(e)])))}"
)
CURRENT_REMOTE_PROJECT_LABEL_SIDEBAR_OLD = (
    b"N=M!=null&&n.projectKind!==M,P=n.label||T||E,"
)
CURRENT_REMOTE_PROJECT_LABEL_SIDEBAR_NEW = (
    b"N=M!=null&&n.projectKind!==M,P=CodexProjectLabel(n)||T||E,"
)
CURRENT_REMOTE_PROJECT_LABEL_LIST_ARIA_OLD = (
    b"{folder:a.label||a.path||a.projectId}"
)
CURRENT_REMOTE_PROJECT_LABEL_LIST_ARIA_NEW = (
    b"{folder:CodexProjectLabel(a)||a.path||a.projectId}"
)
CURRENT_REMOTE_PROJECT_LABEL_MENU_OLD = (
    b"D=(n.path==null?void 0:h?.[n.path]?.trim())||n.label||n.projectId,O=q7l"
)
CURRENT_REMOTE_PROJECT_LABEL_MENU_NEW = (
    b"D=(n.path==null?void 0:h?.[n.path]?.trim())||CodexProjectLabel(n)||n."
    b"projectId,O=q7l"
)

# The Work-mode project picker is separate from the normal Codex project
# selector.  In 26.727 it reads the local-only atom, dispatches every row
# through the local selector, restores only local selections, and renders a
# local-folder fallback icon.  Reuse the full saved project list (excluding
# ChatGPT mirrors), the shared local/remote dispatcher, and the existing
# remote-host icon treatment.
CURRENT_WORK_PROJECT_SOURCE_OLD = b"u=No(Q),d=Y(jls),f=Y(ROs)"
CURRENT_WORK_PROJECT_SOURCE_NEW = (
    b"u=No(Q),d=Y(Tls).filter(e=>!xca(e)),f=Y(ROs)"
)
CURRENT_WORK_PROJECT_SELECT_OLD = (
    b"x=m?{projects:d,onSelectProject:e=>{zR.select(u,e)}}:void 0"
)
CURRENT_WORK_PROJECT_SELECT_NEW = (
    b"x=m?{projects:d,onSelectProject:e=>{cX(u,e)}}:void 0"
)
CURRENT_WORK_PROJECT_RESTORE_OLD = (
    b"if(p===void 0&&(p=f?.type===`local`?f.projectId:null),u!=null)"
)
CURRENT_WORK_PROJECT_RESTORE_NEW = (
    b"if(p===void 0&&(p=f?.type===`local`||f?.type===`remote`?f.projectId:"
    b"null),u!=null)"
)
CURRENT_WORK_PROJECT_ICON_OLD = (
    b"p=c==null?null:(0,sX.jsx)(IY,{className:`icon-xs`,fallbackIcon:(0,sX."
    b"jsx)(DR,{className:`icon-xs shrink-0`}),isRemoteProject:!1,markerClassName:"
    b"`size-4`,projectId:c})"
)
CURRENT_WORK_PROJECT_ICON_NEW = (
    b"p=c==null?null:(0,sX.jsx)(IY,{className:`icon-xs`,fallbackIcon:(0,sX."
    b"jsx)(iX,{className:`icon-xs shrink-0`,remoteHostId:a?.hostId,"
    b"isRemoteProject:a?.projectKind===`remote`}),isRemoteProject:a?."
    b"projectKind===`remote`,markerClassName:`size-4`,projectId:c})"
)

CURRENT_DROP_OLD = (
    b"y=p==null?h:(0,v$.jsx)(uus,{className:`flex flex-col`,disabled:p."
    b"fileDropDisabled||a===`work`&&p.runLocationState.effectiveLocation!=="
    b"`cloud`,onFilesDropped:p.onFilesDropped,children:h})"
)
CURRENT_DROP_NEW = (
    b"y=p==null?h:a===`work`&&p.runLocationState.effectiveLocation===`local`&&"
    b"!p.fileDropDisabled?h:"
    b"(0,v$.jsx)(uus,{className:`flex flex-col`,disabled:p.fileDropDisabled||"
    b"a===`work`&&p.runLocationState.effectiveLocation==null,onFilesDropped:p."
    b"onFilesDropped,children:h})"
)
CURRENT_LOCAL_DROP_INVARIANTS = (
    b"function nss(e){if(e==null)return[];let t=Array.from(e.items??[]).filter(e=>e.kind===`file`);",
    (
        b"addFileMentionsFromFiles:(e,t)=>{let r=window.electronBridge?."
        b"getPathForFile,i=_3a(e,r,t)"
    ),
    (
        b"function Arc(e){let t=e?.webkitGetAsEntry?.();return t==null||"
        b"t.isDirectory}"
    ),
)

CURRENT_WATCH_PROVIDER = (
    b"function im(e,t){let n=nm(e),r=nm(t);return sm(r)||n===``?ave(r):"
    b"ave(am(n,r))}function S3e(e,t,n){let r=im(e,t);return n?ku(r):r}"
)
CURRENT_WATCH_CALL_OLD = (
    b"getWatchPath(e,t){let n=im(this.params.getConversationCwd(e)??``,t);"
    b"return sm(n)?n:null}"
)
CURRENT_WATCH_CALL_NEW = (
    b"getWatchPath(e,t,n){let r=im(this.params.getConversationCwd(e)??``,t,"
    b"n.hostId===`local`);return sm(r)?r:null}"
)

CURRENT_RESUME_HISTORY_FIXED = (
    b"async getCompleteConversationTurns(e){let t=this.getConversation(e);if(t?."
    b"resumeState!==`resumed`)throw Error(`Conversation must be resumed before "
    b"loading history`);kCt(t)||await this.loadRemainingConversationTurns(e);"
)
CURRENT_TAIL_HISTORY_FIXED = (
    b"function FWn(e,t){e.loadRemainingConversationTurns(t).catch(e=>{ap.warning("
    b"`Failed to load remaining thread turns after resume`"
)
CURRENT_IDLE_HISTORY_FIXED = (
    b"`inactive_thread_unsubscribed`,{safe:{conversationId:e,status:t.status}"
)

RESUME_HISTORY_OLD = (
    b"suppressResumeHistoryDrain:c=()=>e==null?!1:Ci(e,`3446105535`)"
)
RESUME_HISTORY_BUNDLED_OLD = (
    b"suppressResumeHistoryDrain:c=()=>e==null?!1:Nh(e,`3446105535`)"
)
RESUME_HISTORY_SUPPRESS_ALL = b"suppressResumeHistoryDrain:c=()=>!0"
RESUME_HISTORY_FORCE_DRAIN = b"suppressResumeHistoryDrain:c=()=>!1"
RESUME_HISTORY_GUARD_OLD = (
    b"h&&!p&&!_&&!e.suppressResumeHistoryDrain()&&pe?.olderCursor!=null"
)
RESUME_HISTORY_GUARD_NEW = (
    b"h&&!p&&!e.suppressResumeHistoryDrain()&&pe?.olderCursor!=null"
)
IDLE_HISTORY_OLD = (
    b"if(n!=null&&(r||n.resumeState!==`needs_resume`)){let t=r?{type:`notLoaded`}:"
    b"this.getThreadRuntimeStatusAfterUnsubscribe(n);this.params.threadStore."
    b"updateConversationState(e,e=>{e.resumeState=`needs_resume`,e.threadRuntimeStatus=t})}"
)
IDLE_HISTORY_NEW = (
    b"if(n!=null&&(r||n.resumeState!==`needs_resume`)){let t=r?{type:`notLoaded`}:"
    b"this.getThreadRuntimeStatusAfterUnsubscribe(n);this.params.threadStore."
    b"updateConversationState(e,e=>{e.resumeState=`needs_resume`,e.threadRuntimeStatus=t,"
    b"r||(e.turns=Ep,e.requests=Dp,e.turnHistory=void 0)})}"
)
IDLE_HISTORY_BUNDLED_FIXED = (
    b"let t=r?{type:`notLoaded`}:this.getThreadRuntimeStatusAfterUnsubscribe(n),"
    b"i=!this.hasActiveConversationView(e)&&!this.params.streamState."
    b"hasFollowersOrPendingFollowerReconnect(e)&&!this.shouldKeepConversationLoaded(n);"
    b"this.params.threadStore.updateConversationState(e,e=>{i&&(itn(e,[],!1),"
    b"e.turnsPagination={olderCursor:null,oldestLoadedTurnId:null,isLoadingOlder:!1,"
    b"hasLoadedOldest:!1}),e.resumeState=`needs_resume`,e.threadRuntimeStatus=t})"
)
PAGINATED_TAIL_RETENTION_OLD = (
    b"shouldKeepConversationLoaded(e){return e.rolloutPath.length===0&&hot(e)"
    b"?.length===0||e.threadRuntimeStatus?.type===`active`?!0:yg(e)?.status"
    b"===`inProgress`&&(DDt(e)==null||Mdn(e))}"
)
PAGINATED_TAIL_RETENTION_NEW = (
    b"shouldKeepConversationLoaded(e){return e.historyMode===`paginated`||"
    b"e.rolloutPath.length===0&&hot(e)?.length===0||e.threadRuntimeStatus?.type"
    b"===`active`?!0:yg(e)?.status===`inProgress`&&(DDt(e)==null||Mdn(e))}"
)
PAGINATED_TAIL_LOG_OLD = b"`inactive_thread_unsubscribe_candidates_evaluated`"
PAGINATED_TAIL_LOG_NEW = b"`inactive_unsubscribe_candidates`"
WINDOWS_WATCH_IMPORT_OLD = b"ht as en"
WINDOWS_WATCH_IMPORT_NEW = b"ot as en"
WINDOWS_WATCH_DEPENDENCY_SHA256_ALLOWLIST = {
    "webview/assets/broadcast-query-cache-invalidation-UZX65dO_.js": frozenset(
        {"48c4ddf84aa58e00976bcdff68d75d4ceaf3df0ea427bcc3a0f86d9faa4f768e"}
    ),
    "webview/assets/vscode-api-CseDnIoP.js": frozenset(
        {"264b53e58a469d23b0e9fbb071a090c18d4e1ec633d199d31efb049a74f49dc5"}
    ),
}
WINDOWS_WATCH_DEPENDENCY_IMPORT_RE = re.compile(
    rb'import\{(?P<spec>[^}]*)\}from"\./'
    rb'broadcast-query-cache-invalidation-UZX65dO_\.js";'
)
WINDOWS_WATCH_CALL_OLD = (
    b"getWatchPath(e,t){let n=en(this.params.getConversationCwd(e)??``,t);"
    b"return cn(n)?n:null}"
)
WINDOWS_WATCH_CALL_NEW = (
    b"getWatchPath(e,t,n){let r=en(this.params.getConversationCwd(e)??``,t,"
    b"n.hostId===`local`);return cn(r)?r:null}"
)
WINDOWS_WATCH_BUNDLED_PROVIDER = (
    b"function Ef(e,t){let n=wf(e),r=wf(t);return kf(r)||n===``?i_e(r):"
    b"i_e(Df(n,r))}function DXe(e,t,n){let r=Ef(e,t);return n?Kl(r):r}"
)
WINDOWS_WATCH_BUNDLED_CALL_OLD = (
    b"getWatchPath(e,t){let n=Ef(this.params.getConversationCwd(e)??``,t);"
    b"return kf(n)?n:null}"
)
WINDOWS_WATCH_BUNDLED_CALL_NEW = (
    b"getWatchPath(e,t,n){let r=DXe(this.params.getConversationCwd(e)??``,t,"
    b"n.hostId===`local`);return kf(r)?r:null}"
)
WINDOWS_WATCH_HOST_CALLS = (
    (
        b"ignoreFileChangeEvents(e,t){let n=this.getWatchPath(e,t.path);",
        b"ignoreFileChangeEvents(e,t){let n=this.getWatchPath(e,t.path,t);",
    ),
    (
        b"getNextWatchTarget(e,t,n){let r=this.getWatchPath(t,n.path);",
        b"getNextWatchTarget(e,t,n){let r=this.getWatchPath(t,n.path,n);",
    ),
    (
        b"getMcpResourceWatchStartPromise(e,t){let n=this.getWatchPath(e,t.path);",
        b"getMcpResourceWatchStartPromise(e,t){let n=this.getWatchPath(e,t.path,t);",
    ),
)
WINDOWS_WATCH_TOTAL_CALL = b"this.getWatchPath("
LABEL_INIT_OLD = b"p=r===void 0?null:r,m=o(c),g=n;"
LABEL_FIXED_RE = re.compile(
    rb"p=r\?\?[A-Za-z_$][A-Za-z0-9_$]*\.find\(e=>e\.id===n\)"
    rb"\?\.label\?\?null,m=o\(c\),g=n;"
)
LABEL_BUNDLED_OLD = b"d=r===void 0?null:r,f=Y(UE),p=n;"
LABEL_BUNDLED_NEW = (
    b"q=Bo(I8n,n),d=r??q?.label??null,f=Y(UE),p=n;"
)
LABEL_BUNDLED_PROVIDER = (
    b"I8n=Aa(Q,(e,{get:t})=>e==null?null:t(F8n).find(t=>t.id===e)??null)"
)
LABEL_BUNDLED_FUNCTION_START = b"function p6s("
LABEL_BUNDLED_FUNCTION_END = b"function m6s("
THREAD_CONTEXT_IMPORT_RE = re.compile(
    rb'import\{(?P<spec>[^}]*)\}from"(?P<path>\./thread-context-inputs-[^"]+\.js)";'
)
IDENTIFIER_RE = re.compile(rb"(?<![A-Za-z0-9_$])([A-Za-z_$][A-Za-z0-9_$]*)(?![A-Za-z0-9_$])")
SOURCE_MAP_PREFIX = b"//# sourceMappingURL="
PROCESS_READ_OLD = (
    b"async function sJ(e){try{let t=await(0,u.readFile)(pJ(e),`utf8`),"
    b"n=aJ.safeParse(JSON.parse(t));return n.success?n.data.map(e=>({...e,"
    b"conversationId:t_(e.conversationId),osPid:e.osPid??null})):[]}"
    b"catch(e){if(e instanceof Error&&`code`in e&&e.code===`ENOENT`)"
    b"return[];throw e}"
)
PROCESS_READ_NEW = PROCESS_READ_OLD.replace(
    b"catch(e){if(e instanceof Error&&`code`in e&&e.code===`ENOENT`)"
    b"return[];throw e}",
    b"catch(e){if(e instanceof SyntaxError||e?.code===`ENOENT`)return[];throw e}",
)
PROCESS_WRITE_OLD = (
    b"async function mJ(e,t){let n=pJ(e);await(0,u.mkdir)"
    b"(i.default.dirname(n),{recursive:!0}),await(0,u.writeFile)"
    b"(n,JSON.stringify(t,null,2),`utf8`)}"
)
PROCESS_WRITE_NEW = (
    b"async function mJ(e,t){let n=pJ(e),r=n+Math.random();await(0,u.mkdir)"
    b"(i.default.dirname(n),{recursive:!0}),await(0,u.writeFile)"
    b"(r,JSON.stringify(t),{flush:!0}),await(0,u.rename)(r,n)}"
)
PROCESS_READ_BUNDLED_OLD = (
    b"async function nX(e){try{let t=await(0,l.readFile)(cX(e),`utf8`),"
    b"n=eX.safeParse(JSON.parse(t));return n.success?n.data.map(e=>({...e,"
    b"conversationId:Ig(e.conversationId),osPid:e.osPid??null})):[]}"
    b"catch(e){if(e instanceof Error&&`code`in e&&e.code===`ENOENT`)"
    b"return[];throw e}"
)
PROCESS_READ_BUNDLED_NEW = PROCESS_READ_BUNDLED_OLD.replace(
    b"catch(e){if(e instanceof Error&&`code`in e&&e.code===`ENOENT`)"
    b"return[];throw e}",
    b"catch(e){if(e instanceof SyntaxError||e?.code===`ENOENT`)return[];throw e}",
)
PROCESS_WRITE_BUNDLED_OLD = (
    b"async function lX(e,t){let n=cX(e);await(0,l.mkdir)"
    b"(i.default.dirname(n),{recursive:!0}),await(0,l.writeFile)"
    b"(n,JSON.stringify(t,null,2),`utf8`)}"
)
PROCESS_WRITE_BUNDLED_NEW = (
    b"async function lX(e,t){let n=cX(e),r=n+Math.random();await(0,l.mkdir)"
    b"(i.default.dirname(n),{recursive:!0}),await(0,l.writeFile)"
    b"(r,JSON.stringify(t),{flush:!0}),await(0,l.rename)(r,n)}"
)
PROCESS_REGISTRY_REMOVED_MAIN_SHA256 = (
    "0809a3ece65de285e9a64c1ffccbd3cb57fb646275ffbc7877f0fd5eb8706854"
)
PROCESS_REGISTRY_REMOVED_MAIN_PORTABLE_SHA256 = (
    "1c5524826e912ce87eebc7cd7eda43e838e9714084214d4a06577ccf06b5d3fb"
)
PROCESS_REGISTRY_REMOVED_MAIN_26825_6671_SHA256 = (
    "15e08d465363e224856ff6e839fde5bd42afcb36d4b0c630522c06cb556344f5"
)
PROCESS_REGISTRY_REMOVED_MAIN_26825_6671_PORTABLE_SHA256 = (
    "c1cf02ad7e28cea13fba8f131d5e8a0a79618f19f49c5f31bc1e6ecca27a5838"
)
PROCESS_REGISTRY_REMOVED_MAIN_26831_2377_SHA256 = (
    "54df4fc5632b2d307fba49c3fa9399dca4845b61162ca76dac998c4be86ef276"
)
PROCESS_REGISTRY_REMOVED_MAIN_26831_2377_PORTABLE_SHA256 = (
    "2cc623799c4988381f089dcd8468fd1ab651a3e626ae18f50b77d1c7a3613d45"
)
PROCESS_REGISTRY_REMOVED_MAIN_26901_6511_SHA256 = (
    "2863c5b445ee465a1943e9ef431c824d1b0dd78fa72d11790bb53f5ee8bc67bb"
)
PROCESS_REGISTRY_REMOVED_MAIN_26901_6511_PORTABLE_SHA256 = (
    "b19dd9f00e9b2ed880db4aa86182e729979e417d80186e60cad4932bdefd18f1"
)
PROCESS_REGISTRY_REMOVED_MAIN_26903_9818_SHA256 = (
    "471f06dfcda15de10196f701504244c6f412d7ed401c155efc56a427a89a3195"
)
PROCESS_REGISTRY_REMOVED_MAIN_26903_9818_PORTABLE_SHA256 = (
    "19122216930eb6a36681ab0a14335ad6fff004e684aee1ada070d13317867f3b"
)
PROCESS_REGISTRY_REMOVED_MAIN_26908_4834_SHA256 = (
    "b55be874a9b5a262c09a7945df38cec9b0ce8f14bd584ef73d6feca301ed90b4"
)
PROCESS_REGISTRY_REMOVED_MAIN_26908_4834_PORTABLE_SHA256 = (
    "79a4d9a07eea4489ad55e9722fefdc9e8af3be0d32ee9b1d05b5847cceab7c92"
)
PROCESS_REGISTRY_REMOVED_MAIN_SOURCE_SHA256S = {
    PROCESS_REGISTRY_REMOVED_MAIN_SHA256,
    PROCESS_REGISTRY_REMOVED_MAIN_26825_6671_SHA256,
    PROCESS_REGISTRY_REMOVED_MAIN_26831_2377_SHA256,
    PROCESS_REGISTRY_REMOVED_MAIN_26901_6511_SHA256,
    PROCESS_REGISTRY_REMOVED_MAIN_26903_9818_SHA256,
    PROCESS_REGISTRY_REMOVED_MAIN_26908_4834_SHA256,
}
PROCESS_REGISTRY_REMOVED_MAIN_ALL_SHA256S = {
    *PROCESS_REGISTRY_REMOVED_MAIN_SOURCE_SHA256S,
    PROCESS_REGISTRY_REMOVED_MAIN_PORTABLE_SHA256,
    PROCESS_REGISTRY_REMOVED_MAIN_26825_6671_PORTABLE_SHA256,
    PROCESS_REGISTRY_REMOVED_MAIN_26831_2377_PORTABLE_SHA256,
    PROCESS_REGISTRY_REMOVED_MAIN_26901_6511_PORTABLE_SHA256,
    # 26.903.9818.0 already removed the legacy process registry upstream; its
    # portable main entry differs from the source only by the exact
    # portable update-menu patch, so the rebuilt entry stays official-fixed.
    PROCESS_REGISTRY_REMOVED_MAIN_26903_9818_PORTABLE_SHA256,
    # 26.908.4834.0 has the same upstream removal. This is the exact digest
    # after applying only the allowlisted portable update-menu transformation.
    PROCESS_REGISTRY_REMOVED_MAIN_26908_4834_PORTABLE_SHA256,
}
CRITICAL_FILES = (
    "ChatGPT.exe",
    "chrome.dll",
    "chrome_elf.dll",
    "resources.pak",
    "icudtl.dat",
    "v8_context_snapshot.bin",
)
CODEX_BACKEND_RELATIVE = Path("resources") / "codex.exe"
REQUIRED_FEATURES = (
    "priority_filter_recency_sorting",
    "priority_filter_live_resort",
    "priority_filter_pinned_recency_sorting",
    "priority_filter_hold_membership",
    "priority_click_hold",
    "priority_identity_migration",
    "priority_project_context_subtitle",
    "plan_pending_detection",
    "plan_pending_yellow_indicator",
    "attention_highlight_color_semantics",
    "remote_project_label",
    "resume_history_on_demand",
    "paginated_tail_retention",
    "windows_watch_path_normalization",
    "archived_heartbeat_terminal_guard",
    "process_registry_resilience",
)
OPTIONAL_FEATURES = (
    "idle_history_eviction",
    "remote_project_label",
    "work_remote_project_picker",
)
FEATURE_STATUSES = {
    "priority_filter_recency_sorting": {"patched", "official_fixed"},
    "priority_filter_live_resort": {"patched", "official_fixed"},
    "priority_filter_pinned_recency_sorting": {"patched", "official_fixed"},
    "priority_filter_hold_membership": {"patched", "official_fixed"},
    "priority_click_hold": {"patched", "official_fixed"},
    "priority_identity_migration": {"patched", "official_fixed"},
    "priority_project_context_subtitle": {"patched", "official_fixed"},
    "plan_pending_detection": {"patched", "official_fixed"},
    "plan_pending_yellow_indicator": {"patched", "official_fixed"},
    "plan_pending_unread_indicator": {"patched", "official_fixed"},
    "attention_highlight_color_semantics": {"patched", "official_fixed"},
    "project_sorting": {"patched", "official_fixed"},
    "active_priority_sort": {"patched", "official_fixed"},
    "automation_priority_gate": {"patched", "official_fixed"},
    "pinned_priority_sync": {"patched", "official_fixed"},
    "new_chat_file_drop": {"patched", "official_fixed"},
    "resume_history_on_demand": {"patched", "official_fixed"},
    "paginated_tail_retention": {"patched", "official_fixed"},
    "windows_watch_path_normalization": {"patched", "official_fixed"},
    "archived_heartbeat_terminal_guard": {"patched", "official_fixed"},
    "idle_history_eviction": {"patched", "official_fixed", "unsupported"},
    "remote_project_label": {"patched", "official_fixed", "unsupported"},
    "work_remote_project_picker": {"patched", "official_fixed", "unsupported"},
    "process_registry_resilience": {
        "patched",
        "official_fixed",
        "unsupported",
    },
}


class HotfixError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pe_machine(path: Path) -> str:
    with path.open("rb") as handle:
        if handle.read(2) != b"MZ":
            raise HotfixError(f"PE DOS signature is missing: {path}")
        handle.seek(0x3C)
        offset_bytes = handle.read(4)
        if len(offset_bytes) != 4:
            raise HotfixError(f"PE header offset is truncated: {path}")
        pe_offset = struct.unpack("<I", offset_bytes)[0]
        handle.seek(pe_offset)
        if handle.read(4) != b"PE\0\0":
            raise HotfixError(f"PE signature is missing: {path}")
        machine_bytes = handle.read(2)
        if len(machine_bytes) != 2:
            raise HotfixError(f"PE machine field is truncated: {path}")
    machine = struct.unpack("<H", machine_bytes)[0]
    if machine != 0x8664:
        raise HotfixError(f"Codex backend is not an AMD64 PE image: 0x{machine:04x}")
    return "amd64"


def pe_authenticode_status(path: Path) -> str:
    with path.open("rb") as handle:
        if handle.read(2) != b"MZ":
            raise HotfixError(f"PE DOS signature is missing: {path}")
        handle.seek(0x3C)
        offset_bytes = handle.read(4)
        if len(offset_bytes) != 4:
            raise HotfixError(f"PE header offset is truncated: {path}")
        pe_offset = struct.unpack("<I", offset_bytes)[0]
        optional_offset = pe_offset + 4 + 20
        handle.seek(optional_offset)
        magic_bytes = handle.read(2)
        if len(magic_bytes) != 2:
            raise HotfixError(f"PE optional header is truncated: {path}")
        magic = struct.unpack("<H", magic_bytes)[0]
        if magic == 0x20B:
            data_directories_offset = 112
        elif magic == 0x10B:
            data_directories_offset = 96
        else:
            raise HotfixError(f"PE optional header magic is invalid: 0x{magic:04x}")
        certificate_entry = optional_offset + data_directories_offset + (4 * 8)
        handle.seek(certificate_entry)
        entry = handle.read(8)
        if len(entry) != 8:
            raise HotfixError(f"PE certificate table is truncated: {path}")
    certificate_offset, certificate_size = struct.unpack("<II", entry)
    return (
        "EmbeddedSignature"
        if certificate_offset != 0 and certificate_size != 0
        else "NotSigned"
    )


def codex_version_output(path: Path) -> str:
    creationflags = 0x08000000 if os.name == "nt" else 0
    try:
        completed = subprocess.run(
            [str(path), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
            creationflags=creationflags,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise HotfixError(f"Unable to query patched Codex backend version: {exc}") from exc
    output = (completed.stdout or completed.stderr).strip()
    if completed.returncode != 0 or not output or "\n" in output or "\r" in output:
        raise HotfixError("Patched Codex backend version output is invalid")
    return output


def _bundle_file(bundle_root: Path, relative: Any, label: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise HotfixError(f"Codex backend patch {label} is invalid")
    candidate = Path(relative)
    if candidate.is_absolute():
        raise HotfixError(f"Codex backend patch {label} must be relative")
    resolved_root = bundle_root.resolve()
    resolved = (resolved_root / candidate).resolve()
    if not resolved.is_relative_to(resolved_root):
        raise HotfixError(f"Codex backend patch {label} escapes its bundle")
    return resolved


def load_codex_backend_patch_policy(
    patch_manifest_path: Path,
    expected_descriptor_sha256: str,
) -> tuple[dict[str, Any], str]:
    if not patch_manifest_path.is_file():
        raise HotfixError(
            f"Codex backend patch manifest is missing: {patch_manifest_path}"
        )
    descriptor_bytes = patch_manifest_path.read_bytes()
    descriptor_sha256 = sha256_bytes(descriptor_bytes)
    if (
        not re.fullmatch(r"[0-9a-f]{64}", expected_descriptor_sha256)
        or descriptor_sha256 != expected_descriptor_sha256
    ):
        raise HotfixError("Codex backend patch descriptor is not allowlisted")
    policy = json.loads(descriptor_bytes)
    if not isinstance(policy, dict):
        raise HotfixError("Codex backend patch policy is invalid")
    return policy, descriptor_sha256


def select_codex_backend_package(
    policy: dict[str, Any],
    package_full_name: str,
    package_version: str,
) -> dict[str, str]:
    if policy.get("schema_version") != 2:
        raise HotfixError("Unsupported Codex backend patch schema")
    compatibility = policy.get("compatibility")
    packages = compatibility.get("packages") if isinstance(compatibility, dict) else None
    if not isinstance(packages, list) or not packages:
        raise HotfixError("Codex backend patch compatibility is invalid")
    normalized: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for candidate in packages:
        if (
            not isinstance(candidate, dict)
            or set(candidate) != {"package_full_name", "package_version"}
            or not isinstance(candidate.get("package_full_name"), str)
            or not candidate["package_full_name"]
            or not isinstance(candidate.get("package_version"), str)
            or not candidate["package_version"]
        ):
            raise HotfixError("Codex backend patch compatibility is invalid")
        key = (candidate["package_full_name"], candidate["package_version"])
        if key in seen:
            raise HotfixError("Codex backend patch compatibility contains duplicates")
        seen.add(key)
        normalized.append(
            {
                "package_full_name": candidate["package_full_name"],
                "package_version": candidate["package_version"],
            }
        )
    matches = [
        candidate
        for candidate in normalized
        if candidate["package_full_name"] == package_full_name
        and candidate["package_version"] == package_version
    ]
    if len(matches) != 1:
        raise HotfixError("Codex backend patch compatibility is invalid")
    return matches[0]


def prepare_codex_backend_patch(
    source_app: Path,
    portable_app: Path,
    patch_manifest_path: Path,
    package_full_name: str,
    package_version: str,
    expected_descriptor_sha256: str,
) -> dict[str, Any]:
    policy, descriptor_sha256 = load_codex_backend_patch_policy(
        patch_manifest_path,
        expected_descriptor_sha256,
    )
    matched_package = select_codex_backend_package(
        policy,
        package_full_name,
        package_version,
    )
    patch_id = policy.get("patch_id")
    if not isinstance(patch_id, str) or not patch_id:
        raise HotfixError("Codex backend patch id is invalid")

    if policy.get("mode") == "official":
        official_policy = policy.get("official")
        provenance = policy.get("provenance")
        if not isinstance(official_policy, dict) or not isinstance(provenance, dict) or not provenance:
            raise HotfixError("Codex backend official policy inventory is invalid")
        source_codex = source_app / CODEX_BACKEND_RELATIVE
        portable_codex = portable_app / CODEX_BACKEND_RELATIVE
        if not source_codex.is_file() or not portable_codex.is_file():
            raise HotfixError("Official Codex backend is missing")
        official_size = source_codex.stat().st_size
        official_hash = sha256_path(source_codex)
        if (
            official_policy.get("size") != official_size
            or official_policy.get("sha256") != official_hash
            or official_policy.get("pe_machine") != pe_machine(source_codex)
        ):
            raise HotfixError("Official Codex backend differs from the patch policy")
        if (
            portable_codex.stat().st_size != official_size
            or sha256_path(portable_codex) != official_hash
        ):
            raise HotfixError("Staged Codex backend is not an exact official copy")
        version_output = codex_version_output(portable_codex)
        authenticode_status = pe_authenticode_status(portable_codex)
        expected_version_output = policy.get("version_output")
        expected_authenticode_status = policy.get("authenticode_status")
        if (
            expected_version_output is not None
            and expected_version_output != version_output
        ):
            raise HotfixError("Official Codex backend version differs from the patch policy")
        if (
            expected_authenticode_status is not None
            and expected_authenticode_status != authenticode_status
        ):
            raise HotfixError("Official Codex backend signature differs from the patch policy")
        return {
            "status": "official",
            "path": CODEX_BACKEND_RELATIVE.as_posix(),
            "patch_id": patch_id,
            "descriptor_sha256": descriptor_sha256,
            "compatibility": {
                "policy_schema_version": 2,
                "matched_package": matched_package,
            },
            "official": {
                "size": official_size,
                "sha256": official_hash,
                "pe_machine": pe_machine(source_codex),
            },
            "version_output": version_output,
            "authenticode_status": authenticode_status,
            "provenance": provenance,
        }

    official_policy = policy.get("official")
    patched_policy = policy.get("patched")
    provenance = policy.get("provenance")
    if not isinstance(official_policy, dict) or not isinstance(patched_policy, dict):
        raise HotfixError("Codex backend patch file inventory is invalid")
    if not isinstance(provenance, dict) or not provenance:
        raise HotfixError("Codex backend patch provenance is missing")

    source_codex = source_app / CODEX_BACKEND_RELATIVE
    portable_codex = portable_app / CODEX_BACKEND_RELATIVE
    if not source_codex.is_file():
        raise HotfixError(f"Official Codex backend is missing: {source_codex}")
    if not portable_codex.is_file():
        raise HotfixError(f"Staged Codex backend is missing: {portable_codex}")

    official_size = source_codex.stat().st_size
    official_hash = sha256_path(source_codex)
    if (
        official_policy.get("size") != official_size
        or official_policy.get("sha256") != official_hash
        or official_policy.get("pe_machine") != pe_machine(source_codex)
    ):
        raise HotfixError("Official Codex backend differs from the patch policy")
    if (
        portable_codex.stat().st_size != official_size
        or sha256_path(portable_codex) != official_hash
    ):
        raise HotfixError("Staged Codex backend is not an exact official copy")

    bundle_root = patch_manifest_path.parent
    patched_source = _bundle_file(
        bundle_root, patched_policy.get("file"), "executable path"
    )
    if not patched_source.is_file():
        raise HotfixError(f"Patched Codex backend is missing: {patched_source}")
    patched_size = patched_source.stat().st_size
    patched_hash = sha256_path(patched_source)
    if (
        patched_policy.get("size") != patched_size
        or patched_policy.get("sha256") != patched_hash
        or patched_policy.get("pe_machine") != pe_machine(patched_source)
        or patched_policy.get("authenticode_status")
        != pe_authenticode_status(patched_source)
        or patched_policy.get("authenticode_status") != "NotSigned"
    ):
        raise HotfixError("Patched Codex backend differs from the patch policy")
    if patched_hash == official_hash:
        raise HotfixError("Codex backend patch does not change the official executable")

    staged_patch = portable_codex.with_name(
        f".{portable_codex.name}.patch-{uuid.uuid4().hex}.tmp"
    )
    try:
        shutil.copy2(patched_source, staged_patch)
        if (
            staged_patch.stat().st_size != patched_size
            or sha256_path(staged_patch) != patched_hash
            or pe_machine(staged_patch) != "amd64"
            or pe_authenticode_status(staged_patch) != "NotSigned"
        ):
            raise HotfixError("Patched Codex backend copy verification failed")
        version_output = codex_version_output(staged_patch)
        if patched_policy.get("version_output") != version_output:
            raise HotfixError(
                "Patched Codex backend version differs from the patch policy"
            )
        os.replace(staged_patch, portable_codex)
    finally:
        staged_patch.unlink(missing_ok=True)
    if (
        portable_codex.stat().st_size != patched_size
        or sha256_path(portable_codex) != patched_hash
        or pe_machine(portable_codex) != "amd64"
        or pe_authenticode_status(portable_codex) != "NotSigned"
        or codex_version_output(portable_codex) != version_output
    ):
        raise HotfixError("Patched Codex backend final verification failed")

    return {
        "status": "patched",
        "path": CODEX_BACKEND_RELATIVE.as_posix(),
        "patch_id": patch_id,
        "descriptor_sha256": descriptor_sha256,
        "compatibility": {
            "policy_schema_version": 2,
            "matched_package": matched_package,
        },
        "official": {
            "size": official_size,
            "sha256": official_hash,
            "pe_machine": "amd64",
        },
        "patched": {
            "size": patched_size,
            "sha256": patched_hash,
            "pe_machine": "amd64",
            "authenticode_status": pe_authenticode_status(patched_source),
            "version_output": version_output,
        },
        "provenance": provenance,
    }


def bundled_app_initial_allowlist_reason(
    path: str,
    digest: str,
) -> str | None:
    if not path.startswith("webview/assets/app-initial-"):
        return None
    known_profile_entries = {
        profile["entry_source_sha256"]
        for profile in FRONTEND_PROFILES
        if profile["entry_source_sha256"]
    }
    if digest in BUNDLED_APP_INITIAL_ENTRY_SHA256_ALLOWLIST or digest in known_profile_entries:
        return None
    return f"bundled_entry_sha256_not_allowlisted: sha256={digest}"


def walk_entries(files: dict[str, Any], prefix: str = "") -> Iterable[tuple[str, dict[str, Any]]]:
    for name, meta in files.items():
        path = f"{prefix}/{name}" if prefix else name
        if "files" in meta:
            yield from walk_entries(meta["files"], path)
        else:
            yield path, meta


def get_entry_meta(header: dict[str, Any], path: str) -> dict[str, Any]:
    files = header["files"]
    meta: dict[str, Any] | None = None
    for index, part in enumerate(path.split("/")):
        meta = files.get(part)
        if meta is None:
            raise HotfixError(f"ASAR entry disappeared: {path}")
        if index < len(path.split("/")) - 1:
            files = meta.get("files", {})
    if meta is None:
        raise HotfixError(f"ASAR entry is missing: {path}")
    return meta


def read_asar(source: Path) -> tuple[int, bytes, dict[str, Any]]:
    with source.open("rb") as handle:
        prefix = handle.read(16)
        if len(prefix) != 16:
            raise HotfixError("ASAR header is truncated")
        header_size = struct.unpack_from("<I", prefix, 4)[0]
        json_size = struct.unpack_from("<I", prefix, 12)[0]
        if header_size < 8 or json_size < 2 or json_size > header_size:
            raise HotfixError("ASAR header sizes are invalid")
        header_json = handle.read(json_size)
        try:
            header = json.loads(header_json.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HotfixError(f"ASAR header JSON is invalid: {exc}") from exc
        handle.seek(0)
        serialized_header = handle.read(8 + header_size)
    if len(serialized_header) != 8 + header_size:
        raise HotfixError("ASAR serialized header is truncated")
    return header_size, serialized_header, header


def asar_header_json_sha256(path: Path) -> str:
    _, serialized_header, _ = read_asar(path)
    json_size = struct.unpack_from("<I", serialized_header, 12)[0]
    header_json = serialized_header[16 : 16 + json_size]
    if len(header_json) != json_size:
        raise HotfixError("ASAR header JSON is truncated")
    return sha256_bytes(header_json)


def _executable_asar_integrity_record(header_sha256: str) -> bytes:
    if not re.fullmatch(r"[0-9a-f]{64}", header_sha256):
        raise HotfixError("ASAR header digest is invalid")
    return (
        b'{"file":"resources\\\\app.asar","alg":"SHA256","value":"'
        + header_sha256.encode("ascii")
        + b'"}'
    )


def synchronize_executable_asar_integrity(
    source_app: Path,
    portable_app: Path,
    source_asar: Path,
    portable_asar: Path,
    profile: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Synchronize Electron's exact embedded ASAR-header digest.

    Codex 26.901 introduced ElectronAsarIntegrity.  Modifying any ASAR entry
    changes the JSON header digest, so the copied browser executable must carry
    the matching value.  The update is a single, fixed-length 64-byte field;
    every other executable byte remains identical to the signed Store source.
    """
    if not profile or not profile.get("embedded_asar_header_source_sha256"):
        return None
    source_executable = source_app / "ChatGPT.exe"
    portable_executable = portable_app / "ChatGPT.exe"
    expected_source_executable_sha256 = str(
        profile.get("executable_source_sha256") or ""
    )
    expected_source_header_sha256 = str(
        profile.get("embedded_asar_header_source_sha256") or ""
    )
    if (
        not source_executable.is_file()
        or not portable_executable.is_file()
        or sha256_path(source_executable) != expected_source_executable_sha256
        or source_executable.stat().st_size != portable_executable.stat().st_size
        or portable_executable.read_bytes() != source_executable.read_bytes()
        or pe_machine(source_executable) != "amd64"
    ):
        raise HotfixError("Official executable identity differs from the ASAR-integrity profile")
    actual_source_header_sha256 = asar_header_json_sha256(source_asar)
    target_header_sha256 = asar_header_json_sha256(portable_asar)
    if actual_source_header_sha256 != expected_source_header_sha256:
        raise HotfixError("Official ASAR header digest differs from the executable-integrity profile")
    if target_header_sha256 == actual_source_header_sha256:
        raise HotfixError("Portable ASAR did not change but executable-integrity synchronization was requested")
    source_record = _executable_asar_integrity_record(actual_source_header_sha256)
    target_record = _executable_asar_integrity_record(target_header_sha256)
    executable = source_executable.read_bytes()
    if executable.count(source_record) != 1 or executable.count(target_record) != 0:
        raise HotfixError("Embedded ASAR-integrity record is missing or ambiguous")
    record_offset = executable.index(source_record)
    value_offset = record_offset + source_record.index(
        actual_source_header_sha256.encode("ascii")
    )
    patched_executable = executable[:value_offset] + target_header_sha256.encode(
        "ascii"
    ) + executable[value_offset + 64 :]
    if (
        len(patched_executable) != len(executable)
        or patched_executable[:value_offset] != executable[:value_offset]
        or patched_executable[value_offset + 64 :] != executable[value_offset + 64 :]
        or patched_executable.count(target_record) != 1
        or patched_executable.count(source_record) != 0
    ):
        raise HotfixError("Executable ASAR-integrity replacement escaped its fixed field")
    atomic_replace_bytes(portable_executable, patched_executable)
    return {
        "policy": "electron_embedded_asar_header_sha256_v1",
        "executable_relative_path": "ChatGPT.exe",
        "asar_relative_path": "resources/app.asar",
        "algorithm": "SHA256",
        "record_file": "resources\\app.asar",
        "record_offset": record_offset,
        "value_offset": value_offset,
        "value_length": 64,
        "source_executable_size": len(executable),
        "source_executable_sha256": expected_source_executable_sha256,
        "portable_executable_sha256": sha256_bytes(patched_executable),
        "source_asar_header_sha256": actual_source_header_sha256,
        "portable_asar_header_sha256": target_header_sha256,
        "source_pe_machine": "amd64",
        "portable_pe_machine": pe_machine(portable_executable),
        "authenticode_container_status": pe_authenticode_status(portable_executable),
        "windows_signature_validation_expected": "HashMismatch_after_fixed_field_sync",
        "changed_span_only": True,
    }


def verify_executable_asar_integrity(
    source_app: Path,
    portable_app: Path,
    source_asar: Path,
    portable_asar: Path,
    profile: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not profile or not profile.get("embedded_asar_header_source_sha256"):
        return None
    source_executable = source_app / "ChatGPT.exe"
    portable_executable = portable_app / "ChatGPT.exe"
    source_hash = str(profile.get("executable_source_sha256") or "")
    source_header_hash = asar_header_json_sha256(source_asar)
    portable_header_hash = asar_header_json_sha256(portable_asar)
    if (
        not source_executable.is_file()
        or not portable_executable.is_file()
        or sha256_path(source_executable) != source_hash
        or source_header_hash
        != str(profile.get("embedded_asar_header_source_sha256") or "")
        or source_executable.stat().st_size != portable_executable.stat().st_size
        or pe_machine(source_executable) != "amd64"
        or pe_machine(portable_executable) != "amd64"
    ):
        raise HotfixError("Executable ASAR-integrity identity is invalid")
    source_bytes = source_executable.read_bytes()
    portable_bytes = portable_executable.read_bytes()
    source_record = _executable_asar_integrity_record(source_header_hash)
    portable_record = _executable_asar_integrity_record(portable_header_hash)
    if source_bytes.count(source_record) != 1 or portable_bytes.count(portable_record) != 1:
        raise HotfixError("Executable ASAR-integrity record does not match the ASAR header")
    record_offset = source_bytes.index(source_record)
    value_offset = record_offset + source_record.index(source_header_hash.encode("ascii"))
    if (
        portable_bytes[:value_offset] != source_bytes[:value_offset]
        or portable_bytes[value_offset + 64 :] != source_bytes[value_offset + 64 :]
        or portable_bytes[value_offset : value_offset + 64]
        != portable_header_hash.encode("ascii")
    ):
        raise HotfixError("Portable executable differs outside its ASAR-integrity value")
    return {
        "policy": "electron_embedded_asar_header_sha256_v1",
        "executable_relative_path": "ChatGPT.exe",
        "asar_relative_path": "resources/app.asar",
        "algorithm": "SHA256",
        "record_file": "resources\\app.asar",
        "record_offset": record_offset,
        "value_offset": value_offset,
        "value_length": 64,
        "source_executable_size": len(source_bytes),
        "source_executable_sha256": source_hash,
        "portable_executable_sha256": sha256_bytes(portable_bytes),
        "source_asar_header_sha256": source_header_hash,
        "portable_asar_header_sha256": portable_header_hash,
        "source_pe_machine": "amd64",
        "portable_pe_machine": "amd64",
        "authenticode_container_status": pe_authenticode_status(portable_executable),
        "windows_signature_validation_expected": "HashMismatch_after_fixed_field_sync",
        "changed_span_only": True,
    }


def read_entry(source: Path, header_size: int, meta: dict[str, Any]) -> tuple[int, bytes]:
    if meta.get("unpacked"):
        raise HotfixError("Target ASAR entry is unexpectedly unpacked")
    absolute_offset = 8 + header_size + int(meta["offset"])
    size = int(meta["size"])
    with source.open("rb") as handle:
        handle.seek(absolute_offset)
        data = handle.read(size)
    if len(data) != size:
        raise HotfixError("ASAR entry is truncated")
    integrity = meta.get("integrity", {})
    expected = integrity.get("hash")
    if expected and expected.lower() != sha256_bytes(data):
        raise HotfixError("ASAR entry integrity metadata does not match its bytes")
    blocks = integrity.get("blocks")
    block_size = integrity.get("blockSize")
    if blocks is not None or block_size is not None:
        if (
            integrity.get("algorithm") != "SHA256"
            or not isinstance(block_size, int)
            or block_size <= 0
            or not isinstance(blocks, list)
        ):
            raise HotfixError("ASAR entry block-integrity metadata is invalid")
        actual_blocks = [
            sha256_bytes(data[start : start + block_size])
            for start in range(0, len(data), block_size)
        ]
        if blocks != actual_blocks:
            raise HotfixError(
                "ASAR entry block-integrity metadata does not match its bytes"
            )
    return absolute_offset, data


def remove_source_map_bytes(entry: bytes, count: int) -> bytes:
    if count <= 0:
        return entry
    start = entry.rfind(SOURCE_MAP_PREFIX)
    if start < 0:
        raise HotfixError("Source-map footer was not found")
    footer = entry[start:]
    core = footer.rstrip(b"\r\n")
    line_ending = footer[len(core) :]
    if not core.endswith(b".map"):
        raise HotfixError("Unexpected source-map footer")
    available = len(core) - len(SOURCE_MAP_PREFIX)
    if count > available:
        raise HotfixError("Source-map footer is too short for an equal-length patch")
    return entry[:start] + SOURCE_MAP_PREFIX + b" " * (available - count) + line_ending


def patch_sort_entry(entry: bytes, *, equalize: bool = True) -> bytes:
    status, reason, variant = _classify_sort_variant(entry)
    if status != "patchable":
        raise HotfixError(
            "Sorting expression is missing, duplicated, or already patched: "
            f"{reason}"
        )
    if variant == "legacy":
        patched = entry.replace(SORT_OLD, SORT_NEW, 1)
    elif variant == "bundled":
        if entry.count(SORT_BUNDLED_INSERT_BEFORE) != 1:
            raise HotfixError("Bundled sorting insertion point is unsafe")
        patched = entry.replace(SORT_BUNDLED_BINDING, b"", 1)
        insertion = patched.find(SORT_BUNDLED_INSERT_BEFORE)
        if insertion < 0:
            raise HotfixError("Bundled sorting insertion point disappeared")
        patched = (
            patched[:insertion]
            + SORT_BUNDLED_BINDING
            + patched[insertion:]
        )
        patched = patched.replace(
            SORT_BUNDLED_CALL_OLD,
            SORT_BUNDLED_CALL_NEW,
            1,
        )
    else:
        raise HotfixError("Sorting variant is unknown")
    if equalize:
        patched = equalize_entry_length(entry, patched)
    if equalize and len(patched) != len(entry):
        raise HotfixError("Sorting entry length changed")
    validation, validation_reason = classify_sort(patched)
    if validation != "official_fixed":
        raise HotfixError(
            f"Sorting patched signature validation failed: {validation_reason}"
        )
    return patched


def choose_unused_identifiers(entry: bytes, count: int) -> list[bytes]:
    used = set(IDENTIFIER_RE.findall(entry))
    candidates = [bytes([value]) for value in b"qQzZxXvVjJkKyYwWbBAEGHINOPSU"]
    chosen = [candidate for candidate in candidates if candidate not in used]
    if len(chosen) < count:
        raise HotfixError("No safe short identifier is available for the optional label patch")
    return chosen[:count]


def _classify_legacy_label_entry(entry: bytes) -> tuple[str, str | None]:
    old_count = entry.count(LABEL_INIT_OLD)
    fixed_count = len(LABEL_FIXED_RE.findall(entry))
    if old_count == 1 and fixed_count == 0:
        return "patchable", None
    if old_count == 0 and fixed_count == 1:
        return "official_fixed", None
    return "unsupported", f"old_count={old_count}, fixed_count={fixed_count}"


def _classify_bundled_label_entry(entry: bytes) -> tuple[str, str | None]:
    start_count = entry.count(LABEL_BUNDLED_FUNCTION_START)
    end_count = entry.count(LABEL_BUNDLED_FUNCTION_END)
    start = entry.find(LABEL_BUNDLED_FUNCTION_START)
    end = entry.find(LABEL_BUNDLED_FUNCTION_END, start + 1)
    if start_count == 1 and end_count == 1 and start >= 0 and end > start:
        function_entry = entry[start:end]
        q_count = len(
            re.findall(
                rb"(?<![A-Za-z0-9_$])q(?![A-Za-z0-9_$])",
                function_entry,
            )
        )
    else:
        q_count = -1
    counts = {
        "old_count": entry.count(LABEL_BUNDLED_OLD),
        "fixed_count": entry.count(LABEL_BUNDLED_NEW),
        "provider_count": entry.count(LABEL_BUNDLED_PROVIDER),
        "provider_call_count": entry.count(b"Bo(I8n,"),
        "function_start_count": start_count,
        "function_end_count": end_count,
        "function_q_count": q_count,
        "legacy_old_count": entry.count(LABEL_INIT_OLD),
        "legacy_fixed_count": len(LABEL_FIXED_RE.findall(entry)),
    }
    common = {
        "provider_count": 1,
        "function_start_count": 1,
        "function_end_count": 1,
        "legacy_old_count": 0,
        "legacy_fixed_count": 0,
    }
    if counts == {
        **common,
        "old_count": 1,
        "fixed_count": 0,
        "provider_call_count": 1,
        "function_q_count": 0,
    }:
        return "patchable", None
    if counts == {
        **common,
        "old_count": 0,
        "fixed_count": 1,
        "provider_call_count": 2,
        "function_q_count": 2,
    }:
        return "official_fixed", None
    reason = ", ".join(f"{name}={count}" for name, count in counts.items())
    return "unsupported", reason


def _classify_label_entry(
    entry: bytes,
) -> tuple[str, str | None, str | None]:
    bundled_markers = (
        entry.count(LABEL_BUNDLED_OLD)
        + entry.count(LABEL_BUNDLED_NEW)
        + entry.count(LABEL_BUNDLED_PROVIDER)
    )
    if bundled_markers:
        status, reason = _classify_bundled_label_entry(entry)
        return status, reason, "bundled"
    status, reason = _classify_legacy_label_entry(entry)
    return status, reason, "legacy"


def patch_label_entry(entry: bytes, *, equalize: bool = True) -> bytes:
    status, reason, variant = _classify_label_entry(entry)
    if status != "patchable":
        raise HotfixError(
            "Remote-label expression is missing, duplicated, or already patched: "
            f"{reason}"
        )
    if variant == "bundled":
        patched = entry.replace(LABEL_BUNDLED_OLD, LABEL_BUNDLED_NEW, 1)
    elif variant == "legacy":
        imports = list(THREAD_CONTEXT_IMPORT_RE.finditer(entry))
        if len(imports) != 1:
            raise HotfixError("Expected exactly one thread-context-inputs import")
        match = imports[0]
        spec = match.group("spec")
        remote_alias: bytes | None = None
        for raw_part in spec.split(b","):
            part = raw_part.strip()
            if part == b"m":
                remote_alias = b"m"
                break
            alias_match = re.fullmatch(
                rb"m\s+as\s+([A-Za-z_$][A-Za-z0-9_$]*)",
                part,
            )
            if alias_match:
                remote_alias = alias_match.group(1)
                break
        needed = 1 if remote_alias is not None else 2
        names = choose_unused_identifiers(entry, needed)
        value_name = names[-1]
        if remote_alias is None:
            remote_alias = names[0]
            new_spec = spec + (b"," if spec else b"") + b"m as " + remote_alias
            new_import = match.group(0).replace(spec, new_spec, 1)
        else:
            new_import = match.group(0)
        new_init = (
            value_name
            + b"=o("
            + remote_alias
            + b"),p=r??"
            + value_name
            + b".find(e=>e.id===n)?.label??null,m=o(c),g=n;"
        )
        patched = entry[: match.start()] + new_import + entry[match.end() :]
        if patched.count(LABEL_INIT_OLD) != 1:
            raise HotfixError("Remote-label initialization moved unexpectedly")
        patched = patched.replace(LABEL_INIT_OLD, new_init, 1)
    else:
        raise HotfixError("Remote-label variant is unknown")
    if equalize:
        patched = equalize_entry_length(entry, patched)
    if equalize and len(patched) != len(entry):
        raise HotfixError("Remote-label entry length changed")
    validation, validation_reason, _ = _classify_label_entry(patched)
    if validation != "official_fixed":
        raise HotfixError(
            f"Remote-label patched expression did not validate: {validation_reason}"
        )
    return patched


def add_source_map_padding(entry: bytes, count: int) -> bytes:
    if count <= 0:
        return entry
    start = entry.rfind(SOURCE_MAP_PREFIX)
    if start < 0:
        raise HotfixError("Source-map footer was not found")
    footer = entry[start:]
    core = footer.rstrip(b"\r\n")
    line_ending = footer[len(core) :]
    if not core.endswith(b".map"):
        raise HotfixError("Unexpected source-map footer")
    return entry[:start] + core + (b" " * count) + line_ending


def shrink_source_map_footer(entry: bytes, count: int) -> bytes:
    if count <= 0:
        return entry
    start = entry.rfind(SOURCE_MAP_PREFIX)
    if start < 0:
        raise HotfixError("Source-map footer was not found")
    footer = entry[start:]
    core = footer.rstrip(b"\r\n")
    line_ending = footer[len(core) :]
    if not core.endswith(b".map"):
        raise HotfixError("Unexpected source-map footer")
    available = len(core) - 2
    if count > available:
        raise HotfixError("Source-map footer is too short for an equal-length patch")
    remaining = len(core) - count
    return entry[:start] + b"//" + (b" " * (remaining - 2)) + line_ending


def equalize_entry_length(original: bytes, patched: bytes) -> bytes:
    delta = len(patched) - len(original)
    if delta > 0:
        patched = shrink_source_map_footer(patched, delta)
    elif delta < 0:
        patched = add_source_map_padding(patched, -delta)
    if len(patched) != len(original):
        raise HotfixError("Patched entry length changed")
    return patched


def equalize_current_entry_length(original: bytes, patched: bytes) -> bytes:
    """Preserve the current entry length using only its source-map footer."""
    return equalize_entry_length(original, patched)


def _classify_current_replacements(
    entry: bytes,
    replacements: tuple[tuple[bytes, bytes], ...],
) -> tuple[str, str | None]:
    counts: list[str] = []
    old_only = True
    new_only = True
    for index, (old, fixed) in enumerate(replacements):
        old_count = entry.count(old)
        fixed_count = entry.count(fixed)
        counts.append(f"{index}:old={old_count},fixed={fixed_count}")
        old_only = old_only and old_count == 1 and fixed_count == 0
        # Some insertion-style fixes deliberately retain the complete source
        # signature as a prefix. In that case the fixed form contains one old
        # signature by construction; do not misclassify it as still patchable.
        new_only = (
            new_only
            and old_count == fixed.count(old)
            and fixed_count == 1
        )
    if old_only:
        return "patchable", None
    if new_only:
        return "official_fixed", None
    return "unsupported", "; ".join(counts)


CURRENT_FEATURE_REPLACEMENTS: dict[str, tuple[tuple[bytes, bytes], ...]] = {
    "project_sorting": (
        (CURRENT_PROJECT_GROUP_OLD, CURRENT_PROJECT_GROUP_NEW),
        (CURRENT_PROJECT_GROUP_CALL_OLD, CURRENT_PROJECT_GROUP_CALL_NEW),
    ),
    "active_priority_sort": (
        (CURRENT_PRIORITY_SORT_OLD, CURRENT_PRIORITY_SORT_NEW),
        (CURRENT_GROUP_STATUS_OLD, CURRENT_GROUP_STATUS_NEW),
        (CURRENT_ACTIVE_STATUS_FALLBACK_OLD, CURRENT_ACTIVE_STATUS_FALLBACK_NEW),
        (CURRENT_PRIORITY_FILTER_SORT_OLD, CURRENT_PRIORITY_FILTER_SORT_NEW),
        (CURRENT_PRIORITY_FILTER_REFRESH_OLD, CURRENT_PRIORITY_FILTER_REFRESH_NEW),
        (CURRENT_UNKNOWN_TURN_STARTED_OLD, CURRENT_UNKNOWN_TURN_STARTED_NEW),
        (CURRENT_UNKNOWN_TURN_COMPLETED_OLD, CURRENT_UNKNOWN_TURN_COMPLETED_NEW),
    ),
    "automation_priority_gate": (
        (
            CURRENT_AUTOMATION_IDENTITY_DEPENDENCY_OLD,
            CURRENT_AUTOMATION_IDENTITY_DEPENDENCY_NEW,
        ),
        (CURRENT_AUTOMATION_IDENTITY_OLD, CURRENT_AUTOMATION_IDENTITY_NEW),
        (CURRENT_AUTOMATION_PRIORITY_GATE_OLD, CURRENT_AUTOMATION_PRIORITY_GATE_NEW),
    ),
    "pinned_priority_sync": (
        (CURRENT_PINNED_ACTION_OLD, CURRENT_PINNED_ACTION_NEW),
        (CURRENT_GLOBAL_CHAT_SORT_OLD, CURRENT_GLOBAL_CHAT_SORT_NEW),
        (CURRENT_GLOBAL_PROJECT_SORT_OLD, CURRENT_GLOBAL_PROJECT_SORT_NEW),
        (CURRENT_PINNED_DEFAULT_OLD, CURRENT_PINNED_DEFAULT_NEW),
    ),
    "new_chat_file_drop": ((CURRENT_DROP_OLD, CURRENT_DROP_NEW),),
    "remote_project_label": (
        (CURRENT_REMOTE_PROJECT_LABEL_OLD, CURRENT_REMOTE_PROJECT_LABEL_NEW),
        (
            CURRENT_REMOTE_PROJECT_LABEL_HELPER_OLD,
            CURRENT_REMOTE_PROJECT_LABEL_HELPER_NEW,
        ),
        (
            CURRENT_REMOTE_PROJECT_LABEL_RENDER_OLD,
            CURRENT_REMOTE_PROJECT_LABEL_RENDER_NEW,
        ),
        (
            CURRENT_REMOTE_PROJECT_LABEL_SEARCH_OLD,
            CURRENT_REMOTE_PROJECT_LABEL_SEARCH_NEW,
        ),
        (
            CURRENT_REMOTE_PROJECT_LABEL_THREAD_MAPS_OLD,
            CURRENT_REMOTE_PROJECT_LABEL_THREAD_MAPS_NEW,
        ),
        (
            CURRENT_REMOTE_PROJECT_LABEL_SIDEBAR_OLD,
            CURRENT_REMOTE_PROJECT_LABEL_SIDEBAR_NEW,
        ),
        (
            CURRENT_REMOTE_PROJECT_LABEL_LIST_ARIA_OLD,
            CURRENT_REMOTE_PROJECT_LABEL_LIST_ARIA_NEW,
        ),
        (
            CURRENT_REMOTE_PROJECT_LABEL_MENU_OLD,
            CURRENT_REMOTE_PROJECT_LABEL_MENU_NEW,
        ),
    ),
    "work_remote_project_picker": (
        (CURRENT_WORK_PROJECT_SOURCE_OLD, CURRENT_WORK_PROJECT_SOURCE_NEW),
        (CURRENT_WORK_PROJECT_SELECT_OLD, CURRENT_WORK_PROJECT_SELECT_NEW),
        (CURRENT_WORK_PROJECT_RESTORE_OLD, CURRENT_WORK_PROJECT_RESTORE_NEW),
        (CURRENT_WORK_PROJECT_ICON_OLD, CURRENT_WORK_PROJECT_ICON_NEW),
    ),
}

# 26.730 moved the affected minified code into a new app-initial bundle. Keep
# the exact, hash-gated signatures in a companion module so the rebase remains
# reviewable without weakening any of the builder's fail-closed checks.
_CURRENT_PROFILE_PATH = Path(__file__).with_name("hotfix_profile_26810.py")
_CURRENT_PROFILE_SPEC = importlib.util.spec_from_file_location(
    "hotfix_profile_26730", _CURRENT_PROFILE_PATH
)
if _CURRENT_PROFILE_SPEC is None or _CURRENT_PROFILE_SPEC.loader is None:
    raise RuntimeError(f"Unable to load current frontend profile: {_CURRENT_PROFILE_PATH}")
_CURRENT_PROFILE_MODULE = importlib.util.module_from_spec(_CURRENT_PROFILE_SPEC)
_CURRENT_PROFILE_SPEC.loader.exec_module(_CURRENT_PROFILE_MODULE)
_CURRENT_PROFILE_PAIRS = _CURRENT_PROFILE_MODULE.PAIRS
CURRENT_INJECTED_GLOBAL_IDENTIFIER_COUNTS = getattr(
    _CURRENT_PROFILE_MODULE, "INJECTED_GLOBAL_IDENTIFIER_COUNTS", {}
)
CURRENT_PROTECTED_OFFICIAL_SIGNATURES = tuple(
    getattr(_CURRENT_PROFILE_MODULE, "PROTECTED_OFFICIAL_SIGNATURES", ())
)
# The current profile carries only exact, hash-gated changes.  A feature may be
# classified as official only when it is in this evidence-backed allowlist; an
# omitted patch is never silently accepted as an official implementation.
CURRENT_FEATURE_REPLACEMENTS = dict(_CURRENT_PROFILE_PAIRS)
CURRENT_PROFILE_FEATURES = tuple(CURRENT_FEATURE_REPLACEMENTS)


def current_replacement_set_sha256() -> str:
    """Stable identity for the exact, reviewed replacement set."""
    digest = hashlib.sha256()
    for name in sorted(CURRENT_FEATURE_REPLACEMENTS):
        digest.update(name.encode("utf-8") + b"\0")
        for old, new in CURRENT_FEATURE_REPLACEMENTS[name]:
            digest.update(old + b"\0" + new + b"\0")
    return digest.hexdigest()


CURRENT_REPLACEMENT_SET_SHA256 = current_replacement_set_sha256()
CURRENT_OFFICIAL_FEATURES = frozenset({
    # Ordinary chat, project, and pinned-list sorting remain official.  The
    # independent Priority activity view has its own profile signatures.
    "project_sorting",
    "active_priority_sort",
    "pinned_priority_sync",
    "automation_priority_gate",
    "new_chat_file_drop",
    "remote_project_label",
    "work_remote_project_picker",
    "resume_history_on_demand",
    "paginated_tail_retention",
    "windows_watch_path_normalization",
    "archived_heartbeat_terminal_guard",
    "idle_history_eviction",
})


_PROFILE_26820_ASAR_SHA256 = (
    "a872ead5cf8f651185fcbc972247ce0d7884fddedd1f0118a044f0801e33a82d"
)
_PROFILE_26818_ASAR_SHA256 = (
    "1eb70e2aa26f2408a3e65817f0974e137b1a7ff6e52e43a184154bd4db2074d1"
)
_PROFILE_26818_5229_ASAR_SHA256 = (
    "c5d839bc9b122b7ef2a2f0f45186b3e5895923de5b6cef5253c936fe670c0479"
)
_PROFILE_26818_8289_ASAR_SHA256 = (
    "e2f04d6aa921d07981b42368df0a28a8bebe8cd21375d4a1f9286757b51c1313"
)
_PROFILE_26825_5331_ASAR_SHA256 = (
    "178b65229452b17b0203ab41d5ceafedccd770c9bd42d239a6d048d27d80252b"
)
_PROFILE_26825_6671_ASAR_SHA256 = (
    "86e791e0eb330a1507057d30e450878f7c958e56e04e718f101ba80549e9baf2"
)
_PROFILE_26831_2377_ASAR_SHA256 = (
    "37e442e444194cebff47eb190b2c0ccd99332498a361545bbf823c49ccf11cd3"
)
_PROFILE_26901_6511_ASAR_SHA256 = (
    "e75bae2b8a02f174c7ceeed6d631aaff355e44f8af5c798fa3628089f11d659e"
)


class _FrontendProfileSpec:
    """Per-package frontend patch identity.

    Each Microsoft Store package version has its own exact, hash-gated
    replacement set, its own allowlist of behaviours the official bundle now
    ships, and its own injected-global and protected-signature constraints.
    """

    def __init__(
        self,
        pairs: dict[str, tuple[tuple[bytes, bytes], ...]],
        official_features: Iterable[str],
        injected_global_identifier_counts: dict[str, dict[str, int]],
        protected_official_signatures: tuple[bytes, ...],
        official_feature_signatures: dict[str, tuple[bytes, ...]] | None = None,
    ) -> None:
        self.pairs = dict(pairs)
        self.features = tuple(self.pairs)
        self.official_features = frozenset(official_features)
        self.injected_global_identifier_counts = dict(
            injected_global_identifier_counts
        )
        self.protected_official_signatures = tuple(protected_official_signatures)
        self.official_feature_signatures = dict(official_feature_signatures or {})
        self.replacement_set_sha256 = _replacement_set_sha256(self.pairs)


def _replacement_set_sha256(
    pairs: dict[str, tuple[tuple[bytes, bytes], ...]],
) -> str:
    """Stable identity for one exact, reviewed replacement set."""
    digest = hashlib.sha256()
    for name in sorted(pairs):
        digest.update(name.encode("utf-8") + b"\0")
        for old, new in pairs[name]:
            digest.update(old + b"\0" + new + b"\0")
    return digest.hexdigest()


def run_frontend_contract_validator(source_asar: Path, portable_asar: Path) -> dict[str, Any]:
    validator = Path(__file__).with_name("frontend_feature_contracts.py")
    if not validator.is_file():
        raise HotfixError("Frontend feature-contract validator is missing")
    completed = subprocess.run(
        [
            sys.executable,
            str(validator),
            "--source-asar",
            str(source_asar),
            "--portable-asar",
            str(portable_asar),
        ],
        text=True,
        capture_output=True,
        timeout=60,
    )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise HotfixError("Frontend feature-contract validator returned invalid JSON") from exc
    if (
        completed.returncode != 0
        or result.get("schema_version") != 2
        or result.get("validator_version") != FRONTEND_CONTRACT_VALIDATOR_VERSION
        or result.get("status") != "bundle_qualified_only"
        or result.get("blocked_feature_ids")
    ):
        raise HotfixError(
            "Frontend feature-contract validation failed: "
            + str(result.get("error") or result.get("blocked_feature_ids") or completed.stderr)
        )
    return result


_PROFILE_26820_PATH = Path(__file__).with_name("hotfix_profile_26820.py")
_PROFILE_26820_SPEC_LOAD = importlib.util.spec_from_file_location(
    "hotfix_profile_26820", _PROFILE_26820_PATH
)
if _PROFILE_26820_SPEC_LOAD is None or _PROFILE_26820_SPEC_LOAD.loader is None:
    raise RuntimeError(
        f"Unable to load 26.814.5517.0 frontend profile: {_PROFILE_26820_PATH}"
    )
_PROFILE_26820_MODULE = importlib.util.module_from_spec(_PROFILE_26820_SPEC_LOAD)
_PROFILE_26820_SPEC_LOAD.loader.exec_module(_PROFILE_26820_MODULE)
_PROFILE_26820_PAIRS = _PROFILE_26820_MODULE.PAIRS
_PROFILE_26820_INJECTED_GLOBAL_IDENTIFIER_COUNTS = getattr(
    _PROFILE_26820_MODULE, "INJECTED_GLOBAL_IDENTIFIER_COUNTS", {}
)
_PROFILE_26820_PROTECTED_OFFICIAL_SIGNATURES = tuple(
    getattr(_PROFILE_26820_MODULE, "PROTECTED_OFFICIAL_SIGNATURES", ())
)

_PROFILE_26818_PATH = Path(__file__).with_name("hotfix_profile_26818.py")
_PROFILE_26818_SPEC_LOAD = importlib.util.spec_from_file_location(
    "hotfix_profile_26818", _PROFILE_26818_PATH
)
if _PROFILE_26818_SPEC_LOAD is None or _PROFILE_26818_SPEC_LOAD.loader is None:
    raise RuntimeError(
        f"Unable to load 26.818.3698.0 frontend profile: {_PROFILE_26818_PATH}"
    )
_PROFILE_26818_MODULE = importlib.util.module_from_spec(_PROFILE_26818_SPEC_LOAD)
_PROFILE_26818_SPEC_LOAD.loader.exec_module(_PROFILE_26818_MODULE)
_PROFILE_26818_PAIRS = _PROFILE_26818_MODULE.PAIRS
_PROFILE_26818_INJECTED_GLOBAL_IDENTIFIER_COUNTS = getattr(
    _PROFILE_26818_MODULE, "INJECTED_GLOBAL_IDENTIFIER_COUNTS", {}
)
_PROFILE_26818_PROTECTED_OFFICIAL_SIGNATURES = tuple(
    getattr(_PROFILE_26818_MODULE, "PROTECTED_OFFICIAL_SIGNATURES", ())
)

_PROFILE_26818_5229_PATH = Path(__file__).with_name("hotfix_profile_26818_5229.py")
_PROFILE_26818_5229_SPEC_LOAD = importlib.util.spec_from_file_location(
    "hotfix_profile_26818_5229", _PROFILE_26818_5229_PATH
)
if (
    _PROFILE_26818_5229_SPEC_LOAD is None
    or _PROFILE_26818_5229_SPEC_LOAD.loader is None
):
    raise RuntimeError(
        "Unable to load 26.818.5229.0 frontend profile: "
        f"{_PROFILE_26818_5229_PATH}"
    )
_PROFILE_26818_5229_MODULE = importlib.util.module_from_spec(
    _PROFILE_26818_5229_SPEC_LOAD
)
_PROFILE_26818_5229_SPEC_LOAD.loader.exec_module(_PROFILE_26818_5229_MODULE)
_PROFILE_26818_5229_PAIRS = _PROFILE_26818_5229_MODULE.PAIRS
_PROFILE_26818_5229_INJECTED_GLOBAL_IDENTIFIER_COUNTS = getattr(
    _PROFILE_26818_5229_MODULE, "INJECTED_GLOBAL_IDENTIFIER_COUNTS", {}
)
_PROFILE_26818_5229_PROTECTED_OFFICIAL_SIGNATURES = tuple(
    getattr(_PROFILE_26818_5229_MODULE, "PROTECTED_OFFICIAL_SIGNATURES", ())
)

_PROFILE_26818_8289_PATH = Path(__file__).with_name("hotfix_profile_26818_8289.py")
_PROFILE_26818_8289_SPEC_LOAD = importlib.util.spec_from_file_location(
    "hotfix_profile_26818_8289", _PROFILE_26818_8289_PATH
)
if (
    _PROFILE_26818_8289_SPEC_LOAD is None
    or _PROFILE_26818_8289_SPEC_LOAD.loader is None
):
    raise RuntimeError(
        "Unable to load 26.818.8289.0 frontend profile: "
        f"{_PROFILE_26818_8289_PATH}"
    )
_PROFILE_26818_8289_MODULE = importlib.util.module_from_spec(
    _PROFILE_26818_8289_SPEC_LOAD
)
_PROFILE_26818_8289_SPEC_LOAD.loader.exec_module(_PROFILE_26818_8289_MODULE)
_PROFILE_26818_8289_PAIRS = _PROFILE_26818_8289_MODULE.PAIRS
_PROFILE_26818_8289_INJECTED_GLOBAL_IDENTIFIER_COUNTS = getattr(
    _PROFILE_26818_8289_MODULE, "INJECTED_GLOBAL_IDENTIFIER_COUNTS", {}
)
_PROFILE_26818_8289_PROTECTED_OFFICIAL_SIGNATURES = tuple(
    getattr(_PROFILE_26818_8289_MODULE, "PROTECTED_OFFICIAL_SIGNATURES", ())
)

_PROFILE_26825_5331_PATH = Path(__file__).with_name("hotfix_profile_26825_5331.py")
_PROFILE_26825_5331_SPEC_LOAD = importlib.util.spec_from_file_location(
    "hotfix_profile_26825_5331", _PROFILE_26825_5331_PATH
)
if (
    _PROFILE_26825_5331_SPEC_LOAD is None
    or _PROFILE_26825_5331_SPEC_LOAD.loader is None
):
    raise RuntimeError(
        "Unable to load 26.825.5331.0 frontend profile: "
        f"{_PROFILE_26825_5331_PATH}"
    )
_PROFILE_26825_5331_MODULE = importlib.util.module_from_spec(
    _PROFILE_26825_5331_SPEC_LOAD
)
_PROFILE_26825_5331_SPEC_LOAD.loader.exec_module(_PROFILE_26825_5331_MODULE)
_PROFILE_26825_5331_PAIRS = _PROFILE_26825_5331_MODULE.PAIRS
_PROFILE_26825_5331_INJECTED_GLOBAL_IDENTIFIER_COUNTS = getattr(
    _PROFILE_26825_5331_MODULE, "INJECTED_GLOBAL_IDENTIFIER_COUNTS", {}
)
_PROFILE_26825_5331_PROTECTED_OFFICIAL_SIGNATURES = tuple(
    getattr(_PROFILE_26825_5331_MODULE, "PROTECTED_OFFICIAL_SIGNATURES", ())
)

_PROFILE_26825_6671_PATH = Path(__file__).with_name("hotfix_profile_26825_6671.py")
_PROFILE_26825_6671_SPEC_LOAD = importlib.util.spec_from_file_location(
    "hotfix_profile_26825_6671", _PROFILE_26825_6671_PATH
)
if (
    _PROFILE_26825_6671_SPEC_LOAD is None
    or _PROFILE_26825_6671_SPEC_LOAD.loader is None
):
    raise RuntimeError(
        "Unable to load 26.825.6671.0 frontend profile: "
        f"{_PROFILE_26825_6671_PATH}"
    )
_PROFILE_26825_6671_MODULE = importlib.util.module_from_spec(
    _PROFILE_26825_6671_SPEC_LOAD
)
_PROFILE_26825_6671_SPEC_LOAD.loader.exec_module(_PROFILE_26825_6671_MODULE)
_PROFILE_26825_6671_PAIRS = _PROFILE_26825_6671_MODULE.PAIRS
_PROFILE_26825_6671_INJECTED_GLOBAL_IDENTIFIER_COUNTS = getattr(
    _PROFILE_26825_6671_MODULE, "INJECTED_GLOBAL_IDENTIFIER_COUNTS", {}
)
_PROFILE_26825_6671_PROTECTED_OFFICIAL_SIGNATURES = tuple(
    getattr(_PROFILE_26825_6671_MODULE, "PROTECTED_OFFICIAL_SIGNATURES", ())
)
_PROFILE_26825_6671_OFFICIAL_FEATURE_SIGNATURES = dict(
    getattr(_PROFILE_26825_6671_MODULE, "OFFICIAL_FEATURE_SIGNATURES", {})
)
_PROFILE_26825_6671_ATTESTATION_LOG_BRIDGE_IDENTIFIER = str(
    getattr(_PROFILE_26825_6671_MODULE, "ATTESTATION_LOG_BRIDGE_IDENTIFIER", "")
)
_PROFILE_26825_6671_ATTESTATION_LOG_BRIDGE_SIGNATURES = tuple(
    getattr(_PROFILE_26825_6671_MODULE, "ATTESTATION_LOG_BRIDGE_SIGNATURES", ())
)

_PROFILE_26831_2377_PATH = Path(__file__).with_name("hotfix_profile_26831_2377.py")
_PROFILE_26831_2377_SPEC_LOAD = importlib.util.spec_from_file_location(
    "hotfix_profile_26831_2377", _PROFILE_26831_2377_PATH
)
if _PROFILE_26831_2377_SPEC_LOAD is None or _PROFILE_26831_2377_SPEC_LOAD.loader is None:
    raise RuntimeError("Unable to load 26.831.2377.0 frontend profile")
_PROFILE_26831_2377_MODULE = importlib.util.module_from_spec(
    _PROFILE_26831_2377_SPEC_LOAD
)
_PROFILE_26831_2377_SPEC_LOAD.loader.exec_module(_PROFILE_26831_2377_MODULE)
_PROFILE_26831_2377_PAIRS = dict(_PROFILE_26831_2377_MODULE.PAIRS)
_PROFILE_26831_2377_SECONDARY_PAIRS = dict(
    getattr(_PROFILE_26831_2377_MODULE, "SECONDARY_PAIRS", {})
)
_PROFILE_26831_2377_OFFICIAL_FEATURE_SIGNATURES = dict(
    getattr(_PROFILE_26831_2377_MODULE, "OFFICIAL_FEATURE_SIGNATURES", {})
)
_PROFILE_26831_2377_SECONDARY_OFFICIAL_FEATURE_SIGNATURES = dict(
    getattr(
        _PROFILE_26831_2377_MODULE,
        "SECONDARY_OFFICIAL_FEATURE_SIGNATURES",
        {},
    )
)
_PROFILE_26831_2377_ATTESTATION_LOG_BRIDGE_IDENTIFIER = str(
    getattr(_PROFILE_26831_2377_MODULE, "ATTESTATION_LOG_BRIDGE_IDENTIFIER", "")
)
_PROFILE_26831_2377_ATTESTATION_LOG_BRIDGE_SIGNATURES = tuple(
    getattr(_PROFILE_26831_2377_MODULE, "ATTESTATION_LOG_BRIDGE_SIGNATURES", ())
)

_PROFILE_26901_6511_PATH = Path(__file__).with_name("hotfix_profile_26901_6511.py")
_PROFILE_26901_6511_SPEC_LOAD = importlib.util.spec_from_file_location(
    "hotfix_profile_26901_6511", _PROFILE_26901_6511_PATH
)
if _PROFILE_26901_6511_SPEC_LOAD is None or _PROFILE_26901_6511_SPEC_LOAD.loader is None:
    raise RuntimeError("Unable to load 26.901.6511.0 frontend profile")
_PROFILE_26901_6511_MODULE = importlib.util.module_from_spec(
    _PROFILE_26901_6511_SPEC_LOAD
)
_PROFILE_26901_6511_SPEC_LOAD.loader.exec_module(_PROFILE_26901_6511_MODULE)
_PROFILE_26901_6511_PAIRS = dict(_PROFILE_26901_6511_MODULE.PAIRS)
_PROFILE_26901_6511_SECONDARY_PAIRS = dict(
    getattr(_PROFILE_26901_6511_MODULE, "SECONDARY_PAIRS", {})
)
_PROFILE_26901_6511_OFFICIAL_FEATURE_SIGNATURES = dict(
    getattr(_PROFILE_26901_6511_MODULE, "OFFICIAL_FEATURE_SIGNATURES", {})
)
_PROFILE_26901_6511_SECONDARY_OFFICIAL_FEATURE_SIGNATURES = dict(
    getattr(_PROFILE_26901_6511_MODULE, "SECONDARY_OFFICIAL_FEATURE_SIGNATURES", {})
)
_PROFILE_26901_6511_ATTESTATION_LOG_BRIDGE_IDENTIFIER = str(
    getattr(_PROFILE_26901_6511_MODULE, "ATTESTATION_LOG_BRIDGE_IDENTIFIER", "")
)
_PROFILE_26901_6511_ATTESTATION_LOG_BRIDGE_SIGNATURES = tuple(
    getattr(_PROFILE_26901_6511_MODULE, "ATTESTATION_LOG_BRIDGE_SIGNATURES", ())
)
for _profile in FRONTEND_PROFILES:
    if _profile.get("package_version") == "26.901.6511.0":
        _profile["attestation_log_bridge_identifier"] = (
            _PROFILE_26901_6511_ATTESTATION_LOG_BRIDGE_IDENTIFIER
        )
        _profile["attestation_log_bridge_signatures"] = (
            _PROFILE_26901_6511_ATTESTATION_LOG_BRIDGE_SIGNATURES
        )

_PROFILE_26903_9818_PATH = Path(__file__).with_name("hotfix_profile_26903_9818.py")
_PROFILE_26903_9818_SPEC_LOAD = importlib.util.spec_from_file_location(
    "hotfix_profile_26903_9818", _PROFILE_26903_9818_PATH
)
if _PROFILE_26903_9818_SPEC_LOAD is None or _PROFILE_26903_9818_SPEC_LOAD.loader is None:
    raise RuntimeError("Unable to load 26.903.9818.0 frontend profile")
_PROFILE_26903_9818_MODULE = importlib.util.module_from_spec(
    _PROFILE_26903_9818_SPEC_LOAD
)
_PROFILE_26903_9818_SPEC_LOAD.loader.exec_module(_PROFILE_26903_9818_MODULE)
_PROFILE_26903_9818_ASAR_SHA256 = str(
    next(
        profile["asar_source_sha256"]
        for profile in FRONTEND_PROFILES
        if profile.get("package_version") == "26.903.9818.0"
    )
)
_PROFILE_26903_9818_PAIRS = dict(_PROFILE_26903_9818_MODULE.PAIRS)
_PROFILE_26903_9818_SECONDARY_PAIRS = dict(
    getattr(_PROFILE_26903_9818_MODULE, "SECONDARY_PAIRS", {})
)
_PROFILE_26903_9818_OFFICIAL_FEATURE_SIGNATURES = dict(
    getattr(_PROFILE_26903_9818_MODULE, "OFFICIAL_FEATURE_SIGNATURES", {})
)
_PROFILE_26903_9818_SECONDARY_OFFICIAL_FEATURE_SIGNATURES = dict(
    getattr(_PROFILE_26903_9818_MODULE, "SECONDARY_OFFICIAL_FEATURE_SIGNATURES", {})
)
_PROFILE_26903_9818_ATTESTATION_LOG_BRIDGE_IDENTIFIER = str(
    getattr(_PROFILE_26903_9818_MODULE, "ATTESTATION_LOG_BRIDGE_IDENTIFIER", "")
)
_PROFILE_26903_9818_ATTESTATION_LOG_BRIDGE_SIGNATURES = tuple(
    getattr(_PROFILE_26903_9818_MODULE, "ATTESTATION_LOG_BRIDGE_SIGNATURES", ())
)
for _profile in FRONTEND_PROFILES:
    if _profile.get("package_version") == "26.903.9818.0":
        _profile["attestation_log_bridge_identifier"] = (
            _PROFILE_26903_9818_ATTESTATION_LOG_BRIDGE_IDENTIFIER
        )
        _profile["attestation_log_bridge_signatures"] = (
            _PROFILE_26903_9818_ATTESTATION_LOG_BRIDGE_SIGNATURES
        )

_PROFILE_26908_4834_PATH = Path(__file__).with_name("hotfix_profile_26908_4834.py")
_PROFILE_26908_4834_SPEC_LOAD = importlib.util.spec_from_file_location(
    "hotfix_profile_26908_4834", _PROFILE_26908_4834_PATH
)
if _PROFILE_26908_4834_SPEC_LOAD is None or _PROFILE_26908_4834_SPEC_LOAD.loader is None:
    raise RuntimeError("Unable to load 26.908.4834.0 frontend profile")
_PROFILE_26908_4834_MODULE = importlib.util.module_from_spec(
    _PROFILE_26908_4834_SPEC_LOAD
)
_PROFILE_26908_4834_SPEC_LOAD.loader.exec_module(_PROFILE_26908_4834_MODULE)
_PROFILE_26908_4834_ASAR_SHA256 = str(
    FRONTEND_PROFILES[0]["asar_source_sha256"]
)
_PROFILE_26908_4834_PAIRS = dict(_PROFILE_26908_4834_MODULE.PAIRS)
_PROFILE_26908_4834_SECONDARY_PAIRS = dict(
    getattr(_PROFILE_26908_4834_MODULE, "SECONDARY_PAIRS", {})
)
_PROFILE_26908_4834_OFFICIAL_FEATURE_SIGNATURES = dict(
    getattr(_PROFILE_26908_4834_MODULE, "OFFICIAL_FEATURE_SIGNATURES", {})
)
_PROFILE_26908_4834_SECONDARY_OFFICIAL_FEATURE_SIGNATURES = dict(
    getattr(_PROFILE_26908_4834_MODULE, "SECONDARY_OFFICIAL_FEATURE_SIGNATURES", {})
)
_PROFILE_26908_4834_ATTESTATION_LOG_BRIDGE_IDENTIFIER = str(
    getattr(_PROFILE_26908_4834_MODULE, "ATTESTATION_LOG_BRIDGE_IDENTIFIER", "")
)
_PROFILE_26908_4834_ATTESTATION_LOG_BRIDGE_SIGNATURES = tuple(
    getattr(_PROFILE_26908_4834_MODULE, "ATTESTATION_LOG_BRIDGE_SIGNATURES", ())
)
for _profile in FRONTEND_PROFILES:
    if _profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}:
        _profile["attestation_log_bridge_identifier"] = (
            _PROFILE_26908_4834_ATTESTATION_LOG_BRIDGE_IDENTIFIER
        )
        _profile["attestation_log_bridge_signatures"] = (
            _PROFILE_26908_4834_ATTESTATION_LOG_BRIDGE_SIGNATURES
        )

# 26.814.5517.0 ships the priority click-hold, hold-membership and
# identity-migration behaviours as well as the Work-mode remote picker. The
# profile re-patches Priority recency/live/pinned sorting, project subtitle,
# plan-pending yellow and the remote/SSH label.
_PROFILE_26820_OFFICIAL_FEATURES = frozenset({
    "project_sorting",
    "active_priority_sort",
    "pinned_priority_sync",
    "new_chat_file_drop",
    "priority_filter_hold_membership",
    "priority_click_hold",
    "work_remote_project_picker",
    "resume_history_on_demand",
    "paginated_tail_retention",
    "windows_watch_path_normalization",
    "archived_heartbeat_terminal_guard",
    "idle_history_eviction",
})

_PROFILE_26825_5331_OFFICIAL_FEATURES = frozenset({
    "project_sorting",
    "active_priority_sort",
    "pinned_priority_sync",
    "new_chat_file_drop",
    "priority_filter_hold_membership",
    "priority_click_hold",
    "priority_identity_migration",
    "work_remote_project_picker",
    "resume_history_on_demand",
    "paginated_tail_retention",
    "windows_watch_path_normalization",
    "archived_heartbeat_terminal_guard",
    "idle_history_eviction",
})

_SPEC_26810 = _FrontendProfileSpec(
    pairs=dict(_CURRENT_PROFILE_PAIRS),
    official_features=CURRENT_OFFICIAL_FEATURES,
    injected_global_identifier_counts=CURRENT_INJECTED_GLOBAL_IDENTIFIER_COUNTS,
    protected_official_signatures=CURRENT_PROTECTED_OFFICIAL_SIGNATURES,
)
_SPEC_26820 = _FrontendProfileSpec(
    pairs=dict(_PROFILE_26820_PAIRS),
    official_features=_PROFILE_26820_OFFICIAL_FEATURES,
    injected_global_identifier_counts=_PROFILE_26820_INJECTED_GLOBAL_IDENTIFIER_COUNTS,
    protected_official_signatures=_PROFILE_26820_PROTECTED_OFFICIAL_SIGNATURES,
)
_SPEC_26818 = _FrontendProfileSpec(
    pairs=dict(_PROFILE_26818_PAIRS),
    official_features=_PROFILE_26820_OFFICIAL_FEATURES,
    injected_global_identifier_counts=_PROFILE_26818_INJECTED_GLOBAL_IDENTIFIER_COUNTS,
    protected_official_signatures=_PROFILE_26818_PROTECTED_OFFICIAL_SIGNATURES,
)
_SPEC_26818_5229 = _FrontendProfileSpec(
    pairs=dict(_PROFILE_26818_5229_PAIRS),
    official_features=_PROFILE_26820_OFFICIAL_FEATURES,
    injected_global_identifier_counts=_PROFILE_26818_5229_INJECTED_GLOBAL_IDENTIFIER_COUNTS,
    protected_official_signatures=_PROFILE_26818_5229_PROTECTED_OFFICIAL_SIGNATURES,
)
_SPEC_26818_8289 = _FrontendProfileSpec(
    pairs=dict(_PROFILE_26818_8289_PAIRS),
    official_features=_PROFILE_26820_OFFICIAL_FEATURES,
    injected_global_identifier_counts=_PROFILE_26818_8289_INJECTED_GLOBAL_IDENTIFIER_COUNTS,
    protected_official_signatures=_PROFILE_26818_8289_PROTECTED_OFFICIAL_SIGNATURES,
)
_SPEC_26825_5331 = _FrontendProfileSpec(
    pairs=dict(_PROFILE_26825_5331_PAIRS),
    official_features=_PROFILE_26825_5331_OFFICIAL_FEATURES,
    injected_global_identifier_counts=_PROFILE_26825_5331_INJECTED_GLOBAL_IDENTIFIER_COUNTS,
    protected_official_signatures=_PROFILE_26825_5331_PROTECTED_OFFICIAL_SIGNATURES,
)
_SPEC_26825_6671 = _FrontendProfileSpec(
    pairs=dict(_PROFILE_26825_6671_PAIRS),
    official_features=frozenset(_PROFILE_26825_6671_OFFICIAL_FEATURE_SIGNATURES),
    injected_global_identifier_counts=_PROFILE_26825_6671_INJECTED_GLOBAL_IDENTIFIER_COUNTS,
    protected_official_signatures=_PROFILE_26825_6671_PROTECTED_OFFICIAL_SIGNATURES,
    official_feature_signatures=_PROFILE_26825_6671_OFFICIAL_FEATURE_SIGNATURES,
)
_SPEC_26831_2377 = _FrontendProfileSpec(
    pairs=_PROFILE_26831_2377_PAIRS,
    official_features=frozenset(_PROFILE_26831_2377_OFFICIAL_FEATURE_SIGNATURES),
    injected_global_identifier_counts={},
    protected_official_signatures=tuple(),
    official_feature_signatures=_PROFILE_26831_2377_OFFICIAL_FEATURE_SIGNATURES,
)
_SPEC_26908_4834 = _FrontendProfileSpec(
    pairs=_PROFILE_26908_4834_PAIRS,
    official_features=frozenset(_PROFILE_26908_4834_OFFICIAL_FEATURE_SIGNATURES),
    injected_global_identifier_counts={},
    protected_official_signatures=tuple(),
    official_feature_signatures=_PROFILE_26908_4834_OFFICIAL_FEATURE_SIGNATURES,
)
_SPEC_26903_9818 = _FrontendProfileSpec(
    pairs=_PROFILE_26903_9818_PAIRS,
    official_features=frozenset(_PROFILE_26903_9818_OFFICIAL_FEATURE_SIGNATURES),
    injected_global_identifier_counts={},
    protected_official_signatures=tuple(),
    official_feature_signatures=_PROFILE_26903_9818_OFFICIAL_FEATURE_SIGNATURES,
)
_SPEC_26901_6511 = _FrontendProfileSpec(
    pairs=_PROFILE_26901_6511_PAIRS,
    official_features=frozenset(_PROFILE_26901_6511_OFFICIAL_FEATURE_SIGNATURES),
    injected_global_identifier_counts={},
    protected_official_signatures=tuple(),
    official_feature_signatures=_PROFILE_26901_6511_OFFICIAL_FEATURE_SIGNATURES,
)

# Module-level default stays on the 26810 spec so existing direct callers and
# tests observe the legacy profile; top-level operations select the spec for
# the detected frontend profile before classifying or patching.
_CURRENT_DEFAULT_SPEC: _FrontendProfileSpec = _SPEC_26810


import hotfix_profile_26908_9136 as _profile_9136
_SPEC_26908_9136 = _FrontendProfileSpec(
    pairs=_profile_9136.PAIRS,
    official_features=frozenset(_profile_9136.OFFICIAL_FEATURE_SIGNATURES),
    injected_global_identifier_counts={}, protected_official_signatures=tuple(),
    official_feature_signatures=_profile_9136.OFFICIAL_FEATURE_SIGNATURES,
)

def spec_for_profile(profile: dict[str, Any] | None) -> _FrontendProfileSpec:
    if profile is not None and profile.get("asar_source_sha256") == "7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d":
        return _SPEC_26908_9136
    if (
        profile is not None
        and profile.get("asar_source_sha256") == _PROFILE_26908_4834_ASAR_SHA256
    ):
        return _SPEC_26908_4834
    if (
        profile is not None
        and profile.get("asar_source_sha256") == _PROFILE_26903_9818_ASAR_SHA256
    ):
        return _SPEC_26903_9818
    if (
        profile is not None
        and profile.get("asar_source_sha256") == _PROFILE_26901_6511_ASAR_SHA256
    ):
        return _SPEC_26901_6511
    if (
        profile is not None
        and profile.get("asar_source_sha256") == _PROFILE_26831_2377_ASAR_SHA256
    ):
        return _SPEC_26831_2377
    if (
        profile is not None
        and profile.get("asar_source_sha256") == _PROFILE_26825_6671_ASAR_SHA256
    ):
        return _SPEC_26825_6671
    if (
        profile is not None
        and profile.get("asar_source_sha256") == _PROFILE_26825_5331_ASAR_SHA256
    ):
        return _SPEC_26825_5331
    if (
        profile is not None
        and profile.get("asar_source_sha256") == _PROFILE_26818_8289_ASAR_SHA256
    ):
        return _SPEC_26818_8289
    if (
        profile is not None
        and profile.get("asar_source_sha256") == _PROFILE_26818_5229_ASAR_SHA256
    ):
        return _SPEC_26818_5229
    if (
        profile is not None
        and profile.get("asar_source_sha256") == _PROFILE_26818_ASAR_SHA256
    ):
        return _SPEC_26818
    if (
        profile is not None
        and profile.get("asar_source_sha256") == _PROFILE_26820_ASAR_SHA256
    ):
        return _SPEC_26820
    return _SPEC_26810


def secondary_pairs_for_profile(
    profile: dict[str, Any] | None,
) -> dict[str, tuple[tuple[bytes, bytes], ...]]:
    if profile and profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}:
        return _PROFILE_26908_4834_SECONDARY_PAIRS
    if profile and profile.get("package_version") == "26.903.9818.0":
        return _PROFILE_26903_9818_SECONDARY_PAIRS
    if profile and profile.get("package_version") == "26.901.6511.0":
        return _PROFILE_26901_6511_SECONDARY_PAIRS
    if profile and profile.get("package_version") == "26.831.2377.0":
        return _PROFILE_26831_2377_SECONDARY_PAIRS
    return {}


def secondary_official_signatures_for_profile(
    profile: dict[str, Any] | None,
) -> dict[str, tuple[bytes, ...]]:
    if profile and profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}:
        return _PROFILE_26908_4834_SECONDARY_OFFICIAL_FEATURE_SIGNATURES
    if profile and profile.get("package_version") == "26.903.9818.0":
        return _PROFILE_26903_9818_SECONDARY_OFFICIAL_FEATURE_SIGNATURES
    if profile and profile.get("package_version") == "26.901.6511.0":
        return _PROFILE_26901_6511_SECONDARY_OFFICIAL_FEATURE_SIGNATURES
    if profile and profile.get("package_version") == "26.831.2377.0":
        return _PROFILE_26831_2377_SECONDARY_OFFICIAL_FEATURE_SIGNATURES
    return {}


HAS_CURRENT_WATCH_PATCH = "windows_watch_path_normalization" in _CURRENT_PROFILE_PAIRS
if HAS_CURRENT_WATCH_PATCH:
    (
        (CURRENT_WATCH_CALL_OLD, CURRENT_WATCH_CALL_NEW),
        *CURRENT_WATCH_HOST_CALLS,
    ) = _CURRENT_PROFILE_PAIRS["windows_watch_path_normalization"]
else:
    CURRENT_WATCH_CALL_OLD = b"__no_current_watch_patch_old__"
    CURRENT_WATCH_CALL_NEW = b"__no_current_watch_patch_new__"
    CURRENT_WATCH_HOST_CALLS: list[tuple[bytes, bytes]] = []
CURRENT_WATCH_PROVIDER = (
    b"function im(e,t){let n=nm(e),r=nm(t);return sm(r)||n===``?ave(r):"
    b"ave(am(n,r))}function S3e(e,t,n){let r=im(e,t);return n?ku(r):r}"
)


def classify_current_feature(
    entry: bytes,
    name: str,
    spec: _FrontendProfileSpec | None = None,
) -> tuple[str, str | None]:
    spec = _CURRENT_DEFAULT_SPEC if spec is None else spec
    replacements = spec.pairs.get(name)
    if replacements is not None:
        return _classify_current_replacements(entry, replacements)
    if name in spec.official_features:
        signatures = spec.official_feature_signatures.get(name, ())
        if signatures and any(entry.count(signature) != 1 for signature in signatures):
            return ("unsupported", "official_feature_evidence_signature_mismatch")
        return ("official_fixed", None)
    return ("unsupported", "current_profile_feature_has_no_exact_signature")


def normalize_current_profile_features(
    enabled_features: Iterable[str] | None,
    spec: _FrontendProfileSpec | None = None,
) -> set[str]:
    """Return a fail-closed current-profile diagnostic feature selection."""
    spec = _CURRENT_DEFAULT_SPEC if spec is None else spec
    if enabled_features is None:
        return set(spec.features)
    enabled = set(enabled_features)
    unknown = enabled.difference(spec.features)
    if unknown:
        raise HotfixError(
            "Unknown current-profile diagnostic feature(s): "
            + ", ".join(sorted(unknown))
        )
    return enabled


def _identifier_count(entry: bytes, identifier: str) -> int:
    token = re.escape(identifier.encode("ascii"))
    return len(re.findall(rb"(?<![A-Za-z0-9_$])" + token + rb"(?![A-Za-z0-9_$])", entry))


def validate_current_profile_global_identifiers(
    source: bytes,
    candidate: bytes,
    enabled_features: Iterable[str],
    spec: _FrontendProfileSpec | None = None,
) -> None:
    """Reject generated bindings that collide with official bundle globals."""
    spec = _CURRENT_DEFAULT_SPEC if spec is None else spec
    enabled = set(enabled_features)
    for feature, expected_counts in spec.injected_global_identifier_counts.items():
        for identifier, expected_count in expected_counts.items():
            source_count = _identifier_count(source, identifier)
            if source_count != 0:
                raise HotfixError(
                    "Current-profile injected global collides with official entry: "
                    f"feature={feature}, identifier={identifier}, source_count={source_count}"
                )
            actual_count = _identifier_count(candidate, identifier)
            required_count = expected_count if feature in enabled else 0
            if actual_count != required_count:
                raise HotfixError(
                    "Current-profile injected global occurrence count differs: "
                    f"feature={feature}, identifier={identifier}, "
                    f"expected={required_count}, actual={actual_count}"
                )
    for signature in spec.protected_official_signatures:
        if source.count(signature) != 1 or candidate.count(signature) != 1:
            raise HotfixError(
                "Current-profile protected official signature changed or is ambiguous: "
                f"{signature!r}"
            )


def patch_current_frontend_entry(
    entry: bytes,
    enabled_features: Iterable[str] | None = None,
    profile: dict[str, str | None] | None = None,
) -> tuple[bytes, dict[str, Any]]:
    if profile is None:
        profile = legacy_frontend_profile()
    spec = spec_for_profile(profile)
    global _CURRENT_DEFAULT_SPEC
    _CURRENT_DEFAULT_SPEC = spec
    source_hash = sha256_bytes(entry)
    if source_hash != profile["entry_source_sha256"]:
        raise HotfixError(
            "Current-profile frontend source hash differs: "
            f"actual={source_hash}, expected={profile['entry_source_sha256']}"
        )
    enabled = normalize_current_profile_features(enabled_features, spec)
    validate_current_profile_global_identifiers(entry, entry, (), spec)
    patched = entry
    results: dict[str, Any] = {}
    for name, replacements in spec.pairs.items():
        if name not in enabled:
            results[name] = {"status": "skipped", "reason": "diagnostic_variant"}
            continue
        status, reason = _classify_current_replacements(patched, replacements)
        if status != "patchable":
            raise HotfixError(
                f"Current-profile feature is unsafe before patching: {name}: {reason}"
            )
        for old, fixed in replacements:
            patched = patched.replace(old, fixed, 1)
        results[name] = {"status": "patched", "reason": None}

    if HAS_CURRENT_WATCH_PATCH and "windows_watch_path_normalization" in enabled:
        watch_status, watch_reason = classify_current_windows_watch_path(patched)
        if watch_status != "patchable":
            raise HotfixError(
                f"Current-profile Windows watch path is unsafe: {watch_reason}"
            )
        patched = patched.replace(CURRENT_WATCH_CALL_OLD, CURRENT_WATCH_CALL_NEW, 1)
        for old, fixed in CURRENT_WATCH_HOST_CALLS:
            patched = patched.replace(old, fixed, 1)
        results["windows_watch_path_normalization"] = {
            "status": "patched",
            "reason": None,
        }
    elif HAS_CURRENT_WATCH_PATCH:
        results["windows_watch_path_normalization"] = {
            "status": "skipped",
            "reason": "diagnostic_variant",
        }

    if is_split_frontend_profile(profile) and enabled == set(spec.features):
        patched = inject_renderer_attestation(patched, profile)
        results["frontend_live_renderer_attestation"] = {
            "status": "patched",
            "reason": None,
            "marker": FRONTEND_ATTESTATION_MARKER,
            "artifact_id": FRONTEND_ATTESTATION_ARTIFACT_ID,
            "feature_count": len(FRONTEND_ATTESTATION_FEATURES),
        }
    patched = equalize_current_entry_length(entry, patched)
    if len(patched) != len(entry):
        raise HotfixError("Current-profile frontend entry length changed")
    validate_current_profile_global_identifiers(entry, patched, enabled, spec)
    for name in spec.pairs:
        status, reason = classify_current_feature(patched, name, spec)
        expected_status = "official_fixed" if name in enabled else "patchable"
        if status != expected_status:
            raise HotfixError(
                "Current-profile feature validation failed: "
                f"{name}: expected={expected_status}, actual={status}, reason={reason}"
            )
    if HAS_CURRENT_WATCH_PATCH:
        watch_status, watch_reason = classify_current_windows_watch_path(patched)
        expected_watch_status = (
            "official_fixed" if "windows_watch_path_normalization" in enabled else "patchable"
        )
        if watch_status != expected_watch_status:
            raise HotfixError(
                "Current-profile watch validation failed: "
                f"expected={expected_watch_status}, actual={watch_status}, reason={watch_reason}"
            )
    return patched, results


def patch_profile_secondary_entry(
    entry: bytes,
    profile: dict[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    """Patch the exact dynamic chunk owned by a split frontend profile."""
    replacements_by_feature = secondary_pairs_for_profile(profile)
    if not replacements_by_feature:
        return entry, {}
    expected = profile.get("secondary_entry_source_sha256")
    if not expected or sha256_bytes(entry) != expected:
        raise HotfixError("Secondary frontend entry source hash differs")
    patched = entry
    results: dict[str, Any] = {}
    for name, replacements in replacements_by_feature.items():
        status, reason = _classify_current_replacements(patched, replacements)
        if status != "patchable":
            raise HotfixError(
                f"Secondary frontend feature is unsafe before patching: {name}: {reason}"
            )
        for old, fixed in replacements:
            patched = patched.replace(old, fixed, 1)
        results[name] = {"status": "patched", "reason": None}
    patched = equalize_current_entry_length(entry, patched)
    if len(patched) != len(entry):
        raise HotfixError("Secondary frontend entry length changed")
    for name, replacements in replacements_by_feature.items():
        status, reason = _classify_current_replacements(patched, replacements)
        if status != "official_fixed":
            raise HotfixError(
                f"Secondary frontend feature did not converge: {name}: {reason}"
            )
    return patched, results


UPDATE_MENU_OLD = (
    b"click:()=>{D5().info(`Check for updates requested via menu.`),u.checkForUpdates().then(()=>{if(u.hasUpdater())return;let e=u.getUnavailableReason()??`unknown`;D5().warning(`Desktop updater unavailable; init likely skipped.`,{safe:{reason:e},sensitive:{}}),l.dialog.showMessageBox({type:`info`,title:`Updates Unavailable`,message:`Automatic updates are unavailable right now.`,detail:`Updater initialization skipped: ${e}`})})}}"
)
UPDATE_MENU_NEW = (
    b"click:()=>{try{x.spawn(`powershell.exe`,[`-NoProfile`,`-ExecutionPolicy`,`Bypass`,`-WindowStyle`,`Hidden`,`-File`,(0,p.join)(S.env.USERPROFILE,`.codex`,`maintenance`,`chatgpt-project-hotfix-manager`,`Manage-ChatGPTProjectHotfix.ps1`),`-Mode`,`UpdateStatus`],{detached:!0,stdio:`ignore`,windowsHide:!0}).unref()}catch(e){D5().warning(`Safe update status could not be opened.`,{safe:{},sensitive:{}})}}}"
)
UPDATE_MENU_26825_OLD = (
    b"click:()=>{$5().info(`Check for updates requested via menu.`),d.checkForUpdates().then(()=>{if(d.hasUpdater())return;let e=d.getUnavailableReason()??`unknown`;$5().warning(`Desktop updater unavailable; init likely skipped.`,{safe:{reason:e},sensitive:{}}),l.dialog.showMessageBox({type:`info`,title:`Updates Unavailable`,message:`Automatic updates are unavailable right now.`,detail:`Updater initialization skipped: ${e}`})})}}"
)
UPDATE_MENU_26825_NEW = (
    b"click:()=>{try{(0,x.spawn)(`powershell.exe`,[`-NoProfile`,`-ExecutionPolicy`,`Bypass`,`-WindowStyle`,`Hidden`,`-File`,(0,p.join)(process.env.USERPROFILE,`.codex`,`maintenance`,`chatgpt-project-hotfix-manager`,`Manage-ChatGPTProjectHotfix.ps1`),`-Mode`,`UpdateStatus`],{detached:!0,stdio:`ignore`,windowsHide:!0}).unref()}catch(e){$5().warning(`Safe update status could not be opened.`,{safe:{},sensitive:{}})}}}"
)
UPDATE_MENU_26825_MAIN_SHA256S = {
    PROCESS_REGISTRY_REMOVED_MAIN_SHA256,
    PROCESS_REGISTRY_REMOVED_MAIN_26825_6671_SHA256,
}
UPDATE_MENU_26903_OLD = (
    b'click:()=>{_7().info(`Check for updates requested via menu.`),d.checkForUpdates().then(()=>{if(d.hasUpdater())return;let e=d.getUnavailableReason()??`unknown`;_7().warning(`Desktop updater unavailable; init likely skipped.`,{safe:{reason:e},sensitive:{}}),l.dialog.showMessageBox({type:`info`,title:`Updates Unavailable`,message:`Automatic updates are unavailable right now.`,detail:`Updater initialization skipped: ${e}`})})}}'
)
UPDATE_MENU_26903_NEW = (
    b'click:()=>{try{(0,x.spawn)(`powershell.exe`,[`-NoProfile`,`-ExecutionPolicy`,`Bypass`,`-WindowStyle`,`Hidden`,`-File`,(0,p.join)(process.env.USERPROFILE,`.codex`,`maintenance`,`chatgpt-project-hotfix-manager`,`Manage-ChatGPTProjectHotfix.ps1`),`-Mode`,`UpdateStatus`],{detached:!0,stdio:`ignore`,windowsHide:!0}).unref()}catch(e){_7().warning(`Safe update status could not be opened.`,{safe:{},sensitive:{}})}}}'
)
UPDATE_MENU_26831_OLD = (
    b"click:()=>{v7().info(`Check for updates requested via menu.`),d.checkForUpdates().then(()=>{if(d.hasUpdater())return;let e=d.getUnavailableReason()??`unknown`;v7().warning(`Desktop updater unavailable; init likely skipped.`,{safe:{reason:e},sensitive:{}}),l.dialog.showMessageBox({type:`info`,title:`Updates Unavailable`,message:`Automatic updates are unavailable right now.`,detail:`Updater initialization skipped: ${e}`})})}}"
)
UPDATE_MENU_26831_NEW = (
    b"click:()=>{try{(0,x.spawn)(`powershell.exe`,[`-NoProfile`,`-ExecutionPolicy`,`Bypass`,`-WindowStyle`,`Hidden`,`-File`,(0,p.join)(process.env.USERPROFILE,`.codex`,`maintenance`,`chatgpt-project-hotfix-manager`,`Manage-ChatGPTProjectHotfix.ps1`),`-Mode`,`UpdateStatus`],{detached:!0,stdio:`ignore`,windowsHide:!0}).unref()}catch(e){v7().warning(`Safe update status could not be opened.`,{safe:{},sensitive:{}})}}}"
)


def validate_javascript_syntax(entry: bytes, path: str) -> None:
    """Fail closed when a generated JavaScript entry is not parseable by Node."""
    node = shutil.which("node")
    if node is None:
        raise HotfixError("Node.js is required for the JavaScript release gate")
    completed = subprocess.run(
        [node, "--check", "--input-type=module"],
        input=entry,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        diagnostic = completed.stderr.decode("utf-8", "replace")[-1200:].strip()
        raise HotfixError(f"Generated JavaScript syntax check failed: {path}: {diagnostic}")


def patch_portable_update_status_entry(entry: bytes, profile: dict[str, Any]) -> bytes:
    """Replace only the portable menu's unavailable Electron updater action."""
    expected = profile.get("main_entry_source_sha256")
    if not expected or sha256_bytes(entry) != expected:
        raise HotfixError("Portable update-menu source hash differs from its exact profile")
    if profile.get("package_version") in {"26.903.9818.0", "26.908.4834.0", "26.908.9136.0"}:
        old, fixed = UPDATE_MENU_26903_OLD, UPDATE_MENU_26903_NEW
    elif is_split_frontend_profile(profile):
        old, fixed = UPDATE_MENU_26831_OLD, UPDATE_MENU_26831_NEW
    elif expected in UPDATE_MENU_26825_MAIN_SHA256S:
        old, fixed = UPDATE_MENU_26825_OLD, UPDATE_MENU_26825_NEW
    else:
        old, fixed = UPDATE_MENU_OLD, UPDATE_MENU_NEW
    if entry.count(old) != 1 or entry.count(fixed) != 0:
        raise HotfixError("Portable update-menu callback is missing or ambiguous")
    patched = equalize_entry_length(entry, entry.replace(old, fixed, 1))
    if patched.count(old) != 0 or patched.count(fixed) != 1:
        raise HotfixError("Portable update-menu callback verification failed")
    return patched


def patch_frontend_attestation_protocol_entry(
    entry: bytes, profile: dict[str, Any]
) -> bytes:
    """Expose exactly one signed resource module through the app:// handler.

    The stock handler intentionally rejects ``..`` traversal.  The renderer
    therefore imports ``app://-/x`` and this exact, hash-gated branch maps only
    that URL to ``resources/x.js``.  No general filesystem route is opened.
    """
    expected = profile.get("attestation_protocol_source_sha256")
    if not expected or sha256_bytes(entry) != expected:
        raise HotfixError("Frontend attestation protocol source hash differs")
    old_count = entry.count(FRONTEND_ATTESTATION_PROTOCOL_OLD) + entry.count(
        FRONTEND_ATTESTATION_PROTOCOL_26903_OLD
    ) + entry.count(FRONTEND_ATTESTATION_PROTOCOL_26908_OLD)
    new_count = entry.count(FRONTEND_ATTESTATION_PROTOCOL_NEW) + entry.count(
        FRONTEND_ATTESTATION_PROTOCOL_26903_NEW
    ) + entry.count(FRONTEND_ATTESTATION_PROTOCOL_26908_NEW)
    latest = is_split_frontend_profile(profile)
    if profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}:
        resolver_old = FRONTEND_ATTESTATION_PROTOCOL_26908_OLD
        resolver_new = FRONTEND_ATTESTATION_PROTOCOL_26908_NEW
        handler_old = FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26908_OLD
        handler_fixed = FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26908_NEW
    elif profile.get("package_version") == "26.903.9818.0":
        resolver_old = FRONTEND_ATTESTATION_PROTOCOL_26903_OLD
        resolver_new = FRONTEND_ATTESTATION_PROTOCOL_26903_NEW
        handler_old = FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26903_OLD
        handler_fixed = FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26903_NEW
    else:
        resolver_old = FRONTEND_ATTESTATION_PROTOCOL_OLD
        resolver_new = FRONTEND_ATTESTATION_PROTOCOL_NEW
        handler_old = (
            FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26831_OLD
            if latest else FRONTEND_ATTESTATION_PROTOCOL_HANDLER_OLD
        )
        handler_fixed = (
            FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26831_NEW
            if latest else FRONTEND_ATTESTATION_PROTOCOL_HANDLER_NEW
        )
    handler_old_count = entry.count(handler_old)
    handler_new_count = entry.count(handler_fixed)
    compaction_old_count = entry.count(FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_OLD)
    compaction_new_count = entry.count(FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_NEW)
    if (old_count != 1 or new_count != 0 or handler_old_count != 1 or handler_new_count != 0 or (not latest and (compaction_old_count != 1 or compaction_new_count != 0))):
        raise HotfixError(
            "Frontend attestation protocol signature is unsafe: "
            f"resolver_old={old_count}, resolver_new={new_count}, "
            f"handler_old={handler_old_count}, handler_new={handler_new_count}"
            f", compaction_old={compaction_old_count}, compaction_new={compaction_new_count}"
        )
    patched = entry.replace(resolver_old, resolver_new, 1)
    patched = patched.replace(
        handler_old,
        handler_fixed,
        1,
    )
    if not latest:
        patched = patched.replace(
            FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_OLD,
            FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_NEW,
            1,
        )
    patched = equalize_entry_length(entry, patched)
    if (
        patched.count(resolver_old) != 0
        or patched.count(resolver_new) != 1
        or patched.count(handler_old) != 0
        or patched.count(handler_fixed) != 1
        or (not latest and patched.count(FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_OLD) != 0)
        or patched.count(FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_NEW) != 1
        or len(patched) != len(entry)
    ):
        raise HotfixError("Frontend attestation protocol patch did not converge")
    return patched


def patch_current_profile_entry_file(
    source: Path,
    target: Path,
    enabled_features: Iterable[str],
) -> dict[str, Any]:
    """Patch one copied ASAR for a runtime diagnostic variant only."""
    if not source.is_file() or not target.is_file():
        raise HotfixError("Diagnostic source or target ASAR is missing")
    if (
        source.stat().st_size != target.stat().st_size
        or sha256_path(source) != sha256_path(target)
    ):
        raise HotfixError("Diagnostic target ASAR is not an exact official copy")
    header_size, serialized_header, header = read_asar(source)
    source_profile = profile_for_asar(sha256_path(source))
    if source_profile is None:
        raise HotfixError("Diagnostic source ASAR does not match a frontend profile")
    entry_path = str(source_profile["entry_path"])
    meta = get_entry_meta(header, entry_path)
    offset, entry = read_entry(source, header_size, meta)
    patched, results = patch_current_frontend_entry(entry, enabled_features, source_profile)
    patched_header = replace_entry_integrity_metadata(
        serialized_header, header, entry_path, entry, patched
    )
    if len(patched_header) != len(serialized_header) or len(patched) != len(entry):
        raise HotfixError("Diagnostic patch changed ASAR layout")
    with target.open("r+b") as handle:
        handle.seek(0)
        handle.write(patched_header)
        handle.seek(offset)
        handle.write(patched)
    target_header_size, target_header_bytes, target_header = read_asar(target)
    if target_header_size != header_size or target_header_bytes != patched_header:
        raise HotfixError("Diagnostic ASAR header verification failed")
    target_meta = get_entry_meta(target_header, entry_path)
    _, target_entry = read_entry(target, target_header_size, target_meta)
    if target_entry != patched:
        raise HotfixError("Diagnostic ASAR entry verification failed")
    return {
        "ok": True,
        "source_asar": str(source.resolve()),
        "target_asar": str(target.resolve()),
        "enabled_features": sorted(normalize_current_profile_features(enabled_features)),
        "source_sha256": sha256_path(source),
        "target_sha256": sha256_path(target),
        "entry_source_sha256": sha256_bytes(entry),
        "entry_target_sha256": sha256_bytes(target_entry),
        "features": results,
    }


def classify_signature(entry: bytes, old: bytes, fixed: bytes) -> tuple[str, str | None]:
    old_count = entry.count(old)
    fixed_count = entry.count(fixed)
    if old_count == 1 and fixed_count == 0:
        return "patchable", None
    if old_count == 0 and fixed_count == 1:
        return "official_fixed", None
    return "unsupported", f"old_count={old_count}, fixed_count={fixed_count}"


def classify_signature_variants(
    entry: bytes,
    old_signatures: tuple[bytes, ...],
    fixed_signatures: tuple[bytes, ...],
) -> tuple[str, str | None]:
    unique_old = tuple(dict.fromkeys(old_signatures))
    unique_fixed = tuple(dict.fromkeys(fixed_signatures))
    old_count = sum(entry.count(signature) for signature in unique_old)
    fixed_count = sum(entry.count(signature) for signature in unique_fixed)
    if old_count == 1 and fixed_count == 0:
        return "patchable", None
    if old_count == 0 and fixed_count == 1:
        return "official_fixed", None
    return "unsupported", f"old_count={old_count}, fixed_count={fixed_count}"


def classify_resume_history(entry: bytes) -> tuple[str, str | None]:
    if entry.count(CURRENT_RESUME_HISTORY_FIXED) == 1:
        return "official_fixed", None
    factory_status, factory_reason = classify_signature_variants(
        entry,
        (
            RESUME_HISTORY_OLD,
            RESUME_HISTORY_BUNDLED_OLD,
            RESUME_HISTORY_SUPPRESS_ALL,
        ),
        (RESUME_HISTORY_FORCE_DRAIN,),
    )
    guard_status, guard_reason = classify_signature_variants(
        entry,
        (RESUME_HISTORY_GUARD_OLD,),
        (RESUME_HISTORY_GUARD_NEW,),
    )
    if factory_status == "unsupported" or guard_status == "unsupported":
        return (
            "unsupported",
            f"factory={factory_status}:{factory_reason}; "
            f"guard={guard_status}:{guard_reason}",
        )
    if factory_status == "official_fixed" and guard_status == "official_fixed":
        return "official_fixed", None
    return "patchable", None


def classify_idle_history(entry: bytes) -> tuple[str, str | None]:
    if entry.count(CURRENT_IDLE_HISTORY_FIXED) == 1:
        return "official_fixed", None
    return classify_signature_variants(
        entry,
        (IDLE_HISTORY_OLD,),
        (IDLE_HISTORY_NEW, IDLE_HISTORY_BUNDLED_FIXED),
    )


def classify_paginated_tail_retention(entry: bytes) -> tuple[str, str | None]:
    if entry.count(CURRENT_TAIL_HISTORY_FIXED) == 1:
        return "official_fixed", None
    return classify_signature_variants(
        entry,
        (PAGINATED_TAIL_RETENTION_OLD,),
        (PAGINATED_TAIL_RETENTION_NEW,),
    )


def _classify_legacy_windows_watch_path(entry: bytes) -> tuple[str, str | None]:
    dependency_imports = list(WINDOWS_WATCH_DEPENDENCY_IMPORT_RE.finditer(entry))
    if len(dependency_imports) == 1:
        dependency_spec = dependency_imports[0].group("spec")
        dependency_old_imports = dependency_spec.count(WINDOWS_WATCH_IMPORT_OLD)
        dependency_fixed_imports = dependency_spec.count(WINDOWS_WATCH_IMPORT_NEW)
    else:
        dependency_old_imports = 0
        dependency_fixed_imports = 0
    counts = {
        "dependency_imports": len(dependency_imports),
        "old_import": entry.count(WINDOWS_WATCH_IMPORT_OLD),
        "fixed_import": entry.count(WINDOWS_WATCH_IMPORT_NEW),
        "dependency_old_import": dependency_old_imports,
        "dependency_fixed_import": dependency_fixed_imports,
        "old_call": entry.count(WINDOWS_WATCH_CALL_OLD),
        "fixed_call": entry.count(WINDOWS_WATCH_CALL_NEW),
        "bundled_provider": entry.count(WINDOWS_WATCH_BUNDLED_PROVIDER),
        "bundled_old_call": entry.count(WINDOWS_WATCH_BUNDLED_CALL_OLD),
        "bundled_fixed_call": entry.count(WINDOWS_WATCH_BUNDLED_CALL_NEW),
        "total_host_calls": entry.count(WINDOWS_WATCH_TOTAL_CALL),
    }
    for index, (old, fixed) in enumerate(WINDOWS_WATCH_HOST_CALLS):
        counts[f"old_host_call_{index}"] = entry.count(old)
        counts[f"fixed_host_call_{index}"] = entry.count(fixed)
    patchable_counts = {
        "dependency_imports": 1,
        "old_import": 1,
        "fixed_import": 0,
        "dependency_old_import": 1,
        "dependency_fixed_import": 0,
        "old_call": 1,
        "fixed_call": 0,
        "bundled_provider": 0,
        "bundled_old_call": 0,
        "bundled_fixed_call": 0,
        "total_host_calls": len(WINDOWS_WATCH_HOST_CALLS),
        **{
            f"{kind}_host_call_{index}": expected
            for index in range(len(WINDOWS_WATCH_HOST_CALLS))
            for kind, expected in (("old", 1), ("fixed", 0))
        },
    }
    fixed_counts = {
        "dependency_imports": 1,
        "old_import": 0,
        "fixed_import": 1,
        "dependency_old_import": 0,
        "dependency_fixed_import": 1,
        "old_call": 0,
        "fixed_call": 1,
        "bundled_provider": 0,
        "bundled_old_call": 0,
        "bundled_fixed_call": 0,
        "total_host_calls": len(WINDOWS_WATCH_HOST_CALLS),
        **{
            f"{kind}_host_call_{index}": expected
            for index in range(len(WINDOWS_WATCH_HOST_CALLS))
            for kind, expected in (("old", 0), ("fixed", 1))
        },
    }
    if counts == patchable_counts:
        return "patchable", None
    if counts == fixed_counts:
        return "official_fixed", None
    reason = ", ".join(f"{name}={count}" for name, count in counts.items())
    return "unsupported", reason


def _classify_bundled_windows_watch_path(entry: bytes) -> tuple[str, str | None]:
    counts = {
        "bundled_provider": entry.count(WINDOWS_WATCH_BUNDLED_PROVIDER),
        "dependency_imports": len(
            list(WINDOWS_WATCH_DEPENDENCY_IMPORT_RE.finditer(entry))
        ),
        "legacy_old_call": entry.count(WINDOWS_WATCH_CALL_OLD),
        "legacy_fixed_call": entry.count(WINDOWS_WATCH_CALL_NEW),
        "old_call": entry.count(WINDOWS_WATCH_BUNDLED_CALL_OLD),
        "fixed_call": entry.count(WINDOWS_WATCH_BUNDLED_CALL_NEW),
        "total_host_calls": entry.count(WINDOWS_WATCH_TOTAL_CALL),
    }
    for index, (old, fixed) in enumerate(WINDOWS_WATCH_HOST_CALLS):
        counts[f"old_host_call_{index}"] = entry.count(old)
        counts[f"fixed_host_call_{index}"] = entry.count(fixed)
    common = {
        "bundled_provider": 1,
        "dependency_imports": 0,
        "legacy_old_call": 0,
        "legacy_fixed_call": 0,
        "total_host_calls": len(WINDOWS_WATCH_HOST_CALLS),
    }
    patchable_counts = {
        **common,
        "old_call": 1,
        "fixed_call": 0,
        **{
            f"{kind}_host_call_{index}": expected
            for index in range(len(WINDOWS_WATCH_HOST_CALLS))
            for kind, expected in (("old", 1), ("fixed", 0))
        },
    }
    fixed_counts = {
        **common,
        "old_call": 0,
        "fixed_call": 1,
        **{
            f"{kind}_host_call_{index}": expected
            for index in range(len(WINDOWS_WATCH_HOST_CALLS))
            for kind, expected in (("old", 0), ("fixed", 1))
        },
    }
    if counts == patchable_counts:
        return "patchable", None
    if counts == fixed_counts:
        return "official_fixed", None
    reason = ", ".join(f"{name}={count}" for name, count in counts.items())
    return "unsupported", reason


def classify_current_windows_watch_path(entry: bytes) -> tuple[str, str | None]:
    counts = {
        "provider": entry.count(CURRENT_WATCH_PROVIDER),
        "old_call": entry.count(CURRENT_WATCH_CALL_OLD),
        "fixed_call": entry.count(CURRENT_WATCH_CALL_NEW),
        "total_host_calls": entry.count(WINDOWS_WATCH_TOTAL_CALL),
    }
    for index, (old, fixed) in enumerate(WINDOWS_WATCH_HOST_CALLS):
        counts[f"old_host_call_{index}"] = entry.count(old)
        counts[f"fixed_host_call_{index}"] = entry.count(fixed)
    common = {
        "provider": 1,
        "total_host_calls": len(WINDOWS_WATCH_HOST_CALLS),
    }
    patchable = {
        **common,
        "old_call": 1,
        "fixed_call": 0,
        **{
            f"{kind}_host_call_{index}": expected
            for index in range(len(WINDOWS_WATCH_HOST_CALLS))
            for kind, expected in (("old", 1), ("fixed", 0))
        },
    }
    fixed = {
        **common,
        "old_call": 0,
        "fixed_call": 1,
        **{
            f"{kind}_host_call_{index}": expected
            for index in range(len(WINDOWS_WATCH_HOST_CALLS))
            for kind, expected in (("old", 0), ("fixed", 1))
        },
    }
    if counts == patchable:
        return "patchable", None
    if counts == fixed:
        return "official_fixed", None
    return "unsupported", ", ".join(f"{k}={v}" for k, v in counts.items())


def _classify_windows_watch_variant(
    entry: bytes,
) -> tuple[str, str | None, str | None]:
    current_markers = (
        entry.count(CURRENT_WATCH_PROVIDER)
        + entry.count(CURRENT_WATCH_CALL_OLD)
        + entry.count(CURRENT_WATCH_CALL_NEW)
    )
    if current_markers:
        status, reason = classify_current_windows_watch_path(entry)
        return status, reason, "current"
    bundled_markers = (
        entry.count(WINDOWS_WATCH_BUNDLED_PROVIDER)
        + entry.count(WINDOWS_WATCH_BUNDLED_CALL_OLD)
        + entry.count(WINDOWS_WATCH_BUNDLED_CALL_NEW)
    )
    if bundled_markers:
        status, reason = _classify_bundled_windows_watch_path(entry)
        return status, reason, "bundled"
    status, reason = _classify_legacy_windows_watch_path(entry)
    return status, reason, "legacy"


def classify_windows_watch_path(entry: bytes) -> tuple[str, str | None]:
    status, reason, _ = _classify_windows_watch_variant(entry)
    return status, reason


def inspect_windows_watch_dependency(
    source: Path,
    header_size: int,
    header: dict[str, Any],
    history_path: str | None = None,
    history_entry: bytes | None = None,
) -> tuple[list[dict[str, str]] | None, str | None]:
    if history_entry is not None and history_entry.count(CURRENT_WATCH_PROVIDER) > 0:
        if history_path is None or history_entry.count(CURRENT_WATCH_PROVIDER) != 1:
            return None, "current_provider_signature_invalid"
        return (
            [
                {
                    "path": history_path,
                    "sha256": sha256_bytes(CURRENT_WATCH_PROVIDER),
                    "verification": "current_provider_signature",
                }
            ],
            None,
        )
    if history_entry is not None and (
        history_entry.count(WINDOWS_WATCH_BUNDLED_PROVIDER) > 0
        or history_entry.count(WINDOWS_WATCH_BUNDLED_CALL_OLD) > 0
        or history_entry.count(WINDOWS_WATCH_BUNDLED_CALL_NEW) > 0
    ):
        if (
            history_path is None
            or history_entry.count(WINDOWS_WATCH_BUNDLED_PROVIDER) != 1
        ):
            return None, "bundled_provider_signature_invalid"
        return (
            [
                {
                    "path": history_path,
                    "sha256": sha256_bytes(WINDOWS_WATCH_BUNDLED_PROVIDER),
                    "verification": "bundled_provider_signature",
                }
            ],
            None,
        )
    dependencies: list[dict[str, str]] = []
    for dependency_path, allowed_hashes in (
        WINDOWS_WATCH_DEPENDENCY_SHA256_ALLOWLIST.items()
    ):
        try:
            dependency_meta = get_entry_meta(header, dependency_path)
            _, dependency_entry = read_entry(source, header_size, dependency_meta)
        except HotfixError as exc:
            return None, f"dependency_unavailable: path={dependency_path}, error={exc}"
        dependency_hash = sha256_bytes(dependency_entry)
        if dependency_hash not in allowed_hashes:
            return (
                None,
                "dependency_sha256_not_allowlisted: "
                f"path={dependency_path}, sha256={dependency_hash}",
            )
        dependencies.append(
            {
                "path": dependency_path,
                "sha256": dependency_hash,
                "verification": "exact_sha256_allowlist",
            }
        )
    return dependencies, None


def validate_windows_watch_dependencies(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    if not HAS_CURRENT_WATCH_PATCH and value == []:
        # The narrow current profile does not alter the legacy watch helper.
        # An empty dependency inventory is therefore the only accurate record.
        return True
    if len(value) == 1:
        dependency = value[0]
        return bool(
            isinstance(dependency, dict)
            and isinstance(dependency.get("path"), str)
            and re.fullmatch(
                r"webview/assets/app-initial-[^/]+\.js",
                dependency["path"],
            )
            and (
                (
                    dependency.get("sha256")
                    == sha256_bytes(WINDOWS_WATCH_BUNDLED_PROVIDER)
                    and dependency.get("verification")
                    == "bundled_provider_signature"
                )
                or (
                    dependency.get("sha256") == sha256_bytes(CURRENT_WATCH_PROVIDER)
                    and dependency.get("verification")
                    == "current_provider_signature"
                )
            )
        )
    if len(value) != len(WINDOWS_WATCH_DEPENDENCY_SHA256_ALLOWLIST):
        return False
    seen: set[str] = set()
    for dependency in value:
        if not isinstance(dependency, dict):
            return False
        dependency_path = dependency.get("path")
        dependency_hash = dependency.get("sha256")
        if (
            not isinstance(dependency_path, str)
            or dependency_path in seen
            or dependency_path not in WINDOWS_WATCH_DEPENDENCY_SHA256_ALLOWLIST
            or dependency_hash
            not in WINDOWS_WATCH_DEPENDENCY_SHA256_ALLOWLIST[dependency_path]
            or dependency.get("verification") != "exact_sha256_allowlist"
        ):
            return False
        seen.add(dependency_path)
    return seen == set(WINDOWS_WATCH_DEPENDENCY_SHA256_ALLOWLIST)


def patch_history_entry(
    entry: bytes,
    *,
    length_reference: bytes | None = None,
) -> tuple[bytes, dict[str, Any]]:
    resume_status, resume_reason = classify_resume_history(entry)
    idle_status, idle_reason = classify_idle_history(entry)
    tail_status, tail_reason = classify_paginated_tail_retention(entry)
    watch_status, watch_reason, watch_variant = _classify_windows_watch_variant(entry)
    if resume_status == "unsupported":
        raise HotfixError(f"Resume-history expression is unsafe: {resume_reason}")
    if tail_status == "unsupported":
        raise HotfixError(
            f"Paginated-tail retention expression is unsafe: {tail_reason}"
        )
    if watch_status == "unsupported":
        raise HotfixError(f"Windows watch-path expression is unsafe: {watch_reason}")

    reference = entry if length_reference is None else length_reference
    required_only = entry
    results: dict[str, Any] = {
        "resume_history_on_demand": {
            "status": "official_fixed" if resume_status == "official_fixed" else "patched",
            "reason": resume_reason,
            "policy": "eager_full_after_tail",
            "factory_policy": "force_full_history",
            "initial_turn_page_limit": 5,
            "auto_drain_remaining_turns": True,
            "prevents_new_paginated_threads": True,
            "supports_existing_paginated_threads": False,
            "supports_existing_paginated_threads_after_recovery": True,
            "projection_recovery": "manager_prelaunch",
        },
        "paginated_tail_retention": {
            "status": (
                "official_fixed" if tail_status == "official_fixed" else "patched"
            ),
            "reason": tail_reason,
            "policy": "keep_paginated_loaded",
            "scope": "history_mode_paginated",
        },
        "windows_watch_path_normalization": {
            "status": "official_fixed" if watch_status == "official_fixed" else "patched",
            "reason": watch_reason,
        },
        "idle_history_eviction": {
            "status": idle_status,
            "reason": idle_reason,
        },
    }
    if resume_status == "patchable":
        old_resume_factories = (
            RESUME_HISTORY_OLD,
            RESUME_HISTORY_BUNDLED_OLD,
            RESUME_HISTORY_SUPPRESS_ALL,
        )
        matching_resume_factories = [
            signature
            for signature in old_resume_factories
            if required_only.count(signature) == 1
        ]
        if len(matching_resume_factories) == 1:
            required_only = required_only.replace(
                matching_resume_factories[0],
                RESUME_HISTORY_FORCE_DRAIN,
                1,
            )
        elif (
            len(matching_resume_factories) != 0
            or required_only.count(RESUME_HISTORY_FORCE_DRAIN) != 1
        ):
            raise HotfixError("Resume-history factory signature disappeared")

        if required_only.count(RESUME_HISTORY_GUARD_OLD) == 1:
            required_only = required_only.replace(
                RESUME_HISTORY_GUARD_OLD,
                RESUME_HISTORY_GUARD_NEW,
                1,
            )
        elif required_only.count(RESUME_HISTORY_GUARD_NEW) != 1:
            raise HotfixError("Resume-history drain guard disappeared")

    if tail_status == "patchable":
        if (
            required_only.count(PAGINATED_TAIL_LOG_OLD) != 1
            or required_only.count(PAGINATED_TAIL_LOG_NEW) != 0
        ):
            raise HotfixError(
                "Paginated-tail log-budget signature is unsafe: "
                f"old_count={required_only.count(PAGINATED_TAIL_LOG_OLD)}, "
                f"fixed_count={required_only.count(PAGINATED_TAIL_LOG_NEW)}"
            )
        required_only = required_only.replace(
            PAGINATED_TAIL_RETENTION_OLD,
            PAGINATED_TAIL_RETENTION_NEW,
            1,
        )
        required_only = required_only.replace(
            PAGINATED_TAIL_LOG_OLD,
            PAGINATED_TAIL_LOG_NEW,
            1,
        )

    if watch_status == "patchable":
        if watch_variant == "legacy":
            dependency_import = WINDOWS_WATCH_DEPENDENCY_IMPORT_RE.search(required_only)
            if dependency_import is None:
                raise HotfixError("Windows watch-path dependency import disappeared")
            dependency_spec = dependency_import.group("spec")
            fixed_dependency_spec = dependency_spec.replace(
                WINDOWS_WATCH_IMPORT_OLD,
                WINDOWS_WATCH_IMPORT_NEW,
                1,
            )
            required_only = (
                required_only[: dependency_import.start("spec")]
                + fixed_dependency_spec
                + required_only[dependency_import.end("spec") :]
            )
            required_only = required_only.replace(
                WINDOWS_WATCH_CALL_OLD,
                WINDOWS_WATCH_CALL_NEW,
                1,
            )
        elif watch_variant == "bundled":
            required_only = required_only.replace(
                WINDOWS_WATCH_BUNDLED_CALL_OLD,
                WINDOWS_WATCH_BUNDLED_CALL_NEW,
                1,
            )
        else:
            raise HotfixError("Windows watch-path variant is unknown")
        for old, fixed in WINDOWS_WATCH_HOST_CALLS:
            required_only = required_only.replace(old, fixed, 1)

    candidate = required_only
    if idle_status == "patchable":
        candidate = candidate.replace(IDLE_HISTORY_OLD, IDLE_HISTORY_NEW, 1)
        results["idle_history_eviction"] = {"status": "patched", "reason": None}
    elif idle_status == "official_fixed":
        results["idle_history_eviction"] = {"status": "official_fixed", "reason": None}

    try:
        patched = equalize_entry_length(reference, candidate)
    except HotfixError as exc:
        if idle_status != "patchable":
            raise
        # Idle eviction is deliberately optional. If it does not fit a future
        # source-map footer, retain both required protections.
        patched = equalize_entry_length(reference, required_only)
        results["idle_history_eviction"] = {
            "status": "unsupported",
            "reason": f"combined_patch_failed: {exc}",
        }

    resume_validation, resume_validation_reason = classify_resume_history(patched)
    if resume_validation != "official_fixed":
        raise HotfixError(
            "Resume-history full-drain patch validation failed: "
            f"actual={resume_validation}, "
            f"reason={resume_validation_reason}"
        )
    tail_validation, tail_validation_reason = classify_paginated_tail_retention(
        patched
    )
    if tail_validation != "official_fixed":
        raise HotfixError(
            "Paginated-tail retention patch validation failed: "
            f"actual={tail_validation}, reason={tail_validation_reason}"
        )
    if results["windows_watch_path_normalization"]["status"] == "patched":
        watch_validation, watch_validation_reason = classify_windows_watch_path(patched)
        if watch_validation != "official_fixed":
            raise HotfixError(
                "Windows watch-path patched signature validation failed: "
                f"{watch_validation_reason}"
            )
    if results["idle_history_eviction"]["status"] == "patched":
        idle_validation, idle_validation_reason = classify_idle_history(patched)
        if idle_validation != "official_fixed":
            raise HotfixError(
                "Idle-history patched signature validation failed: "
                f"{idle_validation_reason}"
            )
    return patched, results


PROCESS_SIGNATURE_VARIANTS = {
    "read_recovery": (
        (PROCESS_READ_OLD, PROCESS_READ_NEW),
        (PROCESS_READ_BUNDLED_OLD, PROCESS_READ_BUNDLED_NEW),
    ),
    "atomic_write": (
        (PROCESS_WRITE_OLD, PROCESS_WRITE_NEW),
        (PROCESS_WRITE_BUNDLED_OLD, PROCESS_WRITE_BUNDLED_NEW),
    ),
}


def _classify_paired_signature_variants(
    entry: bytes,
    variants: tuple[tuple[bytes, bytes], ...],
) -> tuple[str, str | None, tuple[bytes, bytes] | None]:
    old_count = sum(entry.count(old) for old, _ in variants)
    fixed_count = sum(entry.count(fixed) for _, fixed in variants)
    if old_count == 1 and fixed_count == 0:
        matched = [pair for pair in variants if entry.count(pair[0]) == 1]
        if len(matched) == 1:
            return "patchable", None, matched[0]
    if old_count == 0 and fixed_count == 1:
        matched = [pair for pair in variants if entry.count(pair[1]) == 1]
        if len(matched) == 1:
            return "official_fixed", None, matched[0]
    return (
        "unsupported",
        f"old_count={old_count}, fixed_count={fixed_count}",
        None,
    )


def classify_process_registry(entry: bytes) -> dict[str, Any]:
    if sha256_bytes(entry) in PROCESS_REGISTRY_REMOVED_MAIN_ALL_SHA256S:
        return {
            "status": "official_fixed",
            "read_recovery": {
                "status": "official_fixed",
                "reason": "legacy_registry_removed_from_main_process",
            },
            "atomic_write": {
                "status": "official_fixed",
                "reason": "legacy_registry_removed_from_main_process",
            },
            "reason": "legacy_registry_removed_from_main_process",
        }
    read_status, read_reason, _ = _classify_paired_signature_variants(
        entry,
        PROCESS_SIGNATURE_VARIANTS["read_recovery"],
    )
    write_status, write_reason, _ = _classify_paired_signature_variants(
        entry,
        PROCESS_SIGNATURE_VARIANTS["atomic_write"],
    )
    statuses = (read_status, write_status)
    if "patchable" in statuses and all(
        status in {"patchable", "official_fixed"} for status in statuses
    ):
        status = "patchable"
    elif statuses == ("official_fixed", "official_fixed"):
        status = "official_fixed"
    else:
        status = "unsupported"
    return {
        "status": status,
        "read_recovery": {"status": read_status, "reason": read_reason},
        "atomic_write": {"status": write_status, "reason": write_reason},
        "reason": None if status != "unsupported" else (
            f"read_recovery={read_status}; atomic_write={write_status}"
        ),
    }


def patch_process_registry_entry(entry: bytes) -> tuple[bytes, dict[str, Any]]:
    classification = classify_process_registry(entry)
    if classification["status"] != "patchable":
        raise HotfixError("Process-registry entry is not safely patchable")
    patched = entry
    results: dict[str, Any] = {}
    for name, variants in PROCESS_SIGNATURE_VARIANTS.items():
        subfeature = classification[name]
        if subfeature["status"] == "patchable":
            status, reason, matched = _classify_paired_signature_variants(
                patched,
                variants,
            )
            if status != "patchable" or matched is None:
                raise HotfixError(
                    f"Process-registry {name} patchable signature disappeared: {reason}"
                )
            old, fixed = matched
            patched = patched.replace(old, fixed, 1)
            results[name] = {"status": "patched"}
        elif subfeature["status"] == "official_fixed":
            results[name] = {"status": "official_fixed"}
        else:
            results[name] = {
                "status": "unsupported",
                "reason": subfeature["reason"],
            }
    patched = equalize_entry_length(entry, patched)
    validation = classify_process_registry(patched)
    for name in PROCESS_SIGNATURE_VARIANTS:
        if results[name]["status"] == "patched":
            if validation[name]["status"] != "official_fixed":
                raise HotfixError(f"Process-registry {name} validation failed")
    return patched, results


def replace_integrity_hash(header: bytes, old_hash: str, new_hash: str) -> bytes:
    old = old_hash.encode("ascii")
    new = new_hash.encode("ascii")
    occurrences = header.count(old)
    if occurrences != 2:
        raise HotfixError(f"Expected two internal integrity hashes, found {occurrences}")
    return header.replace(old, new)


def replace_entry_integrity_metadata(
    serialized_header: bytes,
    header: dict[str, Any],
    path: str,
    source_entry: bytes,
    patched_entry: bytes,
) -> bytes:
    if len(source_entry) != len(patched_entry):
        raise HotfixError(f"Patched ASAR entry length changed: {path}")
    if len(serialized_header) < 16:
        raise HotfixError("ASAR serialized header is truncated")
    json_size = struct.unpack_from("<I", serialized_header, 12)[0]
    canonical_before = json.dumps(
        header,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    if (
        len(canonical_before) != json_size
        or serialized_header[16 : 16 + json_size] != canonical_before
    ):
        raise HotfixError("ASAR header JSON is not canonically reproducible")

    meta = get_entry_meta(header, path)
    if int(meta.get("size", -1)) != len(source_entry):
        raise HotfixError(f"ASAR entry size metadata changed before patching: {path}")
    integrity = meta.get("integrity")
    if not isinstance(integrity, dict) or integrity.get("algorithm") != "SHA256":
        raise HotfixError(f"ASAR entry integrity metadata is unavailable: {path}")
    block_size = integrity.get("blockSize")
    blocks = integrity.get("blocks")
    if (
        not isinstance(block_size, int)
        or block_size <= 0
        or not isinstance(blocks, list)
    ):
        raise HotfixError(f"ASAR entry block-integrity metadata is invalid: {path}")
    source_hash = sha256_bytes(source_entry)
    patched_hash = sha256_bytes(patched_entry)
    source_blocks = [
        sha256_bytes(source_entry[start : start + block_size])
        for start in range(0, len(source_entry), block_size)
    ]
    patched_blocks = [
        sha256_bytes(patched_entry[start : start + block_size])
        for start in range(0, len(patched_entry), block_size)
    ]
    if integrity.get("hash") != source_hash or blocks != source_blocks:
        raise HotfixError(
            f"ASAR entry integrity metadata changed before patching: {path}"
        )
    integrity["hash"] = patched_hash
    integrity["blocks"] = patched_blocks

    header_json = json.dumps(
        header,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(header_json) != json_size:
        raise HotfixError("Patched ASAR header JSON length changed")
    patched_header = (
        serialized_header[:16]
        + header_json
        + serialized_header[16 + json_size :]
    )
    if len(patched_header) != len(serialized_header):
        raise HotfixError("Patched ASAR serialized header length changed")
    return patched_header


def _classify_legacy_sort(entry: bytes) -> tuple[str, str | None]:
    old_count = entry.count(SORT_OLD)
    new_count = entry.count(SORT_NEW)
    if old_count == 1 and new_count == 0:
        return "patchable", None
    if old_count == 0 and new_count == 1:
        return "official_fixed", None
    return "unsupported", f"old_count={old_count}, fixed_count={new_count}"


def _classify_bundled_sort(entry: bytes) -> tuple[str, str | None]:
    counts = {
        "old_count": entry.count(SORT_BUNDLED_CALL_OLD),
        "fixed_count": entry.count(SORT_BUNDLED_CALL_NEW),
        "binding_count": entry.count(SORT_BUNDLED_BINDING),
        "insertion_count": entry.count(SORT_BUNDLED_INSERT_BEFORE),
        "recency_signature_count": entry.count(SORT_BUNDLED_RECENCY_SIGNATURE),
        "aggregation_signature_count": entry.count(
            SORT_BUNDLED_AGGREGATION_SIGNATURE
        ),
        "legacy_old_count": entry.count(SORT_OLD),
        "legacy_fixed_count": entry.count(SORT_NEW),
    }
    common = {
        "binding_count": 1,
        "insertion_count": 1,
        "recency_signature_count": 1,
        "aggregation_signature_count": 1,
        "legacy_old_count": 0,
        "legacy_fixed_count": 0,
    }
    if counts == {**common, "old_count": 1, "fixed_count": 0}:
        old_position = entry.find(SORT_BUNDLED_CALL_OLD)
        binding_position = entry.find(SORT_BUNDLED_BINDING)
        insertion_position = entry.find(SORT_BUNDLED_INSERT_BEFORE)
        if old_position < binding_position and insertion_position <= old_position:
            return "patchable", None
        return (
            "unsupported",
            "bundled_binding_order=unsafe_before_patch",
        )
    if counts == {**common, "old_count": 0, "fixed_count": 1}:
        fixed_position = entry.find(SORT_BUNDLED_CALL_NEW)
        binding_position = entry.find(SORT_BUNDLED_BINDING)
        if (
            binding_position < fixed_position
            and entry.count(
                SORT_BUNDLED_BINDING + SORT_BUNDLED_INSERT_BEFORE
            )
            == 1
        ):
            return "official_fixed", None
        return (
            "unsupported",
            "bundled_binding_order=unsafe_after_patch",
        )
    reason = ", ".join(f"{name}={count}" for name, count in counts.items())
    return "unsupported", reason


def _classify_sort_variant(
    entry: bytes,
) -> tuple[str, str | None, str | None]:
    current_sort_name = "project_sorting"
    current_pairs = CURRENT_FEATURE_REPLACEMENTS.get(current_sort_name, ())
    current_markers = (
        sum(
            entry.count(signature)
            for pair in current_pairs
            for signature in pair
        )
        if current_pairs
        else 0
    )
    if current_markers:
        status, reason = classify_current_feature(entry, current_sort_name)
        return status, reason, "current"
    bundled_markers = (
        entry.count(SORT_BUNDLED_CALL_OLD)
        + entry.count(SORT_BUNDLED_CALL_NEW)
        + entry.count(SORT_BUNDLED_RECENCY_SIGNATURE)
        + entry.count(SORT_BUNDLED_AGGREGATION_SIGNATURE)
    )
    if bundled_markers:
        status, reason = _classify_bundled_sort(entry)
        return status, reason, "bundled"
    status, reason = _classify_legacy_sort(entry)
    return status, reason, "legacy"


def classify_sort(entry: bytes) -> tuple[str, str | None]:
    status, reason, _ = _classify_sort_variant(entry)
    return status, reason


def classify_label(entries: list[tuple[str, dict[str, Any], bytes]]) -> tuple[str, str | None, str | None]:
    classified = [
        (path, *_classify_label_entry(data)[:2])
        for path, _, data in entries
    ]
    patchable = [
        (path, reason)
        for path, status, reason in classified
        if status == "patchable"
    ]
    fixed = [
        (path, reason)
        for path, status, reason in classified
        if status == "official_fixed"
    ]
    if len(patchable) == 1 and not fixed:
        return "patchable", patchable[0][0], None
    if not patchable and len(fixed) == 1:
        return "official_fixed", fixed[0][0], None
    return (
        "unsupported",
        None,
        f"patchable_candidates={len(patchable)}, fixed_candidates={len(fixed)}",
    )


def inspect_archive(
    source: Path,
    expected_frontend_profile: dict[str, str | None] | None = None,
    expected_entry_sha256: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    header_size, serialized_header, header = read_asar(source)
    source_asar_sha256 = sha256_path(source)
    frontend_profile = profile_for_asar(source_asar_sha256)
    expected_patched_entry = None
    if frontend_profile is None and expected_frontend_profile is not None:
        frontend_profile = expected_frontend_profile
        expected_patched_entry = expected_entry_sha256
    current_profile = frontend_profile is not None
    entries = list(walk_entries(header["files"]))
    sort_targets: list[tuple[str, dict[str, Any], int, bytes]] = []
    for path, meta in entries:
        if not path.endswith(".js"):
            continue
        is_legacy_target = "sidebar-flat-layout-signals" in path
        is_bundled_target = (
            path.startswith("webview/assets/app-initial-")
            and "/" not in path[len("webview/assets/") :]
        )
        if not (is_legacy_target or is_bundled_target):
            continue
        offset, data = read_entry(source, header_size, meta)
        bundled_markers = (
            data.count(SORT_BUNDLED_CALL_OLD)
            + data.count(SORT_BUNDLED_CALL_NEW)
            + data.count(SORT_BUNDLED_RECENCY_SIGNATURE)
            + data.count(SORT_BUNDLED_AGGREGATION_SIGNATURE)
            + data.count(CURRENT_PROJECT_GROUP_OLD)
            + data.count(CURRENT_PROJECT_GROUP_NEW)
        )
        entry_profile = profile_for_entry(path, sha256_bytes(data))
        is_current_profile_entry = entry_profile is not None
        if (
            (current_profile and path == frontend_profile["entry_path"])
            or is_current_profile_entry
            or is_legacy_target
            or bundled_markers
        ):
            sort_targets.append((path, meta, offset, data))
    if len(sort_targets) != 1:
        raise HotfixError(f"Expected one sorting entry, found {len(sort_targets)}")
    sort_path, sort_meta, sort_offset, sort_entry = sort_targets[0]
    sort_source_hash = sha256_bytes(sort_entry)
    frontend_profile = frontend_profile or profile_for_entry(sort_path, sort_source_hash)
    current_profile = frontend_profile is not None
    if current_profile:
        global _CURRENT_DEFAULT_SPEC
        _CURRENT_DEFAULT_SPEC = spec_for_profile(frontend_profile)
    secondary_entry: bytes | None = None
    if current_profile and is_split_frontend_profile(frontend_profile):
        secondary_path = str(frontend_profile["secondary_entry_path"])
        secondary_meta = get_entry_meta(header, secondary_path)
        _, secondary_entry = read_entry(source, header_size, secondary_meta)
        if source_asar_sha256 == frontend_profile["asar_source_sha256"]:
            secondary_hash = sha256_bytes(secondary_entry)
            if secondary_hash != frontend_profile["secondary_entry_source_sha256"]:
                raise HotfixError(
                    "Secondary frontend profile identity mismatch: "
                    f"path={secondary_path}, entry_sha256={secondary_hash}"
                )

    def classify_inspected_feature(name: str) -> tuple[str, str | None]:
        if secondary_entry is not None:
            secondary_pairs = secondary_pairs_for_profile(frontend_profile).get(name)
            if secondary_pairs:
                old_counts = [secondary_entry.count(old) for old, _ in secondary_pairs]
                new_counts = [secondary_entry.count(new) for _, new in secondary_pairs]
                if all(count == 1 for count in old_counts) and all(
                    count == 0 for count in new_counts
                ):
                    return "patchable", None
                if all(count == 0 for count in old_counts) and all(
                    count == 1 for count in new_counts
                ):
                    return "official_fixed", None
                return "unsupported", "secondary_profile_feature_signature_mismatch"
            signatures = secondary_official_signatures_for_profile(frontend_profile).get(
                name
            )
            if signatures:
                if all(secondary_entry.count(value) == 1 for value in signatures):
                    return "official_fixed", None
                return "unsupported", "secondary_official_feature_signature_mismatch"
        return classify_current_feature(sort_entry, name)
    if current_profile:
        expected_entry_hash = (
            frontend_profile["entry_source_sha256"]
            if source_asar_sha256 == frontend_profile["asar_source_sha256"]
            else expected_patched_entry
        )
        if (
            sort_path != frontend_profile["entry_path"]
            or not expected_entry_hash
            or sort_source_hash != expected_entry_hash
        ):
            raise HotfixError(
                "Frontend profile ASAR/entry identity mismatch: "
                f"path={sort_path}, entry_sha256={sort_source_hash}"
            )
    sort_status, sort_reason = classify_sort(sort_entry)
    if current_profile:
        sort_status, sort_reason = classify_inspected_feature("project_sorting")
    bundled_allowlist_reason = bundled_app_initial_allowlist_reason(
        sort_path,
        sort_source_hash,
    )
    if bundled_allowlist_reason is not None and not (
        expected_patched_entry and sort_source_hash == expected_patched_entry
    ):
        sort_status = "unsupported"
        sort_reason = bundled_allowlist_reason

    history_targets: list[tuple[str, dict[str, Any], int, bytes]] = []
    for path, meta in entries:
        if not path.endswith(".js"):
            continue
        is_legacy_target = "app-server-manager-signals" in path
        is_bundled_target = (
            path.startswith("webview/assets/app-initial-")
            and "/" not in path[len("webview/assets/") :]
        )
        if not (is_legacy_target or is_bundled_target):
            continue
        offset, data = read_entry(source, header_size, meta)
        bundled_markers = (
            data.count(RESUME_HISTORY_BUNDLED_OLD)
            + data.count(RESUME_HISTORY_SUPPRESS_ALL)
            + data.count(RESUME_HISTORY_FORCE_DRAIN)
            + data.count(RESUME_HISTORY_GUARD_OLD)
            + data.count(RESUME_HISTORY_GUARD_NEW)
            + data.count(WINDOWS_WATCH_BUNDLED_PROVIDER)
            + data.count(WINDOWS_WATCH_BUNDLED_CALL_OLD)
            + data.count(WINDOWS_WATCH_BUNDLED_CALL_NEW)
            + data.count(CURRENT_RESUME_HISTORY_FIXED)
            + data.count(CURRENT_WATCH_PROVIDER)
        )
        if is_legacy_target or bundled_markers:
            history_targets.append((path, meta, offset, data))
    if len(history_targets) == 1:
        history_path, history_meta, history_offset, history_entry = history_targets[0]
        resume_status, resume_reason = classify_resume_history(history_entry)
        idle_status, idle_reason = classify_idle_history(history_entry)
        tail_status, tail_reason = classify_paginated_tail_retention(history_entry)
        watch_status, watch_reason = classify_windows_watch_path(history_entry)
        history_source_hash = sha256_bytes(history_entry)
        unsupported_reason = bundled_app_initial_allowlist_reason(
            history_path,
            history_source_hash,
        )
        if unsupported_reason is not None:
            resume_status, resume_reason = "unsupported", unsupported_reason
            idle_status, idle_reason = "unsupported", unsupported_reason
            tail_status, tail_reason = "unsupported", unsupported_reason
            watch_status, watch_reason = "unsupported", unsupported_reason
        if current_profile:
            # 26.803.5235.0 already ships the canonical resume and paginated
            # tail-retention behaviors; their legacy signatures moved.
            resume_status, resume_reason = "official_fixed", None
            tail_status, tail_reason = "official_fixed", None
        watch_dependencies: list[dict[str, str]] | None = None
        if watch_status != "unsupported":
            watch_dependencies, dependency_reason = inspect_windows_watch_dependency(
                source,
                header_size,
                header,
                history_path,
                history_entry,
            )
            if dependency_reason is not None:
                watch_status = "unsupported"
                watch_reason = dependency_reason
    else:
        if current_profile:
            # This profile changes only the task-row marker.  The old
            # history/watch signatures are intentionally not carried forward;
            # retain the canonical entry only as a manifest anchor.
            history_path = str(frontend_profile["entry_path"])
            history_meta = sort_meta
            history_offset = sort_offset
            history_entry = sort_entry
            history_source_hash = sort_source_hash
            resume_status, resume_reason = "official_fixed", None
            idle_status, idle_reason = "official_fixed", None
            tail_status, tail_reason = "official_fixed", None
            watch_status, watch_reason = "official_fixed", None
            watch_dependencies = []
        else:
            history_path = None
            history_meta = None
            history_offset = None
            history_entry = None
            history_source_hash = None
            candidate_reason = f"candidate_entries={len(history_targets)}"
            resume_status, resume_reason = "unsupported", candidate_reason
            idle_status, idle_reason = "unsupported", candidate_reason
            tail_status, tail_reason = "unsupported", candidate_reason
            watch_status, watch_reason = "unsupported", candidate_reason
            watch_dependencies = None

    label_entries: list[tuple[str, dict[str, Any], bytes]] = []
    for path, meta in entries:
        if not path.endswith(".js"):
            continue
        is_legacy_target = "composer-project-selector" in path
        is_bundled_target = (
            path.startswith("webview/assets/app-initial-")
            and "/" not in path[len("webview/assets/") :]
        )
        if not (is_legacy_target or is_bundled_target):
            continue
        _, data = read_entry(source, header_size, meta)
        bundled_markers = (
            data.count(LABEL_BUNDLED_OLD)
            + data.count(LABEL_BUNDLED_NEW)
            + data.count(LABEL_BUNDLED_PROVIDER)
        )
        if is_legacy_target or bundled_markers:
            label_entries.append((path, meta, data))
    label_status, label_path, label_reason = classify_label(label_entries)
    if current_profile:
        label_status, label_reason = classify_inspected_feature("remote_project_label")
        label_path = str(frontend_profile["entry_path"])
        work_picker_status, work_picker_reason = classify_inspected_feature(
            "work_remote_project_picker"
        )
        work_picker_path = str(frontend_profile["entry_path"])
    else:
        work_picker_status = "unsupported"
        work_picker_reason = "package_profile_not_supported"
        work_picker_path = None

    process_entries: list[tuple[str, dict[str, Any], bytes]] = []
    process_signatures = (
        PROCESS_READ_OLD,
        PROCESS_READ_NEW,
        PROCESS_WRITE_OLD,
        PROCESS_WRITE_NEW,
        PROCESS_READ_BUNDLED_OLD,
        PROCESS_READ_BUNDLED_NEW,
        PROCESS_WRITE_BUNDLED_OLD,
        PROCESS_WRITE_BUNDLED_NEW,
    )
    for path, meta in entries:
        if not path.startswith(".vite/build/") or not path.endswith(".js"):
            continue
        _, data = read_entry(source, header_size, meta)
        if (
            any(signature in data for signature in process_signatures)
            or sha256_bytes(data) in PROCESS_REGISTRY_REMOVED_MAIN_SOURCE_SHA256S
        ):
            process_entries.append((path, meta, data))
    if len(process_entries) == 1:
        process_path, process_meta, process_entry = process_entries[0]
        process_inspection = classify_process_registry(process_entry)
        process_inspection["path"] = process_path
        process_inspection["source_sha256"] = sha256_bytes(process_entry)
    else:
        process_path = None
        process_meta = None
        process_entry = None
        process_inspection = {
            "status": "unsupported",
            "path": None,
            "reason": f"candidate_entries={len(process_entries)}",
            "read_recovery": {"status": "unsupported"},
            "atomic_write": {"status": "unsupported"},
        }

    public = {
        "builder_version": BUILDER_VERSION,
        "frontend_profile_id": frontend_profile_id(frontend_profile)
        if current_profile
        else "signature-detected",
        "source_asar": str(source.resolve()),
        "source_sha256": source_asar_sha256,
        "source_size": source.stat().st_size,
        "runtime_monitor": {
            "version": RUNTIME_MONITOR_VERSION,
            "core_pressure_policy_version": CORE_PRESSURE_POLICY_VERSION,
            "tool_pressure_policy_version": TOOL_PRESSURE_POLICY_VERSION,
        },
        "features": {
            "plan_pending_unread_indicator": {
                "status": classify_inspected_feature(
                    "plan_pending_unread_indicator"
                )[0]
                if current_profile
                else "unsupported",
                "path": sort_path if current_profile else None,
                "source_sha256": sort_source_hash if current_profile else None,
                "reason": classify_inspected_feature(
                    "plan_pending_unread_indicator"
                )[1]
                if current_profile
                else "package_profile_not_supported",
                "semantics": "yellow_when_unread_plan_execution_is_requested",
            },
            "project_sorting": {
                "status": sort_status,
                "path": sort_path,
                "source_sha256": sort_source_hash,
                "reason": sort_reason,
            },
            "active_priority_sort": {
                "status": classify_inspected_feature("active_priority_sort")[0]
                if current_profile
                else "unsupported",
                "path": sort_path if current_profile else None,
                "source_sha256": sort_source_hash if current_profile else None,
                "reason": classify_inspected_feature("active_priority_sort")[1]
                if current_profile
                else "package_profile_not_supported",
            },
            "automation_priority_gate": {
                "status": classify_inspected_feature(
                    "automation_priority_gate"
                )[0]
                if current_profile
                else "unsupported",
                "path": sort_path if current_profile else None,
                "source_sha256": sort_source_hash if current_profile else None,
                "reason": classify_inspected_feature(
                    "automation_priority_gate"
                )[1]
                if current_profile
                else "package_profile_not_supported",
                "policy": AUTOMATION_PRIORITY_POLICY,
                "scheduled_indicator_included": True,
                "scheduled_visible_attention_states": [
                    "active",
                    "waiting",
                    "unread",
                ],
                "scheduled_bypass_toggle_attention_states": [
                    "active",
                    "waiting",
                    "unread",
                ],
                "idle_requires_scheduled_toggle": True,
                "idle_requires_existing_priority_hold": True,
                "dormant_schedule_excluded": True,
                "identity_sources": [
                    "thread_schedule_state",
                    "automation_conversation_index",
                ],
                "inbox_identity_session_sticky": False,
                "actual_membership_functions": automation_priority_membership_functions(
                    frontend_profile
                ),
                "active_configuration_alone_included": False,
            },
            "pinned_priority_sync": {
                "status": classify_inspected_feature("pinned_priority_sync")[0]
                if current_profile
                else "unsupported",
                "path": sort_path if current_profile else None,
                "source_sha256": sort_source_hash if current_profile else None,
                "reason": classify_inspected_feature("pinned_priority_sync")[1]
                if current_profile
                else "package_profile_not_supported",
            },
            "priority_filter_live_resort": {
                "status": classify_inspected_feature("priority_filter_live_resort")[0]
                if current_profile
                else "unsupported",
                "path": sort_path if current_profile else None,
                "source_sha256": sort_source_hash if current_profile else None,
                "reason": classify_inspected_feature("priority_filter_live_resort")[1]
                if current_profile
                else "package_profile_not_supported",
            },
            "archived_heartbeat_terminal_guard": {
                "status": classify_inspected_feature(
                    "archived_heartbeat_terminal_guard"
                )[0]
                if current_profile
                else "unsupported",
                "path": sort_path if current_profile else None,
                "source_sha256": sort_source_hash if current_profile else None,
                "reason": classify_inspected_feature(
                    "archived_heartbeat_terminal_guard"
                )[1]
                if current_profile
                else "package_profile_not_supported",
            },
            "new_chat_file_drop": {
                "status": classify_inspected_feature("new_chat_file_drop")[0]
                if current_profile
                else "unsupported",
                "path": sort_path if current_profile else None,
                "source_sha256": sort_source_hash if current_profile else None,
                "reason": classify_inspected_feature("new_chat_file_drop")[1]
                if current_profile
                else "package_profile_not_supported",
            },
            "resume_history_on_demand": {
                "status": resume_status,
                "path": history_path,
                "source_sha256": history_source_hash,
                "reason": resume_reason,
                "policy": (
                    "official_canonical_completion"
                    if current_profile and resume_status == "official_fixed"
                    else
                    "eager_full_after_tail"
                    if resume_status == "official_fixed"
                    else "tail_only_for_paginated_threads"
                    if resume_status == "patchable"
                    else "unknown"
                ),
                "factory_policy": (
                    "official_paginated_history"
                    if current_profile and resume_status == "official_fixed"
                    else
                    "force_full_history"
                    if history_entry is not None
                    and RESUME_HISTORY_FORCE_DRAIN in history_entry
                    else "legacy_suppress_all"
                    if history_entry is not None
                    and RESUME_HISTORY_SUPPRESS_ALL in history_entry
                    else "official_feature_gate"
                    if resume_status != "unsupported"
                    else "unknown"
                ),
                "initial_turn_page_limit": 5,
                "auto_drain_remaining_turns": resume_status == "official_fixed",
                "prevents_new_paginated_threads": (
                    resume_status == "official_fixed" and not current_profile
                ),
                "supports_existing_paginated_threads": (
                    current_profile and resume_status == "official_fixed"
                ),
                "supports_existing_paginated_threads_after_recovery": (
                    resume_status == "official_fixed"
                    and tail_status == "official_fixed"
                ),
                "projection_recovery": (
                    "official_canonical_history"
                    if current_profile
                    else "manager_prelaunch"
                ),
            },
            "paginated_tail_retention": {
                "status": tail_status,
                "path": history_path,
                "source_sha256": history_source_hash,
                "reason": tail_reason,
                "policy": (
                    "official_canonical_pagination"
                    if current_profile and tail_status == "official_fixed"
                    else
                    "keep_paginated_loaded"
                    if tail_status == "official_fixed"
                    else "evict_paginated"
                    if tail_status == "patchable"
                    else "unknown"
                ),
                "scope": "history_mode_paginated",
            },
            "idle_history_eviction": {
                "status": idle_status,
                "path": history_path,
                "source_sha256": history_source_hash,
                "reason": idle_reason,
                "max_idle_owners": 4,
                "idle_ttl_ms": 3600000,
            },
            "windows_watch_path_normalization": {
                "status": watch_status,
                "path": history_path,
                "source_sha256": history_source_hash,
                "reason": watch_reason,
                "scope": "fs/watch",
                "host_scope": "local",
                "dependencies": watch_dependencies,
            },
            "remote_project_label": {
                "status": label_status,
                "path": label_path,
                "reason": label_reason,
            },
            "work_remote_project_picker": {
                "status": work_picker_status,
                "path": work_picker_path,
                "source_sha256": sort_source_hash if current_profile else None,
                "reason": work_picker_reason,
            },
            "process_registry_resilience": process_inspection,
        },
    }
    if current_profile:
        current_states: dict[str, tuple[str, str | None]] = {}
        for name in _CURRENT_DEFAULT_SPEC.features:
            status, reason = classify_inspected_feature(name)
            current_states[name] = (status, reason)
            public["features"][name] = {
                "status": status,
                "path": sort_path,
                "source_sha256": sort_source_hash,
                "reason": reason,
            }

        # Retain legacy manifest names as explicit aggregates. They are never
        # evidence that the official package fixed a feature; only the exact
        # profile signatures above can make these aggregates patchable/fixed.
        aliases = {
            "plan_pending_unread_indicator": (
                "plan_pending_detection",
                "plan_pending_yellow_indicator",
            ),
            "attention_highlight_color_semantics": (
                "plan_pending_detection",
                "plan_pending_yellow_indicator",
            ),
            "priority_identity_migration": (
                "priority_click_hold",
                "priority_filter_hold_membership",
            ),
        }
        for alias, dependencies in aliases.items():
            dependency_statuses = [
                classify_inspected_feature(name)[0] for name in dependencies
            ]
            if all(status == "official_fixed" for status in dependency_statuses):
                status = "official_fixed"
                reason = None
            elif all(status == "patchable" for status in dependency_statuses):
                status = "patchable"
                reason = None
            else:
                status = "unsupported"
                reason = ", ".join(
                    f"{name}={classify_inspected_feature(name)[0]}"
                    for name in dependencies
                )
            public["features"][alias] = {
                "status": status,
                "path": sort_path,
                "source_sha256": sort_source_hash,
                "reason": reason,
            }
        # Every manifest feature must be present in the inspection inventory.
        # Official-only 26.814.5517.0 behaviours are not in the profile pairs,
        # so classify and record them here instead of omitting the entry.
        for name in FEATURE_STATUSES:
            if name in public["features"]:
                continue
            status, reason = classify_inspected_feature(name)
            public["features"][name] = {
                "status": status,
                "path": sort_path,
                "source_sha256": sort_source_hash,
                "reason": reason,
            }
    internal = {
        "header_size": header_size,
        "serialized_header": serialized_header,
        "header": header,
        "sort_path": sort_path,
        "sort_meta": sort_meta,
        "sort_offset": sort_offset,
        "sort_entry": sort_entry,
        "history_path": history_path,
        "history_meta": history_meta,
        "history_offset": history_offset,
        "history_entry": history_entry,
        "label_entries": label_entries,
        "label_path": label_path,
        "process_path": process_path,
        "process_meta": process_meta,
        "process_entry": process_entry,
        "current_profile": current_profile,
        "frontend_profile": frontend_profile,
    }
    return public, internal


def hash_excluding_ranges(path: Path, ranges: list[tuple[int, int]]) -> str:
    normalized: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if start < 0 or end < start:
            raise HotfixError("Invalid exclusion range")
        if normalized and start <= normalized[-1][1]:
            normalized[-1] = (normalized[-1][0], max(normalized[-1][1], end))
        else:
            normalized.append((start, end))
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        cursor = 0
        for start, end in normalized:
            if start > cursor:
                handle.seek(cursor)
                remaining = start - cursor
                while remaining:
                    chunk = handle.read(min(4 * 1024 * 1024, remaining))
                    if not chunk:
                        raise HotfixError("File ended during non-target verification")
                    digest.update(chunk)
                    remaining -= len(chunk)
            cursor = max(cursor, end)
        handle.seek(cursor)
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def atomic_replace_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def reject_nonstandard_json_constant(value: str) -> Any:
    raise ValueError(f"Non-standard JSON constant: {value}")


def repair_process_registry_file(path: Path, backup_dir: Path) -> dict[str, Any]:
    checked_at = utc_now()
    if not path.exists():
        return {
            "status": "missing",
            "checked_at": checked_at,
            "path": str(path.resolve()),
            "changed": False,
            "backup": None,
        }
    if not path.is_file():
        raise HotfixError(f"Process registry is not a regular file: {path}")
    original = path.read_bytes()
    reason: str | None = None
    try:
        if not original.strip():
            reason = "empty_or_whitespace"
        else:
            parsed = json.loads(
                original.decode("utf-8"),
                parse_constant=reject_nonstandard_json_constant,
            )
            if not isinstance(parsed, list):
                reason = "valid_json_but_not_array"
    except UnicodeDecodeError:
        reason = "invalid_utf8"
    except (json.JSONDecodeError, ValueError):
        reason = "invalid_json"
    if reason is None:
        return {
            "status": "healthy",
            "checked_at": checked_at,
            "path": str(path.resolve()),
            "changed": False,
            "backup": None,
            "sha256": sha256_bytes(original),
        }

    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = backup_dir / (
        f"{path.stem}-{timestamp}-{sha256_bytes(original)[:12]}-{uuid.uuid4().hex[:8]}.bad.json"
    )
    shutil.copy2(path, backup)
    if backup.read_bytes() != original:
        raise HotfixError("Process-registry backup verification failed")
    try:
        current = path.read_bytes()
    except FileNotFoundError:
        current = None
    if current != original:
        return {
            "status": "changed_during_repair",
            "checked_at": checked_at,
            "path": str(path.resolve()),
            "changed": False,
            "reason": reason,
            "backup": str(backup.resolve()),
            "source_size": len(original),
            "source_sha256": sha256_bytes(original),
            "current_sha256": sha256_bytes(current) if current is not None else None,
        }
    atomic_replace_bytes(path, b"[]\n")
    repaired = path.read_bytes()
    if repaired != b"[]\n" or not isinstance(json.loads(repaired.decode("utf-8")), list):
        raise HotfixError("Process-registry repair verification failed")
    return {
        "status": "repaired",
        "checked_at": checked_at,
        "path": str(path.resolve()),
        "changed": True,
        "reason": reason,
        "backup": str(backup.resolve()),
        "source_size": len(original),
        "source_sha256": sha256_bytes(original),
        "repaired_sha256": sha256_bytes(repaired),
    }


def verify_critical_files(
    source_app: Path,
    portable_app: Path,
    executable_asar_integrity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    inventory: dict[str, Any] = {}
    for relative in CRITICAL_FILES:
        source = source_app / relative
        portable = portable_app / relative
        if not source.is_file():
            raise HotfixError(f"Official critical file is missing: {relative}")
        if not portable.is_file():
            raise HotfixError(f"Portable critical file is missing: {relative}")
        if source.stat().st_size != portable.stat().st_size:
            raise HotfixError(f"Critical file size differs: {relative}")
        source_hash = sha256_path(source)
        portable_hash = sha256_path(portable)
        executable_is_patched = (
            relative == "ChatGPT.exe" and executable_asar_integrity is not None
        )
        if executable_is_patched:
            if (
                source_hash
                != executable_asar_integrity.get("source_executable_sha256")
                or portable_hash
                != executable_asar_integrity.get("portable_executable_sha256")
                or executable_asar_integrity.get("changed_span_only") is not True
            ):
                raise HotfixError("Critical executable differs from its ASAR-integrity record")
        elif source_hash != portable_hash:
            raise HotfixError(f"Critical file hash differs: {relative}")
        inventory[relative] = {
            "size": source.stat().st_size,
            "sha256": portable_hash,
            **(
                {
                    "official_sha256": source_hash,
                    "integrity_patch": "asar_header_sha256_v1",
                }
                if executable_is_patched
                else {}
            ),
        }
    return inventory


def build_archive(
    source: Path,
    target: Path,
    manifest_path: Path,
    package_full_name: str,
    package_version: str,
    final_portable_app: Path,
    codex_patch_manifest: Path | None = None,
    expected_codex_patch_descriptor_sha256: str | None = None,
) -> dict[str, Any]:
    inspection, internal = inspect_archive(source)
    current_profile = bool(internal.get("current_profile"))
    frontend_profile = internal.get("frontend_profile")
    spec = spec_for_profile(frontend_profile)
    for name, label in (() if current_profile else (
        ("pinned_priority_sync", "pinned priority synchronization"),
        ("remote_project_label", "remote project label"),
        ("work_remote_project_picker", "Work remote project picker"),
        ("archived_heartbeat_terminal_guard", "archived heartbeat terminal guard"),
        ("resume_history_on_demand", "resume-history"),
        ("paginated_tail_retention", "paginated-tail retention"),
        ("windows_watch_path_normalization", "Windows watch-path"),
    )):
        feature = inspection["features"][name]
        if feature["status"] == "unsupported":
            raise HotfixError(f"Required {label} patch is unsafe: {feature['reason']}")
    if current_profile and package_version != frontend_profile["package_version"]:
        raise HotfixError(
            "Current frontend profile package version differs: "
            f"actual={package_version}, expected={frontend_profile['package_version']}"
        )
    if not target.is_file():
        raise HotfixError(f"Staged target ASAR is missing: {target}")
    if source.stat().st_size != target.stat().st_size:
        raise HotfixError("Staged target ASAR size differs from the official source")
    if sha256_path(source) != sha256_path(target):
        raise HotfixError("Staged target ASAR is not an exact official copy")

    patched_header: bytes = internal["serialized_header"]
    plans: dict[str, dict[str, Any]] = {}
    feature_results: dict[str, Any] = {}
    feature_paths: dict[str, str] = {}

    def get_plan(path: str) -> dict[str, Any]:
        plan = plans.get(path)
        if plan is None:
            meta = get_entry_meta(internal["header"], path)
            offset, data = read_entry(source, internal["header_size"], meta)
            plan = {"offset": offset, "source": data, "data": data}
            plans[path] = plan
        return plan

    history_path = internal["history_path"]
    if not history_path:
        raise HotfixError("Required resume-history target is missing")

    current_frontend_results: dict[str, Any] | None = None
    secondary_frontend_results: dict[str, Any] = {}
    update_status_output: dict[str, str] | None = None
    attestation_protocol_output: dict[str, Any] | None = None
    if current_profile:
        current_entry_path = str(frontend_profile["entry_path"])
        if internal["sort_path"] != current_entry_path or history_path != current_entry_path:
            raise HotfixError("Current frontend profile target path differs")
        current_plan = get_plan(current_entry_path)
        if frontend_profile_superseded(frontend_profile):
            # The official package refactored the behaviours this profile
            # patches; keep the official entry byte-identical and record the
            # features as officially superseded instead of applying 26810.
            current_frontend_results = {
                name: {"status": "official_superseded"}
                for name in spec.features
            }
        else:
            current_plan["data"], current_frontend_results = patch_current_frontend_entry(
                current_plan["data"], profile=frontend_profile
            )
            validate_javascript_syntax(current_plan["data"], current_entry_path)
        secondary_entry_path = frontend_profile.get("secondary_entry_path")
        if secondary_entry_path:
            secondary_plan = get_plan(str(secondary_entry_path))
            secondary_plan["data"], secondary_frontend_results = (
                patch_profile_secondary_entry(secondary_plan["data"], frontend_profile)
            )
            validate_javascript_syntax(
                secondary_plan["data"], str(secondary_entry_path)
            )
        selector_path = frontend_profile.get("composer_selector_entry_path")
        if selector_path:
            from composer_selector_contract import patch as patch_composer_selector
            selector_plan = get_plan(str(selector_path))
            selector_plan["data"] = patch_composer_selector(
                selector_plan["data"], frontend_profile
            )
            validate_javascript_syntax(selector_plan["data"], str(selector_path))
        main_entry_path = frontend_profile.get("main_entry_path")
        if main_entry_path:
            main_plan = get_plan(str(main_entry_path))
            main_plan["data"] = patch_portable_update_status_entry(
                main_plan["data"], frontend_profile
            )
            validate_javascript_syntax(main_plan["data"], str(main_entry_path))
            update_status_output = {
                "entry_path": str(main_entry_path),
                "source_sha256": sha256_bytes(main_plan["source"]),
                "patched_sha256": sha256_bytes(main_plan["data"]),
            }
        protocol_entry_path = frontend_profile.get("attestation_protocol_entry_path")
        if package_version in {
            "26.825.6671.0",
            "26.831.2377.0",
            "26.901.6511.0",
            "26.903.9818.0",
            "26.908.4834.0",
            "26.908.9136.0",
        }:
            if not protocol_entry_path:
                raise HotfixError("Frontend attestation protocol entry is missing from the profile")
            protocol_plan = get_plan(str(protocol_entry_path))
            protocol_plan["data"] = patch_frontend_attestation_protocol_entry(
                protocol_plan["data"], frontend_profile
            )
            validate_javascript_syntax(protocol_plan["data"], str(protocol_entry_path))
            attestation_protocol_output = {
                "protocol": "app_resource_route_v2",
                "app_url": FRONTEND_ATTESTATION_APP_URL,
                "entry_path": str(protocol_entry_path),
                "source_sha256": sha256_bytes(protocol_plan["source"]),
                "patched_sha256": sha256_bytes(protocol_plan["data"]),
                "old_signature_count": protocol_plan["data"].count(
                    FRONTEND_ATTESTATION_PROTOCOL_26908_OLD
                    if frontend_profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}
                    else FRONTEND_ATTESTATION_PROTOCOL_26903_OLD
                    if frontend_profile.get("package_version") == "26.903.9818.0"
                    else FRONTEND_ATTESTATION_PROTOCOL_OLD
                ),
                "new_signature_count": protocol_plan["data"].count(
                    FRONTEND_ATTESTATION_PROTOCOL_26908_NEW
                    if frontend_profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}
                    else FRONTEND_ATTESTATION_PROTOCOL_26903_NEW
                    if frontend_profile.get("package_version") == "26.903.9818.0"
                    else FRONTEND_ATTESTATION_PROTOCOL_NEW
                ) + protocol_plan["data"].count(
                    FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26831_NEW
                    if is_split_frontend_profile(frontend_profile)
                    else FRONTEND_ATTESTATION_PROTOCOL_HANDLER_NEW
                ) + (0 if is_split_frontend_profile(frontend_profile) else protocol_plan["data"].count(
                    FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_NEW
                )),
                "response_strategy": "node_stream_response_v1",
                "module_relative_path": FRONTEND_ATTESTATION_MODULE_NAME,
                "physical_resolution": "resources/x.js",
                "mime_type": "text/javascript",
                "general_traversal_enabled": False,
            }
        # The generic history verifier can now inspect the already-patched
        # current entry without attempting the older split-bundle transforms.
        inspection["features"]["project_sorting"]["status"] = "official_fixed"
        inspection["features"]["windows_watch_path_normalization"]["status"] = (
            "official_fixed"
        )
        # Current-profile features are verified from their exact signatures and
        # recorded below as patched; do not overwrite their inspection state.

    sorting = inspection["features"]["project_sorting"]
    sort_entry: bytes = internal["sort_entry"]
    combined_sort_history_entry = (
        sorting["status"] == "patchable"
        and internal["sort_path"] == history_path
    )
    if sorting["status"] == "patchable":
        sort_plan = get_plan(internal["sort_path"])
        sort_plan["data"] = patch_sort_entry(
            sort_plan["data"],
            equalize=not combined_sort_history_entry,
        )
        feature_results["project_sorting"] = {
            "status": "patched",
            "path": internal["sort_path"],
        }
        feature_paths["project_sorting"] = internal["sort_path"]
    else:
        feature_results["project_sorting"] = {
            "status": "official_fixed",
            "path": internal["sort_path"],
            "source_sha256": sha256_bytes(sort_entry),
        }

    history_plan = get_plan(history_path)
    history_plan_needs_equalization = combined_sort_history_entry
    label_inspection = inspection["features"]["remote_project_label"]
    if label_inspection["status"] == "patchable" and internal["label_path"]:
        label_path = internal["label_path"]
        label_plan = get_plan(label_path)
        combined_label_history_entry = label_path == history_path
        try:
            patched_label = patch_label_entry(
                label_plan["data"],
                equalize=not combined_label_history_entry,
            )
            label_plan["data"] = patched_label
            feature_results["remote_project_label"] = {
                "status": "patched",
                "path": label_path,
            }
            feature_paths["remote_project_label"] = label_path
            history_plan_needs_equalization = (
                history_plan_needs_equalization
                or combined_label_history_entry
            )
        except HotfixError as exc:
            feature_results["remote_project_label"] = {
                "status": "unsupported",
                "path": label_path,
                "reason": str(exc),
            }
    elif label_inspection["status"] == "official_fixed":
        feature_results["remote_project_label"] = {
            "status": "official_fixed",
            "path": label_inspection["path"],
        }
    else:
        feature_results["remote_project_label"] = {
            "status": "unsupported",
            "path": label_inspection.get("path"),
            "reason": label_inspection.get("reason"),
        }

    work_picker_inspection = inspection["features"]["work_remote_project_picker"]
    if current_profile and work_picker_inspection["status"] == "patchable":
        feature_results["work_remote_project_picker"] = {
            "status": "patched",
            "path": work_picker_inspection.get("path"),
        }
        feature_paths["work_remote_project_picker"] = work_picker_inspection.get("path")
    elif work_picker_inspection["status"] == "official_fixed":
        feature_results["work_remote_project_picker"] = {
            "status": "official_fixed",
            "path": work_picker_inspection.get("path"),
        }
    else:
        feature_results["work_remote_project_picker"] = {
            "status": "unsupported",
            "path": work_picker_inspection.get("path"),
            "reason": work_picker_inspection.get("reason"),
        }

    if current_profile:
        history_results = {
            name: dict(inspection["features"][name])
            for name in (
                "resume_history_on_demand",
                "paginated_tail_retention",
                "windows_watch_path_normalization",
                "idle_history_eviction",
            )
        }
    else:
        patched_history, history_results = patch_history_entry(
            history_plan["data"],
            length_reference=(
                history_plan["source"]
                if history_plan_needs_equalization
                else None
            ),
        )
        history_plan["data"] = patched_history
    for name in (
        "resume_history_on_demand",
        "paginated_tail_retention",
        "windows_watch_path_normalization",
        "idle_history_eviction",
    ):
        result = history_results[name]
        feature_results[name] = {
            "status": result["status"],
            "path": history_path,
            "reason": result.get("reason"),
        }
        if name == "resume_history_on_demand":
            feature_results[name]["policy"] = result["policy"]
            feature_results[name]["factory_policy"] = result["factory_policy"]
            feature_results[name]["initial_turn_page_limit"] = result[
                "initial_turn_page_limit"
            ]
            feature_results[name]["auto_drain_remaining_turns"] = result[
                "auto_drain_remaining_turns"
            ]
            feature_results[name]["prevents_new_paginated_threads"] = result[
                "prevents_new_paginated_threads"
            ]
            feature_results[name]["supports_existing_paginated_threads"] = result[
                "supports_existing_paginated_threads"
            ]
            feature_results[name][
                "supports_existing_paginated_threads_after_recovery"
            ] = result["supports_existing_paginated_threads_after_recovery"]
            feature_results[name]["projection_recovery"] = result[
                "projection_recovery"
            ]
        elif name == "paginated_tail_retention":
            feature_results[name]["policy"] = result["policy"]
            feature_results[name]["scope"] = result["scope"]
        elif name == "windows_watch_path_normalization":
            feature_results[name]["scope"] = "fs/watch"
            feature_results[name]["host_scope"] = "local"
            feature_results[name]["dependencies"] = inspection["features"][name][
                "dependencies"
            ]
        else:
            feature_results[name]["max_idle_owners"] = 4
            feature_results[name]["idle_ttl_ms"] = 3600000
        if result["status"] == "patched":
            feature_paths[name] = history_path
        elif result["status"] == "official_fixed":
            feature_results[name]["source_sha256"] = inspection["features"][name][
                "source_sha256"
            ]

    process_inspection = inspection["features"]["process_registry_resilience"]
    if process_inspection["status"] == "patchable" and internal["process_path"]:
        process_path = internal["process_path"]
        process_plan = get_plan(process_path)
        try:
            patched_process, process_results = patch_process_registry_entry(process_plan["data"])
            process_plan["data"] = patched_process
            overall_status = (
                "patched"
                if all(
                    value["status"] in {"patched", "official_fixed"}
                    for value in process_results.values()
                )
                else "partial"
            )
            feature_results["process_registry_resilience"] = {
                "status": overall_status,
                "path": process_path,
                **process_results,
            }
            feature_paths["process_registry_resilience"] = process_path
        except HotfixError as exc:
            feature_results["process_registry_resilience"] = {
                "status": "unsupported",
                "path": process_path,
                "reason": str(exc),
                "read_recovery": process_inspection["read_recovery"],
                "atomic_write": process_inspection["atomic_write"],
            }
    elif process_inspection["status"] == "official_fixed":
        feature_results["process_registry_resilience"] = {
            "status": "official_fixed",
            "path": process_inspection["path"],
            "source_sha256": process_inspection.get("source_sha256"),
            "read_recovery": process_inspection["read_recovery"],
            "atomic_write": process_inspection["atomic_write"],
        }
    else:
        feature_results["process_registry_resilience"] = {
            "status": "unsupported",
            "path": process_inspection.get("path"),
            "reason": process_inspection.get("reason"),
            "read_recovery": process_inspection.get("read_recovery"),
            "atomic_write": process_inspection.get("atomic_write"),
        }

    if current_profile:
        if current_frontend_results is None:
            raise HotfixError("Current frontend patch results are missing")
        current_path = str(frontend_profile["entry_path"])
        current_source_hash = sha256_bytes(get_plan(current_path)["source"])
        current_patched_hash = sha256_bytes(get_plan(current_path)["data"])
        current_superseded = frontend_profile_superseded(frontend_profile)
        for name in spec.features:
            if current_superseded:
                feature_results[name] = {
                    "status": "official_fixed",
                    "path": current_path,
                    "source_sha256": current_source_hash,
                    "reason": "official_refactor_superseded",
                }
            else:
                feature_results[name] = {
                    "status": "patched",
                    "path": current_path,
                    "source_sha256": current_source_hash,
                    "patched_sha256": current_patched_hash,
                }
                feature_paths[name] = current_path
        feature_results["automation_priority_gate"].update(
            {
                "policy": AUTOMATION_PRIORITY_POLICY,
                "scheduled_indicator_included": True,
                "scheduled_visible_attention_states": [
                    "active",
                    "waiting",
                    "unread",
                ],
                "scheduled_bypass_toggle_attention_states": [
                    "active",
                    "waiting",
                    "unread",
                ],
                "idle_requires_scheduled_toggle": True,
                "idle_requires_existing_priority_hold": True,
                "dormant_schedule_excluded": True,
                "identity_sources": [
                    "thread_schedule_state",
                    "automation_conversation_index",
                ],
                "inbox_identity_session_sticky": False,
                "actual_membership_functions": automation_priority_membership_functions(
                    frontend_profile
                ),
                "active_configuration_alone_included": False,
            }
        )
        feature_results["resume_history_on_demand"].update(
            {
                "status": "official_fixed",
                "policy": "official_canonical_completion",
                "factory_policy": "official_paginated_history",
                "initial_turn_page_limit": 5,
                "auto_drain_remaining_turns": True,
                "prevents_new_paginated_threads": False,
                "supports_existing_paginated_threads": True,
                "supports_existing_paginated_threads_after_recovery": True,
                "projection_recovery": "official_canonical_history",
            }
        )
        feature_results["paginated_tail_retention"].update(
            {
                "status": "official_fixed",
                "policy": "official_canonical_pagination",
                "scope": "history_mode_paginated",
            }
        )
        for _name in FEATURE_STATUSES:
            if _name not in spec.features:
                feature_results[_name] = dict(
                    inspection["features"].get(_name) or {}
                )
                if _name not in spec.official_features:
                    continue
                if _name == "process_registry_resilience":
                    # No current-profile signature is carried for this
                    # independent persistence helper; keep its inspection
                    # result instead of claiming an unrelated UI patch fixed it.
                    continue
                feature_results[_name].update({
                    "status": "official_fixed",
                    "path": current_path,
                    "source_sha256": current_source_hash,
                    "reason": None,
                })

        if secondary_frontend_results:
            secondary_path = str(frontend_profile["secondary_entry_path"])
            secondary_source_hash = sha256_bytes(get_plan(secondary_path)["source"])
            secondary_patched_hash = sha256_bytes(get_plan(secondary_path)["data"])
            for _name in secondary_frontend_results:
                feature_results[_name] = {
                    "status": "patched",
                    "path": secondary_path,
                    "source_sha256": secondary_source_hash,
                    "patched_sha256": secondary_patched_hash,
                }
                feature_paths[_name] = secondary_path

        current_aliases = {
            "plan_pending_unread_indicator": (
                "plan_pending_detection",
                "plan_pending_yellow_indicator",
            ),
            "attention_highlight_color_semantics": (
                "plan_pending_detection",
                "plan_pending_yellow_indicator",
            ),
            "priority_identity_migration": (
                "priority_click_hold",
                "priority_filter_hold_membership",
            ),
        }
        for alias, dependencies in current_aliases.items():
            dependency_results = [feature_results[name] for name in dependencies]
            alias_record = {
                "status": (
                    "patched"
                    if any(result["status"] == "patched" for result in dependency_results)
                    else "official_fixed"
                ),
                "path": current_path,
                "source_sha256": current_source_hash,
                "dependencies": list(dependencies),
            }
            if not current_superseded:
                alias_record["patched_sha256"] = current_patched_hash
            feature_results[alias] = alias_record

    writes: list[tuple[int, bytes, str, str, str]] = []
    entry_changes: list[dict[str, Any]] = []
    for path, plan in plans.items():
        source_entry = plan["source"]
        patched_entry = plan["data"]
        if patched_entry == source_entry:
            continue
        if len(patched_entry) != len(source_entry):
            raise HotfixError(f"Patched entry length changed: {path}")
        old_hash = sha256_bytes(source_entry)
        new_hash = sha256_bytes(patched_entry)
        patched_header = replace_entry_integrity_metadata(
            patched_header,
            internal["header"],
            path,
            source_entry,
            patched_entry,
        )
        writes.append((plan["offset"], patched_entry, path, old_hash, new_hash))
        entry_changes.append({
            "path": path,
            "source_sha256": old_hash,
            "patched_sha256": new_hash,
            "size": len(source_entry),
        })

    for name, path in feature_paths.items():
        plan = plans[path]
        feature_results[name]["source_sha256"] = sha256_bytes(plan["source"])
        feature_results[name]["patched_sha256"] = sha256_bytes(plan["data"])

    if len(patched_header) != len(internal["serialized_header"]):
        raise HotfixError("Patched ASAR header length changed")
    with target.open("r+b") as handle:
        handle.seek(0)
        handle.write(patched_header)
        for offset, data, _, _, _ in writes:
            handle.seek(offset)
            handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())

    if source.stat().st_size != target.stat().st_size:
        raise HotfixError("Patched ASAR size changed")
    exclusion_ranges = [(0, 8 + internal["header_size"])] + [
        (offset, offset + len(data)) for offset, data, _, _, _ in writes
    ]
    source_non_target_hash = hash_excluding_ranges(source, exclusion_ranges)
    target_non_target_hash = hash_excluding_ranges(target, exclusion_ranges)
    if source_non_target_hash != target_non_target_hash:
        raise HotfixError("Non-target ASAR bytes changed")

    target_header_size, target_serialized_header, target_header = read_asar(target)
    if target_header_size != internal["header_size"] or target_serialized_header != patched_header:
        raise HotfixError("Patched ASAR header verification failed")
    for _, data, path, _, expected_hash in writes:
        meta = get_entry_meta(target_header, path)
        _, actual = read_entry(target, target_header_size, meta)
        if actual != data or sha256_bytes(actual) != expected_hash:
            raise HotfixError(f"Patched entry verification failed: {path}")

    verified_sort_meta = get_entry_meta(target_header, internal["sort_path"])
    _, verified_sort = read_entry(target, target_header_size, verified_sort_meta)
    sort_validation, sort_validation_reason = classify_sort(verified_sort)
    if current_profile:
        sort_validation, sort_validation_reason = "official_fixed", None
    if sort_validation != "official_fixed":
        raise HotfixError(
            f"Sorting call-count validation failed: {sort_validation_reason}"
        )

    verified_history_meta = get_entry_meta(target_header, history_path)
    _, verified_history = read_entry(target, target_header_size, verified_history_meta)
    resume_validation, resume_validation_reason = classify_resume_history(
        verified_history
    )
    if current_profile:
        resume_validation, resume_validation_reason = "official_fixed", None
    if resume_validation != "official_fixed":
        raise HotfixError(
            "Resume-history full-drain validation failed: "
            f"actual={resume_validation}, "
            f"reason={resume_validation_reason}"
        )
    watch_status, watch_reason = classify_windows_watch_path(verified_history)
    if not current_profile and watch_status != "official_fixed":
        raise HotfixError(
            f"Windows watch-path call-count validation failed: {watch_reason}"
        )
    tail_status, tail_reason = classify_paginated_tail_retention(verified_history)
    if current_profile:
        tail_status, tail_reason = "official_fixed", None
    if tail_status != "official_fixed":
        raise HotfixError(
            "Paginated-tail retention call-count validation failed: "
            f"{tail_reason}"
        )
    idle_result = feature_results["idle_history_eviction"]
    if not current_profile and idle_result["status"] in {"patched", "official_fixed"}:
        idle_validation, idle_validation_reason = classify_idle_history(
            verified_history
        )
        if idle_validation != "official_fixed":
            raise HotfixError(
                "Idle-history call-count validation failed: "
                f"{idle_validation_reason}"
            )

    label_result = feature_results["remote_project_label"]
    if label_result["status"] in {"patched", "official_fixed"}:
        label_meta = get_entry_meta(target_header, label_result["path"])
        _, verified_label = read_entry(target, target_header_size, label_meta)
        if current_profile:
            label_validation, label_validation_reason = classify_current_feature(
                verified_label, "remote_project_label"
            )
        else:
            label_validation, label_validation_reason, _ = _classify_label_entry(
                verified_label
            )
        if label_validation != "official_fixed":
            raise HotfixError(
                "Remote-label call-count validation failed: "
                f"{label_validation_reason}"
            )

    process_result = feature_results["process_registry_resilience"]
    if process_result["status"] in {"patched", "partial"}:
        process_meta = get_entry_meta(target_header, process_result["path"])
        _, verified_process = read_entry(target, target_header_size, process_meta)
        process_validation = classify_process_registry(verified_process)
        for name in PROCESS_SIGNATURE_VARIANTS:
            if process_result[name]["status"] == "patched":
                if process_validation[name]["status"] != "official_fixed":
                    raise HotfixError(f"Patched process-registry {name} validation failed")

    target_hash = sha256_path(target)
    frontend_attestation_module = None
    if current_profile and is_split_frontend_profile(frontend_profile):
        module_path = target.parent / FRONTEND_ATTESTATION_MODULE_NAME
        module_content = renderer_attestation_module(frontend_profile)
        atomic_replace_bytes(module_path, module_content)
        frontend_attestation_module = {
            "relative_path": FRONTEND_ATTESTATION_MODULE_NAME,
            "sha256": sha256_bytes(module_content),
            "size": len(module_content),
        }
    frontend_contract_result = (
        run_frontend_contract_validator(source, target)
        if current_profile and is_split_frontend_profile(frontend_profile)
        else None
    )
    source_app = source.parent.parent
    portable_app = target.parent.parent
    if codex_patch_manifest is not None:
        codex_backend = prepare_codex_backend_patch(
            source_app,
            portable_app,
            codex_patch_manifest,
            package_full_name,
            package_version,
            expected_codex_patch_descriptor_sha256 or "",
        )
    else:
        source_codex = source_app / CODEX_BACKEND_RELATIVE
        if not source_codex.is_file():
            raise HotfixError(f"Official Codex backend is missing: {source_codex}")
        codex_backend = {
            "status": "official",
            "path": CODEX_BACKEND_RELATIVE.as_posix(),
            "official": {
                "size": source_codex.stat().st_size,
                "sha256": sha256_path(source_codex),
                "pe_machine": pe_machine(source_codex),
            },
        }
    launch_mode = (
        "portable"
        if writes or codex_backend["status"] == "patched"
        else "official"
    )
    executable_asar_integrity = None
    if launch_mode == "portable":
        executable_asar_integrity = synchronize_executable_asar_integrity(
            source_app,
            portable_app,
            source,
            target,
            frontend_profile,
        )
    critical_files = verify_critical_files(
        source_app,
        portable_app,
        executable_asar_integrity,
    )
    manifest = {
        "schema_version": 2,
        "builder_version": BUILDER_VERSION,
        "frontend_profile_id": inspection["frontend_profile_id"],
        "frontend_profile": {
            "package_version": frontend_profile["package_version"],
            "asar_source_sha256": frontend_profile["asar_source_sha256"],
            "entry_path": frontend_profile["entry_path"],
            "entry_source_sha256": frontend_profile["entry_source_sha256"],
            **({
                "secondary_entry_path": frontend_profile["secondary_entry_path"],
                "secondary_entry_source_sha256": frontend_profile["secondary_entry_source_sha256"],
            } if frontend_profile.get("secondary_entry_path") else {}),
        }
        if current_profile
        else None,
        "frontend_output": {
            "replacement_set_sha256": spec.replacement_set_sha256,
            "secondary_replacement_set_sha256": (
                _replacement_set_sha256(secondary_pairs_for_profile(frontend_profile))
                if is_split_frontend_profile(frontend_profile)
                else None
            ),
            "entry_path": str(frontend_profile["entry_path"]),
            "entry_sha256": current_patched_hash,
            "asar_sha256": target_hash,
        }
        if current_profile
        else None,
        "update_status_bridge": update_status_output,
        "frontend_attestation_protocol_route": attestation_protocol_output,
        "created_at": utc_now(),
        "package_full_name": package_full_name,
        "package_version": package_version,
        "official_source_asar": str(source.resolve()),
        "official_source_sha256": inspection["source_sha256"],
        "official_source_size": inspection["source_size"],
        "portable_app": str(final_portable_app.resolve()),
        "portable_asar": str((final_portable_app / "resources" / "app.asar").resolve()),
        "portable_asar_sha256": target_hash,
        "executable_asar_integrity": executable_asar_integrity,
        "launch_mode": launch_mode,
        "features": feature_results,
        "feature_contracts": (
            frontend_contract_result["feature_contracts"]
            if frontend_contract_result is not None
            else None
        ),
        "frontend_runtime_attestation": (
            {
                "schema_version": frontend_contract_result["schema_version"],
                "validator_version": frontend_contract_result["validator_version"],
                "status": frontend_contract_result["status"],
                "source_asar_sha256": frontend_contract_result["source_asar_sha256"],
                "portable_asar_sha256": frontend_contract_result["portable_asar_sha256"],
                "frontend_entry_path": frontend_contract_result["frontend_entry_path"],
                "frontend_entry_sha256": frontend_contract_result["frontend_entry_sha256"],
                "actual_javascript": frontend_contract_result["actual_javascript"],
                "live_renderer_probe": frontend_contract_result["live_renderer_probe"],
                "attestation_module": frontend_attestation_module,
                "protocol_route": attestation_protocol_output,
                "content_logged": frontend_contract_result["content_logged"],
                "summary_sha256": frontend_contract_result["summary_sha256"],
            }
            if frontend_contract_result is not None
            else None
        ),
        "entry_changes": entry_changes,
        "runtime_monitor": {
            "version": RUNTIME_MONITOR_VERSION,
            "core_pressure_policy_version": CORE_PRESSURE_POLICY_VERSION,
            "tool_pressure_policy_version": TOOL_PRESSURE_POLICY_VERSION,
        },
        "codex_backend": codex_backend,
        "critical_files": critical_files,
        "validation": {
            "size_unchanged": True,
            "header_verified": True,
            "target_entries_verified": True,
            "source_non_target_sha256": source_non_target_hash,
            "non_target_sha256": target_non_target_hash,
            "launch_status": "pending",
            "runtime_status": "pending",
            # A matching byte signature is necessary but never proof that the
            # Electron UI used the intended remote-project name.  Keep these
            # release states independent so a later build cannot inherit UI
            # acceptance merely because the ASAR patch was generated.
            "remote_project_label": {
                "byte_patch_status": (
                    "passed"
                    if feature_results["remote_project_label"]["status"]
                    in {"patched", "official_fixed"}
                    else "blocked"
                ),
                "javascript_semantics_status": "external_test_required",
                "natural_restart_status": "pending",
                "ui_acceptance_status": "pending",
            },
        },
    }
    atomic_write_json(manifest_path, manifest)
    return manifest


def verify_manifest(
    manifest_path: Path,
    expected_codex_patch_descriptor_sha256: str | None = None,
    codex_patch_manifest: Path | None = None,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 2:
        raise HotfixError("Unsupported manifest schema")
    if manifest.get("builder_version") != BUILDER_VERSION:
        raise HotfixError("Manifest builder version differs")
    if not isinstance(manifest.get("frontend_profile_id"), str) or not manifest[
        "frontend_profile_id"
    ]:
        raise HotfixError("Manifest frontend profile is invalid")
    declared_profile = manifest.get("frontend_profile")
    source_profile = profile_for_asar(str(manifest.get("official_source_sha256") or ""))
    spec = spec_for_profile(source_profile)
    contracts_required = is_split_frontend_profile(source_profile)
    if source_profile is not None:
        expected_profile = {
            "package_version": source_profile["package_version"],
            "asar_source_sha256": source_profile["asar_source_sha256"],
            "entry_path": source_profile["entry_path"],
            "entry_source_sha256": source_profile["entry_source_sha256"],
            **({
                "secondary_entry_path": source_profile["secondary_entry_path"],
                "secondary_entry_source_sha256": source_profile["secondary_entry_source_sha256"],
            } if source_profile.get("secondary_entry_path") else {}),
        }
        if (
            declared_profile != expected_profile
            or manifest["frontend_profile_id"] != frontend_profile_id(source_profile)
            or manifest.get("package_version") != source_profile["package_version"]
        ):
            raise HotfixError("Manifest frontend profile identity is invalid")
        frontend_output = manifest.get("frontend_output")
        if not isinstance(frontend_output, dict) or frontend_output.get(
            "replacement_set_sha256"
        ) != spec.replacement_set_sha256:
            raise HotfixError("Manifest frontend output identity is invalid")
        if frontend_output.get("entry_path") != source_profile["entry_path"]:
            raise HotfixError("Manifest frontend output entry path is invalid")
        expected_secondary_digest = (
            _replacement_set_sha256(secondary_pairs_for_profile(source_profile))
            if is_split_frontend_profile(source_profile)
            else None
        )
        if frontend_output.get("secondary_replacement_set_sha256") != expected_secondary_digest:
            raise HotfixError("Manifest secondary frontend output identity is invalid")
    elif manifest.get("frontend_output") is not None:
        raise HotfixError("Manifest frontend output has no official source profile")
    if manifest.get("launch_mode") not in {"official", "portable"}:
        raise HotfixError("Manifest launch mode is invalid")
    features = manifest.get("features")
    if not isinstance(features, dict) or set(features) != set(FEATURE_STATUSES):
        raise HotfixError("Manifest feature inventory is invalid")
    for name, allowed in FEATURE_STATUSES.items():
        feature = features[name]
        if not isinstance(feature, dict) or feature.get("status") not in allowed:
            raise HotfixError(f"Manifest feature status is invalid: {name}")
        if feature.get("status") != "unsupported" and not isinstance(feature.get("path"), str):
            raise HotfixError(f"Manifest feature path is invalid: {name}")
    feature_contracts = manifest.get("feature_contracts")
    runtime_attestation = manifest.get("frontend_runtime_attestation")
    if contracts_required:
        if not isinstance(feature_contracts, dict) or set(feature_contracts) != set(FEATURE_STATUSES):
            raise HotfixError("Manifest feature-contract inventory is invalid")
        for name, contract in feature_contracts.items():
            if not isinstance(contract, dict) or contract.get("status") not in {
                "native_verified", "patched_verified"
            }:
                raise HotfixError(f"Manifest feature contract is not release-verified: {name}")
            for layer in ("source_identity", "semantic_execution", "route_wiring"):
                if not isinstance(contract.get(layer), dict) or contract[layer].get("status") != "passed":
                    raise HotfixError(f"Manifest feature-contract layer did not pass: {name}/{layer}")
            live_layer = contract.get("runtime_attestation")
            expected_non_renderer = name in NON_RENDERER_ATTESTATION_FEATURES
            if not isinstance(live_layer, dict) or live_layer.get("content_logged") is not False:
                raise HotfixError(f"Manifest runtime contract is invalid: {name}")
            if expected_non_renderer:
                if (
                    live_layer.get("status") != "preverified_non_renderer"
                    or live_layer.get("protocol") != "component_contract_v1"
                    or live_layer.get("scope") not in {"main_process", "guarded_interaction"}
                ):
                    raise HotfixError(f"Manifest non-renderer contract is invalid: {name}")
            elif (
                live_layer.get("status") != "pending_live_renderer"
                or live_layer.get("protocol") != "live_renderer_attestation_v3"
                or live_layer.get("scope") != "renderer"
            ):
                raise HotfixError(f"Manifest live-renderer contract is invalid: {name}")
        if (
            not isinstance(runtime_attestation, dict)
            or runtime_attestation.get("schema_version") != 2
            or runtime_attestation.get("validator_version") != FRONTEND_CONTRACT_VALIDATOR_VERSION
            or runtime_attestation.get("status") != "bundle_qualified_only"
            or runtime_attestation.get("content_logged") is not False
            or not isinstance(runtime_attestation.get("live_renderer_probe"), dict)
            or runtime_attestation["live_renderer_probe"].get("status") != "pending_live_renderer"
        ):
            raise HotfixError("Manifest frontend runtime attestation is invalid")
        module = runtime_attestation.get("attestation_module")
        expected_module = renderer_attestation_module(source_profile)
        module_path = Path(manifest["portable_asar"]).parent / FRONTEND_ATTESTATION_MODULE_NAME
        # A historical artifact keeps the artifact id (and therefore the signed
        # module bytes) it was released with; only the current release must
        # reproduce the live module text exactly.
        current_artifact = (
            manifest.get("artifact_id") == FRONTEND_ATTESTATION_ARTIFACT_ID
        )
        if current_artifact and (
            not isinstance(module, dict)
            or module.get("relative_path") != FRONTEND_ATTESTATION_MODULE_NAME
            or module.get("sha256") != sha256_bytes(expected_module)
            or module.get("size") != len(expected_module)
            or not module_path.is_file()
            or module_path.stat().st_size != len(expected_module)
            or sha256_path(module_path) != sha256_bytes(expected_module)
        ):
            raise HotfixError("Manifest frontend attestation module identity is invalid")
        if not current_artifact and (
            not isinstance(module, dict)
            or module.get("relative_path") != FRONTEND_ATTESTATION_MODULE_NAME
            or not isinstance(module.get("sha256"), str)
            or not module_path.is_file()
            or module_path.stat().st_size != int(module.get("size") or -1)
            or sha256_path(module_path) != str(module.get("sha256"))
        ):
            raise HotfixError("Historical frontend attestation module file is invalid")
        route = runtime_attestation.get("protocol_route")
        top_level_route = manifest.get("frontend_attestation_protocol_route")
        expected_route = {
            "protocol": "app_resource_route_v2",
            "app_url": FRONTEND_ATTESTATION_APP_URL,
            "entry_path": source_profile["attestation_protocol_entry_path"],
            "source_sha256": source_profile["attestation_protocol_source_sha256"],
            "patched_sha256": None,
            "old_signature_count": 0,
            "new_signature_count": (
                1
                if source_profile.get("package_version") in {
                    "26.903.9818.0",
                    "26.908.4834.0",
            "26.908.9136.0",
                }
                else 2
            ),
            "module_relative_path": FRONTEND_ATTESTATION_MODULE_NAME,
            "physical_resolution": "resources/x.js",
            "mime_type": "text/javascript",
            "response_strategy": "node_stream_response_v1",
            "general_traversal_enabled": False,
        }
        if not isinstance(route, dict) or route != top_level_route:
            raise HotfixError("Manifest frontend attestation protocol route is missing")
        for key, expected_value in expected_route.items():
            if key == "patched_sha256":
                if not isinstance(route.get(key), str) or not route.get(key):
                    raise HotfixError("Manifest protocol patched hash is missing")
            elif route.get(key) != expected_value:
                raise HotfixError(f"Manifest frontend protocol route is invalid: {key}")
        portable_asar_path = Path(manifest["portable_asar"])
        portable_header_size, _, portable_header = read_asar(portable_asar_path)
        protocol_meta = get_entry_meta(
            portable_header, source_profile["attestation_protocol_entry_path"]
        )
        _, protocol_data = read_entry(
            portable_asar_path, portable_header_size, protocol_meta
        )
        protocol_handler_old = (
            FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26831_OLD
            if is_split_frontend_profile(source_profile)
            else FRONTEND_ATTESTATION_PROTOCOL_HANDLER_OLD
        )
        protocol_handler_fixed = (
            FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26831_NEW
            if is_split_frontend_profile(source_profile)
            else FRONTEND_ATTESTATION_PROTOCOL_HANDLER_NEW
        )
        is_26908_route = source_profile.get("package_version") in {"26.908.4834.0", "26.908.9136.0"}
        is_26903_route = source_profile.get("package_version") == "26.903.9818.0"
        resolver_new = (
            FRONTEND_ATTESTATION_PROTOCOL_26908_NEW
            if is_26908_route
            else FRONTEND_ATTESTATION_PROTOCOL_26903_NEW if is_26903_route else FRONTEND_ATTESTATION_PROTOCOL_NEW
        )
        resolver_old = (
            FRONTEND_ATTESTATION_PROTOCOL_26908_OLD
            if is_26908_route
            else FRONTEND_ATTESTATION_PROTOCOL_26903_OLD if is_26903_route else FRONTEND_ATTESTATION_PROTOCOL_OLD
        )
        handler_new = (
            FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26908_NEW
            if is_26908_route
            else FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26903_NEW if is_26903_route else protocol_handler_fixed
        )
        handler_old_value = (
            FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26908_OLD
            if is_26908_route
            else FRONTEND_ATTESTATION_PROTOCOL_HANDLER_26903_OLD if is_26903_route else protocol_handler_old
        )
        if (
            sha256_bytes(protocol_data) != route["patched_sha256"]
            or protocol_data.count(resolver_new) != 1
            or protocol_data.count(resolver_old) != 0
            or protocol_data.count(handler_new) != 1
            or protocol_data.count(handler_old_value) != 0
            or (
                not is_26903_route
                and not is_26908_route
                and protocol_data.count(FRONTEND_ATTESTATION_PROTOCOL_COMPACTION_NEW) != 1
            )
        ):
            raise HotfixError("Portable frontend attestation protocol route differs")
    validation = manifest.get("validation")
    if not isinstance(validation, dict) or validation.get("runtime_status") not in {
        "pending",
        "healthy",
        "failed",
    }:
        raise HotfixError("Manifest runtime status is invalid")
    remote_label_validation = validation.get("remote_project_label")
    if not isinstance(remote_label_validation, dict) or remote_label_validation != {
        "byte_patch_status": "passed"
        if features["remote_project_label"]["status"]
        in {"patched", "official_fixed"}
        else "blocked",
        "javascript_semantics_status": "external_test_required",
        "natural_restart_status": "pending",
        "ui_acceptance_status": "pending",
    }:
        raise HotfixError("Manifest remote-project label acceptance state is invalid")
    automation_feature = features["automation_priority_gate"]
    if (
        automation_feature.get("policy") != AUTOMATION_PRIORITY_POLICY
        or automation_feature.get("scheduled_indicator_included") is not True
        or automation_feature.get("scheduled_visible_attention_states")
        != ["active", "waiting", "unread"]
        or automation_feature.get("scheduled_bypass_toggle_attention_states")
        != ["active", "waiting", "unread"]
        or automation_feature.get("idle_requires_scheduled_toggle") is not True
        or automation_feature.get("idle_requires_existing_priority_hold") is not True
        or automation_feature.get("dormant_schedule_excluded") is not True
        or automation_feature.get("identity_sources")
        != ["thread_schedule_state", "automation_conversation_index"]
        or automation_feature.get("inbox_identity_session_sticky") is not False
        or automation_feature.get("actual_membership_functions")
        != automation_priority_membership_functions(source_profile)
        or automation_feature.get("active_configuration_alone_included") is not False
    ):
        raise HotfixError("Manifest automation-priority policy is invalid")
    resume_feature = features["resume_history_on_demand"]
    legacy_resume_policy = {
        "policy": "eager_full_after_tail",
        "factory_policy": "force_full_history",
        "prevents_new_paginated_threads": True,
        "supports_existing_paginated_threads": False,
        "projection_recovery": "manager_prelaunch",
    }
    current_resume_policy = {
        "policy": "official_canonical_completion",
        "factory_policy": "official_paginated_history",
        "prevents_new_paginated_threads": False,
        "supports_existing_paginated_threads": True,
        "projection_recovery": "official_canonical_history",
    }
    actual_resume_policy = {
        key: resume_feature.get(key) for key in legacy_resume_policy
    }
    if (
        actual_resume_policy not in (legacy_resume_policy, current_resume_policy)
        or resume_feature.get("initial_turn_page_limit") != 5
        or resume_feature.get("auto_drain_remaining_turns") is not True
        or resume_feature.get(
            "supports_existing_paginated_threads_after_recovery"
        )
        is not True
    ):
        raise HotfixError("Manifest resume-history policy is invalid")
    tail_feature = features["paginated_tail_retention"]
    if (
        tail_feature.get("policy")
        not in {"keep_paginated_loaded", "official_canonical_pagination"}
        or tail_feature.get("scope") != "history_mode_paginated"
    ):
        raise HotfixError("Manifest paginated-tail retention policy is invalid")
    watch_feature = features["windows_watch_path_normalization"]
    if watch_feature.get("scope") != "fs/watch" or (
        watch_feature.get("host_scope") != "local"
    ):
        raise HotfixError("Manifest Windows watch-path scope is invalid")
    watch_dependencies = watch_feature.get("dependencies")
    if not validate_windows_watch_dependencies(watch_dependencies):
        raise HotfixError("Manifest Windows watch-path dependency inventory is invalid")
    monitor = manifest.get("runtime_monitor")
    if not isinstance(monitor, dict) or monitor != {
        "version": RUNTIME_MONITOR_VERSION,
        "core_pressure_policy_version": CORE_PRESSURE_POLICY_VERSION,
        "tool_pressure_policy_version": TOOL_PRESSURE_POLICY_VERSION,
    }:
        raise HotfixError("Manifest runtime-monitor policy is invalid")
    process_feature = features["process_registry_resilience"]
    process_substatuses: list[str] = []
    for name in ("read_recovery", "atomic_write"):
        subfeature = process_feature.get(name)
        if not isinstance(subfeature, dict) or subfeature.get("status") not in {
            "patched",
            "official_fixed",
            "unsupported",
            "patchable",
        }:
            raise HotfixError(f"Manifest process-registry subfeature is invalid: {name}")
        process_substatuses.append(subfeature["status"])
    if process_feature["status"] in {"patched", "official_fixed"} and not all(
        status in {"patched", "official_fixed"} for status in process_substatuses
    ):
        raise HotfixError("Manifest process-registry feature status is inconsistent")
    source = Path(manifest["official_source_asar"])
    portable_asar = Path(manifest["portable_asar"])
    if not source.is_file() or sha256_path(source) != manifest["official_source_sha256"]:
        raise HotfixError("Official source no longer matches the manifest")
    if source.stat().st_size != int(manifest["official_source_size"]):
        raise HotfixError("Official source size no longer matches the manifest")
    declared_executable_integrity = manifest.get("executable_asar_integrity")
    requires_executable_integrity = bool(
        source_profile
        and source_profile.get("embedded_asar_header_source_sha256")
        and manifest.get("launch_mode") == "portable"
    )
    actual_executable_integrity = None
    if requires_executable_integrity:
        actual_executable_integrity = verify_executable_asar_integrity(
            source.parent.parent,
            Path(manifest["portable_app"]),
            source,
            portable_asar,
            source_profile,
        )
        if declared_executable_integrity != actual_executable_integrity:
            raise HotfixError("Manifest executable ASAR-integrity record differs")
    elif declared_executable_integrity is not None:
        raise HotfixError("Manifest contains an unexpected executable ASAR-integrity record")
    codex_backend = manifest.get("codex_backend")
    if not isinstance(codex_backend, dict) or codex_backend.get("status") not in {
        "official",
        "patched",
    }:
        raise HotfixError("Manifest Codex backend policy is invalid")
    if codex_backend.get("path") != CODEX_BACKEND_RELATIVE.as_posix():
        raise HotfixError("Manifest Codex backend path is invalid")
    expected_backend_compatibility = {
        "policy_schema_version": 2,
        "matched_package": {
            "package_full_name": manifest.get("package_full_name"),
            "package_version": manifest.get("package_version"),
        },
    }
    if codex_backend["status"] in {"patched", "official"} and (
        codex_backend.get("compatibility") != expected_backend_compatibility
        or
        not isinstance(expected_codex_patch_descriptor_sha256, str)
        or not re.fullmatch(
            r"[0-9a-f]{64}", expected_codex_patch_descriptor_sha256
        )
        or codex_backend.get("descriptor_sha256")
        != expected_codex_patch_descriptor_sha256
    ):
        raise HotfixError("Manifest Codex backend policy is invalid")
    official_codex = source.parent.parent / CODEX_BACKEND_RELATIVE
    official_backend = codex_backend.get("official")
    if (
        not isinstance(official_backend, dict)
        or not official_codex.is_file()
        or official_backend.get("size") != official_codex.stat().st_size
        or official_backend.get("sha256") != sha256_path(official_codex)
        or official_backend.get("pe_machine") != pe_machine(official_codex)
    ):
        raise HotfixError("Official Codex backend no longer matches the manifest")
    if codex_backend["status"] == "patched":
        if codex_patch_manifest is None:
            raise HotfixError("Codex backend patch descriptor is required")
        policy, descriptor_sha256 = load_codex_backend_patch_policy(
            codex_patch_manifest,
            expected_codex_patch_descriptor_sha256 or "",
        )
        matched_package = select_codex_backend_package(
            policy,
            str(manifest.get("package_full_name") or ""),
            str(manifest.get("package_version") or ""),
        )
        policy_patched = policy.get("patched")
        if (
            policy.get("schema_version") != 2
            or codex_backend.get("descriptor_sha256") != descriptor_sha256
            or codex_backend.get("patch_id") != policy.get("patch_id")
            or codex_backend.get("compatibility")
            != {
                "policy_schema_version": 2,
                "matched_package": matched_package,
            }
            or codex_backend.get("official") != policy.get("official")
            or not isinstance(policy_patched, dict)
            or codex_backend.get("patched")
            != {
                "size": policy_patched.get("size"),
                "sha256": policy_patched.get("sha256"),
                "pe_machine": policy_patched.get("pe_machine"),
                "authenticode_status": policy_patched.get(
                    "authenticode_status"
                ),
                "version_output": policy_patched.get("version_output"),
            }
            or codex_backend.get("provenance") != policy.get("provenance")
        ):
            raise HotfixError(
                "Manifest Codex backend differs from the allowlisted descriptor"
            )
        if manifest["launch_mode"] != "portable":
            raise HotfixError("Patched Codex backend requires portable launch mode")
        if not isinstance(codex_backend.get("patch_id"), str) or not codex_backend[
            "patch_id"
        ]:
            raise HotfixError("Manifest Codex backend patch id is invalid")
        if not isinstance(codex_backend.get("provenance"), dict) or not codex_backend[
            "provenance"
        ]:
            raise HotfixError("Manifest Codex backend provenance is missing")
        patched_backend = codex_backend.get("patched")
        if not isinstance(patched_backend, dict):
            raise HotfixError("Manifest patched Codex backend inventory is invalid")
        portable_codex = Path(manifest["portable_app"]) / CODEX_BACKEND_RELATIVE
        if (
            not portable_codex.is_file()
            or patched_backend.get("size") != portable_codex.stat().st_size
            or patched_backend.get("sha256") != sha256_path(portable_codex)
            or patched_backend.get("pe_machine") != pe_machine(portable_codex)
            or patched_backend.get("authenticode_status")
            != pe_authenticode_status(portable_codex)
            or patched_backend.get("version_output")
            != codex_version_output(portable_codex)
            or patched_backend.get("sha256") == official_backend.get("sha256")
        ):
            raise HotfixError("Patched Codex backend no longer matches the manifest")
    elif codex_backend["status"] == "official":
        if codex_patch_manifest is None:
            raise HotfixError("Codex backend policy descriptor is required")
        policy, descriptor_sha256 = load_codex_backend_patch_policy(
            codex_patch_manifest,
            expected_codex_patch_descriptor_sha256 or "",
        )
        if (
            policy.get("mode") != "official"
            or codex_backend.get("descriptor_sha256") != descriptor_sha256
            or codex_backend.get("patch_id") != policy.get("patch_id")
            or codex_backend.get("official") != policy.get("official")
            or codex_backend.get("provenance") != policy.get("provenance")
        ):
            raise HotfixError(
                "Manifest Codex backend differs from the allowlisted descriptor"
            )
        expected_version_output = policy.get("version_output")
        expected_authenticode_status = policy.get("authenticode_status")
        portable_codex = Path(manifest["portable_app"]) / CODEX_BACKEND_RELATIVE
        if (
            not portable_codex.is_file()
            or portable_codex.stat().st_size != official_backend.get("size")
            or sha256_path(portable_codex) != official_backend.get("sha256")
            or pe_machine(portable_codex) != official_backend.get("pe_machine")
            or codex_backend.get("version_output") != codex_version_output(portable_codex)
            or codex_backend.get("authenticode_status")
            != pe_authenticode_status(portable_codex)
            or (
                expected_version_output is not None
                and codex_backend.get("version_output") != expected_version_output
            )
            or (
                expected_authenticode_status is not None
                and codex_backend.get("authenticode_status")
                != expected_authenticode_status
            )
        ):
            raise HotfixError("Official Codex backend no longer matches the manifest")
        if manifest["launch_mode"] != "portable":
            raise HotfixError(
                "Official Codex backend with frontend patches requires portable launch mode"
            )
    if contracts_required:
        actual_contracts = run_frontend_contract_validator(source, portable_asar)
        if (
            actual_contracts.get("feature_contracts") != feature_contracts
            or actual_contracts.get("portable_asar_sha256") != manifest.get("portable_asar_sha256")
            or actual_contracts.get("summary_sha256") != runtime_attestation.get("summary_sha256")
        ):
            raise HotfixError("Frontend feature contracts differ from the actual portable ASAR")
    source_inspection, _ = inspect_archive(source)
    if (
        source_inspection["features"]["windows_watch_path_normalization"].get(
            "dependencies"
        )
        != watch_dependencies
    ):
        raise HotfixError(
            "Manifest Windows watch-path dependencies disagree with the official source"
        )
    if manifest["launch_mode"] == "official":
        source_features = source_inspection["features"]
        for name in REQUIRED_FEATURES:
            if source_features[name]["status"] != "official_fixed":
                raise HotfixError(f"Official launch does not preserve required feature: {name}")
            if features[name]["status"] != "official_fixed" or (
                features[name]["path"] != source_features[name]["path"]
            ):
                raise HotfixError(f"Official required feature disagrees with inspection: {name}")
        for name in OPTIONAL_FEATURES:
            manifest_status = features[name]["status"]
            source_status = source_features[name]["status"]
            if manifest_status == "patched":
                raise HotfixError(f"Official launch cannot claim a patched feature: {name}")
            if source_status == "official_fixed" and manifest_status != "official_fixed":
                raise HotfixError(f"Official fixed feature was not recorded: {name}")
            if manifest_status == "official_fixed" and source_status != "official_fixed":
                raise HotfixError(f"Official feature disagrees with source inspection: {name}")
    else:
        if not portable_asar.is_file():
            raise HotfixError("Portable ASAR is missing")
        if sha256_path(portable_asar) != manifest["portable_asar_sha256"]:
            raise HotfixError("Portable ASAR hash mismatch")
        if portable_asar.stat().st_size != source.stat().st_size:
            raise HotfixError("Portable ASAR size differs from the official source")
        critical_files = manifest.get("critical_files")
        if not isinstance(critical_files, dict) or set(critical_files) != set(CRITICAL_FILES):
            raise HotfixError("Portable critical-file inventory is incomplete")
        portable_app = Path(manifest["portable_app"])
        expected_asar = portable_app / "resources" / "app.asar"
        if os.path.normcase(str(portable_asar.resolve())) != os.path.normcase(
            str(expected_asar.resolve())
        ):
            raise HotfixError("Portable ASAR is outside the selected portable app")
        actual_critical = verify_critical_files(
            source.parent.parent,
            portable_app,
            actual_executable_integrity,
        )
        if actual_critical != critical_files:
            raise HotfixError("Portable critical-file inventory differs from verified files")
        if codex_backend["status"] == "official":
            portable_codex = portable_app / CODEX_BACKEND_RELATIVE
            if (
                not portable_codex.is_file()
                or portable_codex.stat().st_size != official_backend["size"]
                or sha256_path(portable_codex) != official_backend["sha256"]
                or pe_machine(portable_codex) != official_backend["pe_machine"]
            ):
                raise HotfixError(
                    "Portable official Codex backend differs from the manifest"
                )
        frontend_output = manifest.get("frontend_output")
        if source_profile is None or not isinstance(frontend_output, dict):
            raise HotfixError("Portable frontend output is not bound to an official profile")
        source_header_size, _, source_header = read_asar(source)
        source_entry_meta = get_entry_meta(source_header, source_profile["entry_path"])
        _, source_entry = read_entry(source, source_header_size, source_entry_meta)
        if frontend_profile_superseded(source_profile):
            expected_entry = source_entry
        else:
            expected_entry, _ = patch_current_frontend_entry(
                source_entry, profile=source_profile
            )
        expected_entry_hash = sha256_bytes(expected_entry)
        validate_javascript_syntax(expected_entry, str(source_profile["entry_path"]))
        if frontend_output.get("entry_sha256") != expected_entry_hash:
            raise HotfixError("Manifest frontend output entry hash is invalid")
        if frontend_output.get("asar_sha256") != manifest["portable_asar_sha256"]:
            raise HotfixError("Manifest frontend output ASAR hash is invalid")
        update_status_bridge = manifest.get("update_status_bridge")
        main_entry_path = source_profile.get("main_entry_path")
        if main_entry_path:
            if not isinstance(update_status_bridge, dict):
                raise HotfixError("Portable update-status bridge is missing")
            source_main_meta = get_entry_meta(source_header, str(main_entry_path))
            _, source_main = read_entry(source, source_header_size, source_main_meta)
            expected_main = patch_portable_update_status_entry(source_main, source_profile)
            validate_javascript_syntax(expected_main, str(main_entry_path))
            if (
                update_status_bridge.get("entry_path") != main_entry_path
                or update_status_bridge.get("source_sha256") != sha256_bytes(source_main)
                or update_status_bridge.get("patched_sha256") != sha256_bytes(expected_main)
            ):
                raise HotfixError("Manifest update-status bridge identity is invalid")
            portable_header_size, _, portable_header = read_asar(portable_asar)
            portable_main_meta = get_entry_meta(portable_header, str(main_entry_path))
            _, portable_main = read_entry(portable_asar, portable_header_size, portable_main_meta)
            if portable_main != expected_main:
                raise HotfixError("Portable update-status bridge differs from exact patch")
        elif update_status_bridge is not None:
            raise HotfixError("Portable update-status bridge has no official profile")
        inspection, _ = inspect_archive(
            portable_asar,
            expected_frontend_profile=source_profile,
            expected_entry_sha256=expected_entry_hash,
        )
        portable_profile = source_profile
        portable_current_profile = True
        header_size, _, header = read_asar(portable_asar)
        portable_initial_meta = get_entry_meta(
            header, str(source_profile["entry_path"])
        )
        _, portable_initial_entry = read_entry(
            portable_asar, header_size, portable_initial_meta
        )
        if sha256_bytes(portable_initial_entry) != expected_entry_hash:
            raise HotfixError("Portable current-profile entry differs from exact patch")
        sorting_result = features["project_sorting"]
        sorting_meta = get_entry_meta(header, sorting_result["path"])
        _, sorting_data = read_entry(portable_asar, header_size, sorting_meta)
        sorting_status, sorting_reason = classify_sort(sorting_data)
        if portable_current_profile:
            sorting_status, sorting_reason = "official_fixed", None
        if sorting_status != "official_fixed":
            raise HotfixError(
                f"Portable sorting fix is no longer valid: {sorting_reason}"
            )
        if inspection["features"]["project_sorting"]["status"] != "official_fixed":
            raise HotfixError("Portable sorting inspection disagrees with the manifest")
        if portable_current_profile:
            superseded_frontend = frontend_profile_superseded(source_profile)
            for current_name in spec.features:
                current_status, current_reason = classify_current_feature(
                    portable_initial_entry, current_name, spec
                )
                expected_status = "unsupported" if superseded_frontend else "official_fixed"
                if current_status != expected_status:
                    raise HotfixError(
                        "Portable current-profile feature is no longer valid: "
                        f"{current_name}: expected={expected_status}, "
                        f"actual={current_status}, reason={current_reason}"
                    )
                if not superseded_frontend and (
                    inspection["features"][current_name]["status"] != "official_fixed"
                ):
                    raise HotfixError(
                        "Portable current-profile inspection disagrees with the manifest: "
                        f"{current_name}"
                    )

        resume_result = features["resume_history_on_demand"]
        resume_meta = get_entry_meta(header, resume_result["path"])
        _, resume_data = read_entry(portable_asar, header_size, resume_meta)
        resume_status, resume_reason = classify_resume_history(resume_data)
        if portable_current_profile:
            resume_status, resume_reason = "official_fixed", None
        if resume_status != "official_fixed":
            raise HotfixError(
                "Portable resume-history policy is no longer valid: "
                f"actual={resume_status}, "
                f"reason={resume_reason}"
            )
        if (
            inspection["features"]["resume_history_on_demand"]["status"]
            != "official_fixed"
        ):
            raise HotfixError(
                "Portable resume-history inspection disagrees with the manifest"
            )
        portable_resume_policy = {
            key: resume_result.get(key)
            for key in (
                "policy",
                "factory_policy",
                "prevents_new_paginated_threads",
                "supports_existing_paginated_threads",
                "projection_recovery",
            )
        }
        expected_portable_resume_policy = (
            {
                "policy": "official_canonical_completion",
                "factory_policy": "official_paginated_history",
                "prevents_new_paginated_threads": False,
                "supports_existing_paginated_threads": True,
                "projection_recovery": "official_canonical_history",
            }
            if portable_current_profile
            else {
                "policy": "eager_full_after_tail",
                "factory_policy": "force_full_history",
                "prevents_new_paginated_threads": True,
                "supports_existing_paginated_threads": False,
                "projection_recovery": "manager_prelaunch",
            }
        )
        if (
            portable_resume_policy != expected_portable_resume_policy
            or resume_result.get("initial_turn_page_limit") != 5
            or resume_result.get("auto_drain_remaining_turns") is not True
            or resume_result.get(
                "supports_existing_paginated_threads_after_recovery"
            )
            is not True
        ):
            raise HotfixError("Portable resume-history policy metadata is invalid")

        tail_result = features["paginated_tail_retention"]
        tail_meta = get_entry_meta(header, tail_result["path"])
        _, tail_data = read_entry(portable_asar, header_size, tail_meta)
        tail_status, tail_reason = classify_paginated_tail_retention(tail_data)
        if portable_current_profile:
            tail_status, tail_reason = "official_fixed", None
        if tail_status != "official_fixed":
            raise HotfixError(
                "Portable paginated-tail retention is no longer valid: "
                f"{tail_reason}"
            )
        if (
            inspection["features"]["paginated_tail_retention"]["status"]
            != "official_fixed"
            or tail_result.get("policy")
            != (
                "official_canonical_pagination"
                if portable_current_profile
                else "keep_paginated_loaded"
            )
            or tail_result.get("scope") != "history_mode_paginated"
        ):
            raise HotfixError(
                "Portable paginated-tail retention metadata is invalid"
            )

        watch_result = features["windows_watch_path_normalization"]
        watch_meta = get_entry_meta(header, watch_result["path"])
        _, watch_data = read_entry(portable_asar, header_size, watch_meta)
        watch_status, watch_reason = classify_windows_watch_path(watch_data)
        if not portable_current_profile and watch_status != "official_fixed":
            raise HotfixError(
                f"Portable Windows watch-path fix is no longer valid: {watch_reason}"
            )
        if (
            inspection["features"]["windows_watch_path_normalization"]["status"]
            != "official_fixed"
        ):
            raise HotfixError(
                "Portable Windows watch-path inspection disagrees with the manifest"
            )
        if (
            inspection["features"]["windows_watch_path_normalization"].get(
                "dependencies"
            )
            != watch_dependencies
        ):
            raise HotfixError(
                "Portable Windows watch-path dependencies disagree with the manifest"
            )

        idle_result = features["idle_history_eviction"]
        if (
            not portable_current_profile
            and idle_result["status"] in {"patched", "official_fixed"}
        ):
            idle_meta = get_entry_meta(header, idle_result["path"])
            _, idle_data = read_entry(portable_asar, header_size, idle_meta)
            idle_status, idle_reason = classify_idle_history(idle_data)
            if idle_status != "official_fixed":
                raise HotfixError(
                    "Portable idle-history fix is no longer valid: "
                    f"{idle_reason}"
                )

        label_result = features["remote_project_label"]
        if (
            label_result["status"] in {"patched", "official_fixed"}
        ):
            label_meta = get_entry_meta(header, label_result["path"])
            _, label_data = read_entry(portable_asar, header_size, label_meta)
            if portable_current_profile:
                label_status, label_reason = classify_current_feature(
                    label_data, "remote_project_label"
                )
            else:
                label_status, label_reason, _ = _classify_label_entry(label_data)
            if label_status != "official_fixed":
                raise HotfixError(
                    f"Portable remote-label fix is no longer valid: {label_reason}"
                )

        process_result = features["process_registry_resilience"]
        if process_result["status"] in {"patched", "official_fixed"}:
            process_meta = get_entry_meta(header, process_result["path"])
            _, process_data = read_entry(portable_asar, header_size, process_meta)
            process_validation = classify_process_registry(process_data)
            for name in PROCESS_SIGNATURE_VARIANTS:
                subfeature = process_result.get(name)
                if not isinstance(subfeature, dict):
                    raise HotfixError(f"Process-registry subfeature is missing: {name}")
                if subfeature.get("status") in {"patched", "official_fixed"}:
                    if process_validation[name]["status"] != "official_fixed":
                        raise HotfixError(
                            f"Portable process-registry {name} patch is no longer valid"
                        )

        changes = manifest.get("entry_changes")
        if not isinstance(changes, list):
            raise HotfixError("Portable manifest entry-change inventory is invalid")
        if not changes:
            if frontend_profile_superseded(source_profile):
                # A superseded frontend profile keeps the official ASAR
                # byte-identical; only the Codex backend outside the ASAR is
                # patched. Require that identity explicitly instead of the
                # usual non-empty entry-change inventory.
                if sha256_path(portable_asar) != manifest.get("official_source_sha256"):
                    raise HotfixError(
                        "Superseded portable ASAR must remain byte-identical "
                        "to the official source"
                    )
            else:
                raise HotfixError("Portable manifest entry-change inventory is missing")
        source_header_size, _, source_header = read_asar(source)
        ranges = [(0, 8 + source_header_size)]
        seen_paths: set[str] = set()
        for change in changes:
            if not isinstance(change, dict) or not isinstance(change.get("path"), str):
                raise HotfixError("Portable manifest entry-change record is invalid")
            path = change["path"]
            if path in seen_paths:
                raise HotfixError(f"Portable manifest contains a duplicate entry change: {path}")
            seen_paths.add(path)
            source_meta = get_entry_meta(source_header, path)
            target_meta = get_entry_meta(header, path)
            source_offset, source_data = read_entry(source, source_header_size, source_meta)
            target_offset, target_data = read_entry(portable_asar, header_size, target_meta)
            if source_offset != target_offset or len(source_data) != len(target_data):
                raise HotfixError(f"Portable entry layout changed: {path}")
            if change.get("source_sha256") != sha256_bytes(source_data):
                raise HotfixError(f"Portable source-entry hash disagrees: {path}")
            if change.get("patched_sha256") != sha256_bytes(target_data):
                raise HotfixError(f"Portable patched-entry hash disagrees: {path}")
            ranges.append((source_offset, source_offset + len(source_data)))
        source_non_target_hash = hash_excluding_ranges(source, ranges)
        target_non_target_hash = hash_excluding_ranges(portable_asar, ranges)
        validation = manifest.get("validation", {})
        if source_non_target_hash != target_non_target_hash:
            raise HotfixError("Portable non-target ASAR bytes no longer match the official source")
        if validation.get("source_non_target_sha256") != source_non_target_hash or (
            validation.get("non_target_sha256") != target_non_target_hash
        ):
            raise HotfixError("Portable non-target ASAR hash disagrees with the manifest")
    return {
        "ok": True,
        "package_version": manifest["package_version"],
        "launch_mode": manifest["launch_mode"],
        "portable_asar_sha256": manifest.get("portable_asar_sha256"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Version-aware ChatGPT project hotfix builder")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect")
    inspect_parser.add_argument("--source", type=Path, required=True)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--source", type=Path, required=True)
    build_parser.add_argument("--target", type=Path, required=True)
    build_parser.add_argument("--manifest", type=Path, required=True)
    build_parser.add_argument("--package-full-name", required=True)
    build_parser.add_argument("--package-version", required=True)
    build_parser.add_argument("--final-portable-app", type=Path, required=True)
    build_parser.add_argument("--codex-patch-manifest", type=Path)
    build_parser.add_argument("--expected-codex-patch-descriptor-sha256")

    diagnostic_parser = subparsers.add_parser("diagnostic-current-profile")
    diagnostic_parser.add_argument("--source", type=Path, required=True)
    diagnostic_parser.add_argument("--target", type=Path, required=True)
    diagnostic_parser.add_argument(
        "--features",
        required=True,
        help="Comma-separated current-profile features; use 'none' for the backend-only baseline.",
    )

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--manifest", type=Path, required=True)
    verify_parser.add_argument("--expected-codex-patch-descriptor-sha256")
    verify_parser.add_argument("--codex-patch-manifest", type=Path)

    registry_parser = subparsers.add_parser("repair-registry")
    registry_parser.add_argument("--path", type=Path, required=True)
    registry_parser.add_argument("--backup-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "inspect":
            result, _ = inspect_archive(args.source)
        elif args.command == "build":
            result = build_archive(
                args.source,
                args.target,
                args.manifest,
                args.package_full_name,
                args.package_version,
                args.final_portable_app,
                args.codex_patch_manifest,
                args.expected_codex_patch_descriptor_sha256,
            )
        elif args.command == "diagnostic-current-profile":
            raw_features = args.features.strip()
            diagnostic_features = (
                set()
                if raw_features.lower() in {"", "none"}
                else {item.strip() for item in raw_features.split(",") if item.strip()}
            )
            result = patch_current_profile_entry_file(
                args.source,
                args.target,
                diagnostic_features,
            )
        elif args.command == "verify":
            result = verify_manifest(
                args.manifest,
                args.expected_codex_patch_descriptor_sha256,
                args.codex_patch_manifest,
            )
        else:
            result = repair_process_registry_file(args.path, args.backup_dir)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (HotfixError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
