"""Execute the packaged idle cache and pending selector with isolated manager bindings."""
from pathlib import Path
import hashlib,json,subprocess
from frontend_feature_contracts import ContractError,_extract_function
import hotfix_profile_26930_7945 as profile
HELPERS=('SB','TB','R0t','z0t','Vm','bZt','Ym','p$','SH','CB','B0t','Um','wf','xZt','SZt','RV','Xm','_Zt','Jm','Km','zJn','ude','fde','dde','mde','Gm','tde')
def run(shared,node='node'):
    text=shared.decode('utf8')
    mapping={'F3t': 'I3t', 'I3t': 'L3t', 'L3t': 'R3t', 'dde': 'dde', 'oN': 'oN', 'JJn': 'YJn', 'xZt': 'SZt', 'Km': 'Km', 'ude': 'ude', 'aN': 'aN', 'tde': 'tde', 'b2t': 'x2t', '_Zt': 'vZt', 'Vm': 'Vm', 'Gm': 'Gm', 'SZt': 'CZt', 'R0t': 'z0t', 'fde': 'fde', 'Jm': 'Jm', 'z0t': 'B0t', 'k8t': 'A8t', 'SH': 'SH', 'RV': 'RV', 'mde': 'mde', 'Xm': 'Xm', 'Lyt': 'Lyt', 'bZt': 'xZt', 'Um': 'Um', 'Ym': 'Ym', 'B0t': 'V0t', 'zJn': 'BJn', 'CB': 'CB', 'wf': 'wf', 'p$': 'p$', 'TB': 'TB', 'qJn': 'JJn', 'SB': 'SB', 'Set': 'Set', 'Map': 'Map', '$ue': '$ue', 'Ff': 'Ff', 'Hm': 'Hm', 'sp': 'sp', 'ede': 'ede', 'rde': 'rde', 'KV': 'KV', 'Z': 'Z', 'fV': 'fV', 'JV': 'JV', 'IV': 'IV', 'Tj': 'Tj', 'I0t': 'L0t', 'V0t': 'H0t', 'gV': 'gV', 'LF': 'LF', 'Qm': 'Qm', 'xde': 'xde', 'UB': 'UB', '_8t': 'v8t', 'CV': 'CV', 'Zm': 'Zm', '$m': '$m', 'wB': 'wB', 'A8t': 'j8t', 'l8t': 'u8t', 'u8t': 'd8t', 'D8t': 'O8t', 'p8t': 'm8t', 'z1t': 'B1t', 'x8t': 'S8t', 'Error': 'Error', 'JSON': 'JSON', 'BJn': 'VJn', 'Nde': 'Nde', 'o': 'o', 'pHe': 'pHe', 'slt': 'slt', 'mHe': 'mHe', 'dlt': 'dlt', 'nA': 'nA', '$X': '$X', 'R3t': 'z3t'}
    from frontend_bindings_26930_7945 import native_function
    payload={'entry':text,'native_to_canonical':{v:k for k,v in mapping.items()},'helpers':{name:native_function(text,mapping.get(name,name),node) for name in HELPERS},'renderer_helper':'async '+_extract_function(profile.ATTESTATION_MODULE.decode('utf8'),'qualifyIdleCache')}
    cp=subprocess.run([node,str((Path(__file__).resolve().parent/'codex_desktop_workflow/data'/'frontend_idle_scenarios_26930_7945.cjs'))],input=json.dumps(payload),text=True,encoding='utf8',capture_output=True,timeout=45)
    if cp.returncode:raise ContractError('Native idle cache contract: '+cp.stderr[-2400:])
    result=json.loads(cp.stdout)
    if result.get('status')!='passed':raise ContractError('Native idle cache result incomplete')
    result['entry_sha256']=hashlib.sha256(shared).hexdigest()
    return result
