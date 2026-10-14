"""Exact native function bodies with explicit scenario bindings.

Results from this adapter are bundle checks. Mounted renderer proof remains
mandatory and is not produced by these synthetic dependency bindings.
"""
from pathlib import Path
import hashlib,json,subprocess
from functools import lru_cache
from frontend_feature_contracts import ContractError
import hotfix_profile_26930_6422 as p

ROOT=Path(__file__).resolve().parent/'codex_desktop_workflow/data'
ROWS=json.loads((ROOT/'frontend_bindings_26930_6422.json').read_text(encoding='utf8'))
BY={(r['role'],r['old']):r for r in ROWS}
GLOBALS={}
for r in ROWS:
    if r['failures']:raise ContractError('Unreviewed native closure')
    table=GLOBALS.setdefault(r['role'],{})
    for old,new in {r['old']:r['current'],**r['closure_bindings']}.items():
        previous=table.setdefault(new,old)
        if previous!=old:raise ContractError('Ambiguous native closure ownership')

@lru_cache(maxsize=8)
def index(raw,node='node'):
    cp=subprocess.run([node,str(ROOT/'frontend_index_bindings_26930_6422.cjs')],input=json.dumps({'entry':raw}),text=True,encoding='utf8',capture_output=True,timeout=40)
    if cp.returncode:raise ContractError('Native AST index failed: '+cp.stderr[-1200:])
    return json.loads(cp.stdout)['entry']

def native_function(raw,name,node='node'):
    candidates=[r for r in index(raw,node).get(name,[]) if r['kind']=='function']
    if not candidates:raise ContractError('Missing native function: '+name)
    depth=min(r['depth'] for r in candidates)
    candidates=[r for r in candidates if r['depth']==depth]
    if len(candidates)!=1:raise ContractError('Ambiguous native function: '+name)
    return candidates[0]['source']

def functions_from(raw,names,role,node='node',module=None):
    text=raw.decode('utf8') if isinstance(raw,bytes) else raw
    bodies={}
    for old in names:
        mapping=BY.get((role,old));native=mapping['current'] if mapping else old
        source=(module or p.ATTESTATION_MODULE).decode('utf8') if native=='qZp' else text
        bodies[old]=(native,native_function(source,native,node))
    payload=[{'role':role,'name':old,'target':native,'old':body,'current':body} for old,(native,body) in bodies.items()]
    cp=subprocess.run([node,str(ROOT/'frontend_map_closures_26930_6422.cjs')],input=json.dumps(payload),text=True,encoding='utf8',capture_output=True,timeout=40)
    if cp.returncode:raise ContractError('Native closure analysis failed: '+cp.stderr[-1200:])
    closures={r['old']:r for r in json.loads(cp.stdout)}
    result={}
    for old,(native,body) in bodies.items():
        free=closures[old]['current_free'];table=GLOBALS.get(role,{})
        getters=','.join('get '+n+'(){return typeof '+table.get(n,n)+"==='undefined'?mkStub("+json.dumps(table.get(n,n))+'):'+table.get(n,n)+'}' for n in free)
        result[old]=f'function {old}(...args){{with({{{getters}}}){{return ({body})(...args)}}}}'
    return result
