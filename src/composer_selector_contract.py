"""Exact 26.901 lazy Work selector patch and actual component-chain regression.

Host hooks are fixture boundaries; label/search/selection logic is extracted
verbatim from the shipped modules, never reimplemented as a Python resolver.
This is bundle qualification, not a substitute for isolated/live UI evidence.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess

ENTRY_PATH = "webview/assets/composer-project-selector-17ef0c338d41.js"
SOURCE_SHA256 = "7ed9a98ee7a6103f05054d1eb771195a0b6fa67cb873ed406b90db617f195481"

# One exact selector chunk per package identity.  The 26.908 bundle re-split
# the Work-mode picker: the raw REMOTE_PROJECTS hook now lives in the initial
# chunk and the selector reads the merged project list through the primary
# chunk atoms, so its replacement set is not interchangeable with 26.903.
ENTRY_PATH_BY_VERSION = {
    "26.901.6511.0": "webview/assets/composer-project-selector-65006fbfe982.js",
    "26.903.9818.0": ENTRY_PATH,
    "26.908.4834.0": "webview/assets/composer-project-selector-82b3c6b0c53d.js",
}
SOURCE_SHA256_BY_VERSION = {
    "26.901.6511.0": "a04df51ca0e741a679022d497e09de847b858366b40dbb137e6aabd8308fe44b",
    "26.903.9818.0": SOURCE_SHA256,
    "26.908.4834.0": "54a8e9bf9df7b2f2ae0ce4cc505c81953c16954aaa8640cd2341672f6e34cefe",
}
PAIRS_BY_VERSION = {
    "26.903.9818.0": None,  # filled below with PAIRS
    "26.908.4834.0": None,
}


def entry_path_for(profile) -> str:
    if profile is None:
        return ENTRY_PATH
    version = str(profile.get("package_version") or "")
    path = profile.get("composer_selector_entry_path") or ENTRY_PATH_BY_VERSION.get(
        version
    )
    if not path:
        raise KeyError(f"No composer-selector entry for {version}")
    return str(path)


def source_sha256_for(profile) -> str:
    if profile is None:
        return SOURCE_SHA256
    version = str(profile.get("package_version") or "")
    digest = SOURCE_SHA256_BY_VERSION.get(version)
    if not digest:
        raise KeyError(f"No composer-selector source hash for {version}")
    return digest


def pairs_for(profile):
    if profile is None:
        return PAIRS
    version = str(profile.get("package_version") or "")
    return PAIRS_BY_VERSION.get(version) or PAIRS
PAIRS = (
    (b"import{$qt as t,", b"import{_3 as q,$qt as t,"),
    (b"g=h?.type===`local`?h.projectId:null", b"g=h?.projectId??null"),
    (
        b"x=n(s),S=r(D)",
        b"x=[...r(s),...r(q).filter(e=>e.projectKind===`remote`)],S=r(D)",
    ),
    (
        b"z=A?{projects:S,onSelectProject:e=>{v(x,{...e,projectKind:`local`})}}:void 0",
        b"z={projects:S.filter(e=>A||e.projectKind===`remote`),onSelectProject:e=>{v(x,e)}}",
    ),
)

# 26.908: the selector imports the merged remote-project atom from the initial
# chunk, keeps the trigger fallback for any project kind, merges remote
# projects into the selection scope and preserves the real project kind when
# the picker reports a selection.
PAIRS_26908 = (
    (b"import{A6t as n,", b"import{att as q,A6t as n,"),
    (b"g=h?.type===`local`?h.projectId:null", b"g=h?.projectId??null"),
    (
        b"b=s(l),x=n(C),S=n(y)",
        b"b=s(l),x=[...n(C),...n(q).filter(e=>e.projectKind===`remote`)],S=n(y)",
    ),
    (
        b"z=A?{projects:x,onSelectProject:e=>{r(b,{...e,projectKind:`local`})}}:void 0",
        b"z={projects:x.filter(e=>A||e.projectKind===`remote`),onSelectProject:e=>{r(b,e)}}",
    ),
)

PAIRS_BY_VERSION["26.903.9818.0"] = PAIRS
PAIRS_BY_VERSION["26.908.4834.0"] = PAIRS_26908


def patch(entry: bytes, profile=None) -> bytes:
    from hotfix_builder import HotfixError, equalize_current_entry_length
    expected = source_sha256_for(profile)
    replacements = pairs_for(profile)
    if hashlib.sha256(entry).hexdigest() != expected:
        raise HotfixError("Work selector official source hash differs")
    result = entry
    for old, new in replacements:
        if result.count(old) != 1 or new in result:
            raise HotfixError("Work selector signature missing or ambiguous")
        result = result.replace(old, new, 1)
    result = equalize_current_entry_length(entry, result)
    if len(result) != len(entry) or any(
        result.count(new) != 1 for _, new in replacements
    ):
        raise HotfixError("Work selector equal-length patch did not converge")
    return result


def fixture_script(
    initial: bytes, primary: bytes, selector: bytes, page: bytes,
    release: str = "26903",
) -> str:
    def _strip_js_literals(text: str) -> str:
        """Blank out string, template and comment contents so scans see only code."""
        out: list[str] = []
        index = 0
        length = len(text)
        while index < length:
            char = text[index]
            if char in "\"'`":
                quote = char
                index += 1
                while index < length:
                    if text[index] == "\\":
                        index += 2
                        continue
                    if text[index] == quote:
                        index += 1
                        break
                    index += 1
                out.append(" ")
                continue
            if char == "/" and index + 1 < length and text[index + 1] == "/":
                while index < length and text[index] != "\n":
                    index += 1
                continue
            if char == "/" and index + 1 < length and text[index + 1] == "*":
                index += 2
                while index + 1 < length and not (
                    text[index] == "*" and text[index + 1] == "/"
                ):
                    index += 1
                index += 2
                continue
            out.append(char)
            index += 1
        return "".join(out)

    from frontend_feature_contracts import ContractError, _extract_function
    is_26908 = release == "26908" or b"att as q" in selector
    modern = is_26908 or b"ra as O" in selector
    anchors_26908 = (
        (initial, b"eV as att"),
        (initial, b"$_a as RB"),
        (selector, b"att as q"),
        (selector, b"r_ as O"),
        (selector, b"as ComposerProjectSelector"),
        (initial, b"import(`./composer-project-selector-e0cbbf7896dc.js`)" if release == "26908_9136" else b"import(`./composer-project-selector-82b3c6b0c53d.js`)"),
        (primary, b"trt as Sze"),
        (primary, b"Bet as Gn"),
        (page, b"trt as Re"),
        (
            page,
            b"jsx)(me,{menuOpen:mt,onMenuOpenChange:gt,projectId:h,shortcut:_t,subtleHover:!0}",
        ),
    )
    anchors_modern = (
        (initial, b"vFi as _3"),
        (initial, b"D1a as JF"),
        (selector, b"ra as O"),
        (selector, b"zF as v"),
        (selector, b"as ComposerProjectSelector"),
        (primary, b"DH as Gi"),
        (primary, b"Rwr as do"),
        (primary, b"import(`./composer-project-selector-17ef0c338d41.js`)"),
        (page, b"Oo as Je"),
        (
            page,
            b"jsx)(Je,{menuOpen:et,onMenuOpenChange:tt,projectId:f,shortcut:it,subtleHover:!0}",
        ),
    )
    anchors_legacy = (
        (initial, b"sAi as f4"),
        (initial, b"Y$ as yF"),
        (selector, b"Ki as C"),
        (selector, b"yF as v"),
        (selector, b"A as ComposerProjectSelector"),
        (primary, b"DSr as Ki"),
        (primary, b"e6 as do"),
        (primary, b'import(`./composer-project-selector-65006fbfe982.js`)'),
        (page, b"do as gt"),
        (
            page,
            b"jsx)(gt,{menuOpen:lt,onMenuOpenChange:ut,projectId:l,shortcut:dt,subtleHover:!0}",
        ),
    )
    if is_26908:
        anchors = anchors_26908
    elif modern:
        anchors = anchors_modern
    else:
        anchors = anchors_legacy
    for entry, anchor in anchors:
        if entry.count(anchor) != 1:
            raise ContractError("Actual Work selector consumer is disconnected: " + anchor.decode())
    extract = lambda entry, name: _extract_function(entry.decode("utf-8"), name)
    if is_26908:
        shared_names = ("u1n", "d3", "p1n", "s1n")
    elif modern:
        shared_names = ("HMr", "IMr", "GMr", "zMr")
    else:
        shared_names = ("DSr", "xSr", "ASr", "wSr")
    wrapper_names = ("A", "j")
    route_name = "$_a" if is_26908 else ("q1a" if modern else "mJa")
    shared = "\n".join(extract(primary, name) for name in shared_names)
    wrappers = "\n".join(extract(selector, name) for name in wrapper_names)
    route = extract(initial, route_name)
    module_stubs = ""
    if modern:
        fixture_declared = {
            "jSr", "g8", "TSr", "h8", "MSr", "me", "bS", "EEn", "kx",
            "aZ", "QZ", "Dv", "Uv", "X", "oy", "Iv", "Kx", "Zp", "OO",
            "U4", "hSr", "vSr", "q4", "Sy", "OSr", "tD", "kSr", "SSr",
            "ht", "ids", "names", "remotes", "local", "originals",
            "wrapper", "walk", "results", "search", "cloud",
            "localEnabled", "selection", "cloudSelection", "assert",
            "memo", "jsx", "n", "e", "t", "r",
            "mkStub", "emptyProjects", "localProjectOptions",
            "Ms", "currentProject",
        }
        module_names = sorted(
            {
                match.group(1)
                for match in re.finditer(
                    r"(?<![A-Za-z0-9_$.])([A-Za-z_$][\w$]*)\."
                    r"(?:c|jsx|jsxs|Fragment|default|Provider|useRef|useState)\b",
                    shared + wrappers + route,
                )
            }
            - {"M", "N"}
            - fixture_declared
        )
        module_stubs = "".join(
            f"const {name}={{c:memo,jsx,jsxs:jsx,Fragment:'fragment',"
            "default:(v)=>v,useRef:v=>({current:v}),"
            "useState:v=>[typeof v==='string'?search:v,()=>{}]};\n"
            for name in module_names
        )
        body = shared + wrappers + route
        declared = set(
            re.findall(r"function\s+([A-Za-z_$][\w$]*)", body)
        ) | set(re.findall(r"(?:let|const|var)\s+([A-Za-z_$][\w$]*)", body))
        clean = _strip_js_literals(body)
        free = {
            match.group(0)
            for match in re.finditer(r"[A-Za-z_$][\w$]*", clean)
            if not clean[: match.start()].rstrip().endswith(".")
            and not (
                clean[match.end():].lstrip().startswith(":")
                and not clean[: match.start()].rstrip().endswith("?")
            )
        }
        reserved = {
            "if", "for", "while", "switch", "catch", "return", "typeof", "function",
            "break", "case", "class", "const", "continue", "default", "delete",
            "do", "else", "export", "extends", "finally", "import", "in",
            "instanceof", "let", "new", "of", "super", "this", "throw", "try",
            "var", "void", "with", "yield", "await", "async", "enum", "null",
            "true", "false", "undefined", "arguments", "eval",
            "M", "N", "r", "T", "k", "x", "s", "D", "_", "i", "E", "y", "c", "u",
            "h", "O", "S", "v", "m", "j", "A", "assert", "memo", "jsx", "walk",
            "String", "Object", "Array", "Symbol", "Math", "Number", "Boolean", "Map",
            "Set", "JSON", "Error", "Promise", "getComputedStyle", "document",
        }
        callable_stubs = "".join(
            f"globalThis.{name}=mkStub('{name}');\n"
            for name in sorted(
                (free - declared - reserved - set(module_names) - fixture_declared)
                | {"z"}
            )
        )
        module_stubs += callable_stubs
        module_stubs += (
            "globalThis.G4={Item:'item',Action:'action',Separator:'separator',"
            "Label:'label',Group:'group'};\n"
            "globalThis.q4={Item:'item',Action:'action'};\n"
            "globalThis.rv=(value)=>value;\n"
            "globalThis.ag=(arg)=>{if(arg===undefined)return{"
            "formatMessage:(m,v)=>String(m?.defaultMessage??'').replace('{projectName}',v?.projectName??'')};"
            "return{projectId:remotes[2].projectId,projectKind:'remote',projectName:remotes[2].label,"
           "label:remotes[2].label,hostId:remotes[2].hostId,path:remotes[2].path};};\n"
       )
        if is_26908:
            module_stubs += (
                "globalThis.$ee=(value)=>value;\n"
                # Menu primitives must keep stable element types so the
                # fixture can walk the real rendered option tree.
                "globalThis.K1={Item:'item',Action:'action',Separator:'separator',"
                "Label:'label',Group:'group'};\n"
                "globalThis.tS={Message:'message'};\n"
                # The composer picker reads the cloud project section through
                # the primary-chunk hook `Y`; the fixture injects the same
                # gizmo-shaped descriptors the real route returns.
                "globalThis.Y=()=>({isError:false,isLoading:false,projects:cloud});\n"
            )
    if is_26908:
        wrapper_stubs = (
            "const M={c:memo},N={jsx,jsxs:jsx},o='selected',l={id:'store'},C={id:'local-projects'},q={id:'remote-projects'},"
            "y='pending',c='capability',f='capability';\n"
            "const n=function(atom){if(arguments.length===0)return{data:localProjectOptions.projects};return atom===C?[local]:atom===q?remotes:atom===o?{type:'remote',projectId:ids[2]}:atom===y?[]:atom===c?localEnabled:null};\n"
            "const store={get:()=>null,set:()=>{},query:{setData:()=>{}},scope:l};\n"
            "const s=atom=>{assert(atom===l,'store hook input');return store};\n"
            "const D=(ctx,value)=>{if(value&&value.projectId){"
            "assert(ctx===store,'cloud selection store context');"
            "const full=remotes.find(r=>r.projectId===value.projectId);"
            "selection={descriptor:full??value,route:fixtureRoute(full??value)};}};\n"
            "const r=(ctx,descriptor)=>{assert(ctx===store,'project selection store context');selection={descriptor,route:fixtureRoute(descriptor)}};\n"
            "const a=()=>({isCapable:true,isLoading:false}),T=Object.assign(()=>'allowed',"
            "{formatMessage:(m,v)=>String(m?.defaultMessage??'').replace('{projectName}',v?.projectName??'')});\n"
            "const p=ctx=>{assert(ctx===store,'clear store context')},E=(ctx,cb)=>{assert(ctx===store,'create store context');cb({gizmo:{id:'g-p-example',display:{name:'Cloud project'}}});};\n"
            "const u=z=>z===o?{type:'remote',projectId:ids[2]}:z===l?store:z===C?[local]:z===q?remotes"
            ":z===y?[]:z===c?localEnabled:null;\n"
            "const h=()=>({isCapable:true,isLoading:false}),O=()=> 'allowed',m=()=>{},w=()=>null,"
            "S=(x,v)=>{cloudSelection=v};\n"
        )
    elif modern:
        wrapper_stubs = (
            "const M={c:memo},N={jsx,jsxs:jsx},o='selected',b='local',q='all',"
            "p='local-enabled',a='store',t='capability';\n"
            "const y=(key,value)=>{if(value&&value.projectId){"
            "const full=remotes.find(r=>r.projectId===value.projectId);"
            "selection={descriptor:full??value,route:fixtureRoute(full??value)};}};\n"
            "const D={id:'projects'},r=atom=>{if(atom===D)return remotes;"
            "const inherited=[...remotes];inherited.projectId=remotes[2].projectId;"
            "inherited.hostId=remotes[2].hostId;inherited.path=remotes[2].path;return inherited;},"
            "T=Object.assign(()=>'allowed',{formatMessage:(m,v)=>String(m?.defaultMessage??'').replace('{projectName}',v?.projectName??'')}),"
            "k={isCapable:true,isLoading:false},x='ctx',s='ctx',_=null,"
            "i=()=>({isCapable:true,isLoading:false}),"
            "E=(ctx,cb)=>cb({gizmo:{id:'g-p-example',display:{name:'Cloud project'}}});\n"
            "const u=z=>z===o?{type:'remote',projectId:ids[2]}:z===b?[local]:z===q?[local,...remotes]"
            ":z===y?[]:z===p?localEnabled:null,c=()=>({}),h=()=>({isCapable:true,isLoading:false}),"
            "O=()=> 'allowed',S=(x,v)=>{cloudSelection=v},"
            "v=(x,d)=>{selection={descriptor:d,route:fixtureRoute(d)}},m=()=>{},"
            "C=Object.assign(DSr,{includes:()=>false});\n"
        )
    else:
        wrapper_stubs = (
            "const M={c:memo},N={jsx,jsxs:jsx},o='selected',b='local',q='all',"
            "p='local-enabled',a='store',t='capability';\n"
            "const y='pending';\n"
            "const u=z=>z===o?{type:'remote',projectId:ids[2]}:z===b?[local]:z===q?[local,...remotes]"
            ":z===y?[]:z===p?localEnabled:null,c=()=>({}),h=()=>({isCapable:true,isLoading:false}),"
            "O=()=> 'allowed',S=(x,v)=>{cloudSelection=v},"
            "v=(x,d)=>{selection={descriptor:d,route:fixtureRoute(d)}},m=()=>{},E=()=>{},C=DSr;\n"
        )
    script = r'''
(()=>{
const assert=(v,m)=>{if(!v)throw Error(m)}, memo=()=>new Array(200).fill(Symbol.for('react.memo_cache_sentinel'));
const jsx=(type,props,key)=>({type,props:props||{},key}),g8={jsx,jsxs:jsx,Fragment:'fragment'},jSr={c:memo};
let search='',cloud=[],localEnabled=true,selection=null,cloudSelection=null;
const MSr={useRef:v=>({current:v}),useState:v=>[typeof v==='string'?search:v,()=>{}]},me=()=>({formatMessage:(m,v)=>m.defaultMessage.replace('{projectName}',v?.projectName??'')}),bS=()=>({isError:false,isLoading:false,projects:cloud}),EEn={},kx=()=>{};
const TSr=jSr,h8=g8,aZ='host-icon',QZ='project-icon',Dv='icon',Uv={},X='intl',oy='loading',Iv='selected',Kx='add',Zp='clear',OO='button',U4='menu',hSr='trigger',vSr='items',q4={Item:'item',Action:'action'},Sy={Message:'message'},OSr=()=>null,tD=()=>[],kSr=e=>[e.gizmo.display.name];
// Third-party fuzzy scorer/sort library boundaries; xSr's real field routing
// and filtering are executed below. Full search is exercised in isolated UI.
const SSr={default:(a,f)=>a.sort((x,y)=>f(x)-f(y))},ht=(s,q)=>String(s).toLowerCase().includes(q.toLowerCase())?1:0;
''' + ((
        "const mkStub=(name)=>new Proxy(function(){return mkStub(name);},{"
        "get:(t,k)=>{"
        "if(k==='__stub')return name;"
        "if(k===Symbol.iterator)return function*(){};"
        "if(k==='length')return 0;"
        "if(k==='find'||k==='filter'||k==='map'||k==='slice'||k==='concat'||k==='flatMap')"
        "return (...a)=>[];"
        "if(k==='some'||k==='every')return (...a)=>k==='every';"
        "if(k==='includes')return ()=>false;"
        "if(k==='join')return ()=>'';"
        "if(k===Symbol.toPrimitive)return undefined;"
        "if(k==='valueOf'||k==='toString')return ()=>'';"
        "if(k==='name')return name;"
        "if(k==='then')return undefined;"
        "return mkStub(name);},"
        "apply:(t,self,args)=>{"
        "if(args&&args.length>=2&&typeof args[0]==='string'&&typeof args[1]==='string')"
        "return String(args[0]).toLowerCase().includes(String(args[1]).toLowerCase())?1:0;"
        "return mkStub(name);},has:()=>true});\n"
        "const emptyProjects=()=>({projects:[]});\n"
        "let currentProject=null;\n"
        "globalThis.Ms=(atom)=>({isError:false,isLoading:false,"
        "projects:atom===globalThis.$jn?cloud:[],"
        "projectId:remotes[2].projectId,projectKind:'remote',projectName:remotes[2].label,"
        "formatMessage:(m,v)=>String(m?.defaultMessage??'').replace('{projectName}',v?.projectName??''),"
        "chatSortMode:'updated_at',projectSortMode:'updated_at'});\n"
        "const localProjectOptions={get projects(){return [local,...remotes]}};\n"
    ) if modern else "") + module_stubs + shared + "\n" + "const fixtureRoute=(()=>{const yv=v=>v;" + route + ";return mJa;})();" + r'''
const ids=['c87575b4-dba0-471e-a647-31ce8575c46b','423dd422-a9ef-4fc4-8c97-583483a49850','050ce269-9b40-44e3-ac49-b67bb85d0c42','48d6231d-156e-493a-a7e3-d3610a38a080'],names=['mailassistant','report-generator','ensolventia','automatic-score'];
const remotes=ids.map((id,i)=>({projectId:id,groupId:id,projectKind:'remote',hostId:'remote-ssh-discovered:Insolvency',hostDisplayName:'Insolvency',path:'/root/'+names[i],label:names[i],gitRepos:[],threadKeys:['t'+i]})),local={projectId:'local-1',projectKind:'local',label:'Local project',name:'Local project',displayName:'Local project',path:'C:/example',gitRepos:[]};
const originals=JSON.stringify(remotes);
const wrapper=(()=>{
''' + wrapper_stubs + wrappers + r'''
return props=>{currentProject=remotes.find(r=>r.projectId===props.projectId)??(props.projectId===local.projectId?local:null);let a=A({...props,localProjectOptions,projectName:currentProject?.label??props.projectName});return a.type===j?j(a.props):a};
})();
const walk=(e,type)=>{if(!e||typeof e!=='object')return null;if(e.type===type)return e;for(const v of Object.values(e.props??e)){if(Array.isArray(v)){for(const a of v){const r=walk(a,type);if(r)return r}}else{const r=walk(v,type);if(r)return r}}return null};
const results=[];
console.error("DIAG z="+(()=>{try{return typeof z}catch(e){return "TDZ"}})()+" y="+(()=>{try{return typeof y}catch(e){return "TDZ"}})()+" gz="+String(Object.prototype.hasOwnProperty.call(globalThis,"z")));
for(let i=0;i<ids.length;i++){
search='';let middle=wrapper({projectId:ids[i],menuOpen:true}),out=(()=>{try{return DSr(middle.props)}catch(e){throw Error(e.message+' [DIAG z:'+(()=>{try{return typeof z}catch(x){return 'TDZ'}})()+' gz:'+Object.prototype.hasOwnProperty.call(globalThis,'z')+' y:'+(()=>{try{return typeof y}catch(x){return 'TDZ'}})()+'] '+'\\n'+String(e.stack).slice(0,900))}})();
assert(out.props.value===names[i],'button label '+names[i]+' actual='+String(out.props.value?.__stub??out.props.value)+' keys='+Object.keys(out.props).join(','));assert(out.props['aria-label'].endsWith(names[i]),'aria label');
 const options=walk(out,wSr);assert(options,'actual menu route');const list=wSr(options.props),node=walk(list,'item');assert(node,'rendered option keys='+(options?Object.keys(options.props).join('|'):'none')+' groups='+String(list?.props?.groups?.length)+' children='+String(Array.isArray(list?.props?.children)?list.props.children.length:typeof list?.props?.children));
 search=names[i];out=DSr(wrapper({projectId:ids[i],menuOpen:true}).props);const filtered=walk(out,wSr);assert(filtered.props.groups.length===1&&filtered.props.groups[0].projectId===ids[i],'human-name search len='+String(filtered.props.groups?.length)+' first='+String(filtered.props.groups?.[0]?.projectId)+' want='+ids[i]+' search='+search);
const selected=walk(wSr(filtered.props),'item');selected.props.onSelect();assert(selection.route.type==='remote'&&selection.route.projectId===ids[i],'SSH selection route sel='+JSON.stringify(selection.route)+' desc='+JSON.stringify(selection.descriptor)+' itemType='+String(typeof selected.props.onSelect));assert(selection.descriptor.hostId===remotes[i].hostId&&selection.descriptor.path===remotes[i].path,'SSH identity');
 results.push({label:out.props.value,aria_label:out.props['aria-label'],project_id:ids[i],route:selection.route});
}
search='';localEnabled=false;let mid=wrapper({projectId:ids[2]}),out=DSr(mid.props);assert(mid.props.localProjectOptions.projects.length===4&&out.props.value==='ensolventia','remote without local capability');
out=DSr(wrapper({}).props);assert(out.props.value==='ensolventia','inherited remote selection got='+String(out.props.value?.__stub??out.props.value)+' keys='+Object.keys(out.props).join(','));
localEnabled=true;out=DSr(wrapper({projectId:local.projectId}).props);assert(out.props.value==='Local project','local preservation got='+String(out.props.value?.__stub??out.props.value)+' list='+localProjectOptions.projects.map(e=>String(e.projectId)+':'+String(e.label??e.projectName)).join('|'));walk(out,wSr).props.onSelectProject(local);assert(selection.route.type==='local','local route');
cloud=[{gizmo:{id:'g-p-example',display:{name:'Cloud project'}}}];out=DSr(wrapper({projectId:'g-p-example'}).props);assert(out.props.value==='Cloud project','cloud preservation');
out.props.onClearProject();assert(cloudSelection===null,'clear route');
remotes[2]={...remotes[2],label:'Renamed SSH'};out=DSr(wrapper({projectId:ids[2]}).props);assert(out.props.value==='Renamed SSH','rename rerender');remotes[2]={...remotes[2],label:names[2]};assert(JSON.stringify(remotes)===originals,'source descriptors unchanged');
return {status:'passed',executed:['A','j','DSr','xSr','ASr','wSr','mJa'],results,visible_uuid_count:0,local_and_cloud_preserved:true,remote_kind_preserved:true,source_descriptors_unchanged:true};
})()
'''
    if is_26908:
        for old_name, new_name in (
            ("DSr", "u1n"),
            ("xSr", "d3"),
            ("ASr", "p1n"),
            ("wSr", "s1n"),
            ("mJa", "$_a"),
        ):
            script = re.sub(
                r"(?<![A-Za-z0-9_$])" + re.escape(old_name) + r"(?![A-Za-z0-9_$])",
                new_name,
                script,
            )
    elif modern:
        for old_name, new_name in (
            ("DSr", "HMr"),
            ("xSr", "IMr"),
            ("ASr", "GMr"),
            ("wSr", "zMr"),
            ("mJa", "q1a"),
        ):
            script = re.sub(
                r"(?<![A-Za-z0-9_$])" + re.escape(old_name) + r"(?![A-Za-z0-9_$])",
                new_name,
                script,
            )
    return script


def validate(
    initial: bytes, primary: bytes, selector: bytes, page: bytes, node: str,
    release: str = "26903",
) -> dict:
    from frontend_feature_contracts import ContractError
    script = fixture_script(initial, primary, selector, page, release)
    process = subprocess.run([node, "-"], input="process.stdout.write(JSON.stringify(" + script + "));", text=True, encoding="utf-8", capture_output=True, timeout=30)
    if process.returncode:
        raise ContractError("Actual Work selector chain failed: " + process.stderr[-1800:])
    result = json.loads(process.stdout)
    result["script_sha256"] = hashlib.sha256(script.encode()).hexdigest()
    return result

ENTRY_PATH_BY_VERSION["26.908.9136.0"] = "webview/assets/composer-project-selector-e0cbbf7896dc.js"
SOURCE_SHA256_BY_VERSION["26.908.9136.0"] = "cf6600cf17a1d48c784c383d0c61e6dc3ec0dce3e65d943130295e7305e09cec"
PAIRS_BY_VERSION["26.908.9136.0"] = PAIRS_26908
