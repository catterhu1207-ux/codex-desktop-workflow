from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path


def load_builder(path: Path):
    spec = importlib.util.spec_from_file_location("hotfix_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def b(value: str) -> bytes:
    return value.encode("utf-8")


# Current profile for the official 26.803.10989.0 app-initial-KpqQCW_k.js
# bundle. The profile preserves the completed-plan unread indicator and Priority
# recency ordering, and restores saved remote-project identity through the
# current project merge and Work selector paths. The Work selector retains its
# original getter contract and filters only the ChatGPT mirror. Every replacement is exact,
# hash-gated, and the aggregate delta is paid only from the source-map footer.
PAIRS: dict[str, tuple[tuple[bytes, bytes], ...]] = {
    "plan_pending_unread_indicator": (
        (
            b("tt=zo(_Ar,n),nt=zo(xk,n),rt=$e??`local`,it;"),
            b("tt=zo(_Ar,n),nt=zo(xk,n),rt=$e??`local`,it;let Rr=zo(Srr,n);tt??=Array.isArray(Rr)&&Rr.some(e=>e?.method===TJt)?`plan`:null;"),
        ),
        (
            b("unreadCount:vt||Ne?0:Ze??0}"),
            b("unreadCount:vt||Ne?0:Ze??0,plan:tt}"),
        ),
        (
            b("if(n.unread===!0){let e;return t[3]===Symbol.for(`react.memo_cache_sentinel`)?(e=(0,b8.jsx)(JOc,{}),t[3]=e):e=t[3],e}return null}function qOc"),
            b("return n.unread?(0,b8.jsx)(JOc,{p:n.plan}):null}function qOc"),
        ),
        (
            b("if((n.unreadCount??0)>0)"),
            b("if((!n.plan||!n.unread)&&(n.unreadCount??0)>0)"),
        ),
        (
            b("function JOc(){let e=(0,XOc.c)(1),t;return e[0]===Symbol.for(`react.memo_cache_sentinel`)?(t=(0,b8.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center text-token-description-foreground`,children:(0,b8.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,b8.jsx)(`span`,{className:`absolute inset-0 rounded-full`,style:{backgroundColor:`var(--vscode-textLink-foreground)`}})})}),e[0]=t):t=e[0],t}"),
            b("function JOc({p:n}){let t=(0,XOc.c)(2),r;return t[0]===n?t[1]:(r=(0,b8.jsx)(`div`,{className:`relative flex size-5 shrink-0 items-center justify-center`,children:(0,b8.jsx)(`span`,{className:`icon-xs relative scale-50`,children:(0,b8.jsx)(`span`,{className:`absolute inset-0 rounded-full`,style:{backgroundColor:n?`var(--color-token-charts-yellow)`:`var(--vscode-textLink-foreground)`}})})}),t[0]=n,t[1]=r)}"),
        ),
    ),
    "priority_live_resort": (
        (
            b("Wyc=Ea(Q,(e,{get:t})=>c8o(Uyc(t,e).filter(({item:n})=>Tyc(t,n,e))))"),
            b("Wyc=Ea(Q,(e,{get:t})=>Uyc(t,e).filter(({item:n})=>Tyc(t,n,e)).sort((e,t)=>t.recencyAt-e.recencyAt))"),
        ),
        (
            b("let x=l(Wyc,u.sidebarMode),S=m==null?void 0:x.find(({item:e})=>{let t=j6(l,e);return t===j6(l,m.item)&&!f.has(t)})?.item,C=byc(l,[...S==null?[]:[S],...v,...x.map(({item:e})=>e)].filter(e=>!n.has(j6(l,e)))),w=l(A6)===!0,"),
            b("let x=l(Wyc,u.sidebarMode),A=l(GM),C=byc(l,[...x.map(({item:e})=>e),...v].filter(e=>!n.has(j6(l,e)))),F=v.findIndex(e=>j6(l,e)===A),I=C.findIndex(e=>j6(l,e)===A);~F&&~I&&C.splice(F,0,C.splice(I,1)[0]);let w=l(A6)===!0,"),
        ),
    ),
    "remote_project_label": (
        (
            b("function p8o(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return f8o(e.map(e=>r.get(e.projectId)??{...e,threadKeys:[]}),n)}"),
            b("function p8o(e,t,n){let r=new Map(t.map(e=>[e.projectId,e]));return f8o(e.map(e=>({...r.get(e.projectId)||{...e,threadKeys:[]},...e})),n)}"),
        ),
    ),
    "work_remote_project_picker": (
        (
            b("function ves(e){return e.filter(e=>e.projectKind===`local`&&!c8i(e))}"),
            b("function ves(e){return e.filter(e=>e.projectKind!==`chatgpt`)}"),
        ),
        (
            b("projects:d,onSelectProject:e=>{xV.select(u,e)}"),
            b("projects:d,onSelectProject:e=>{n0(u,e)}"),
        ),
        (
            b("f?.type===`local`?f.projectId:null"),
            b("f?.type!=`chatgpt`?f?.projectId:null"),
        ),
    ),
}


def main() -> int:
    builder = load_builder(Path(sys.argv[1]))
    asar = Path(sys.argv[2])
    entry_path = sys.argv[3]
    header_size, _, header = builder.read_asar(asar)
    meta = builder.get_entry_meta(header, entry_path)
    _, data = builder.read_entry(asar, header_size, meta)
    patched = data
    for feature, pairs in PAIRS.items():
        print(feature)
        for index, (old, new) in enumerate(pairs):
            counts = (patched.count(old), patched.count(new))
            print(index, counts, len(old), len(new), len(new) - len(old))
            if counts != (1, 0):
                raise RuntimeError(f"{feature}[{index}] unsafe: {counts}")
            patched = patched.replace(old, new, 1)
    print("source", len(data), hashlib.sha256(data).hexdigest())
    print("patched-unpadded", len(patched), hashlib.sha256(patched).hexdigest(), "delta", len(patched)-len(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
