"""Execute the packaged idle cache and pending selector with isolated manager bindings."""
from pathlib import Path
import hashlib,json,subprocess
from frontend_feature_contracts import ContractError,_extract_function
import hotfix_profile_261002_7124 as profile
HELPERS=('SB','TB','R0t','z0t','Vm','bZt','Ym','p$','SH','CB','B0t','Um','wf','xZt','SZt','RV','Xm','_Zt','Jm','Km','zJn','ude','fde','dde','mde','Gm','tde')
def run(shared,node='node'):
    text=shared.decode('utf8')
    mapping={'F3t': 'Y9t', 'I3t': 'X9t', 'L3t': 'Z9t', 'dde': 'Kde', 'oN': 'AM', 'JJn': 'OZn', 'xZt': 'DZn', 'Km': 'mm', 'ude': 'Gde', 'aN': 'kM', 'tde': 'Ide', 'b2t': 'x2t', '_Zt': 'g0t', 'Vm': 'lm', 'Gm': 'pm', 'SZt': 'x0t', 'R0t': 'F8t', 'fde': 'qde', 'Jm': 'gm', 'z0t': 'I8t', 'k8t': 'Ytn', 'SH': 'q9t', 'RV': 'AB', 'mde': 'Yde', 'Xm': 'vm', 'Lyt': 'Bbt', 'bZt': 'y0t', 'Um': 'dm', 'Ym': '_m', 'B0t': 'L8t', 'zJn': 'vZn', 'CB': 'Tz', 'wf': 'sf', 'p$': 'XQ', 'TB': 'Dz', 'qJn': 'DZn', 'SB': 'wz', 'Set': 'Set', 'Map': 'Map', '$ue': '$ue', 'Ff': 'vf', 'Hm': 'um', 'sp': 'Pf', 'ede': 'Fde', 'rde': 'Rde', 'KV': 'RB', 'Z': 'Z', 'fV': 'mB', 'JV': 'BB', 'IV': 'OB', 'Tj': 'XA', 'I0t': 'L0t', 'V0t': 'H0t', 'gV': 'Nz', 'LF': 'fP', 'Qm': 'bm', 'xde': 'nfe', 'UB': '$z', '_8t': 'Ltn', 'CV': 'bB', 'Zm': 'ym', '$m': 'xm', 'wB': 'Ez', 'A8t': 'Xtn', 'l8t': 'Otn', 'u8t': 'ktn', 'D8t': 'qtn', 'p8t': 'Mtn', 'z1t': 'C6t', 'x8t': 'Vtn', 'Error': 'Error', 'JSON': 'JSON', 'BJn': 'yZn', 'Nde': 'mfe', 'o': 'o', 'pHe': 'GHe', 'slt': 'klt', 'mHe': 'KHe', 'dlt': 'Nlt', 'nA': 'nA', '$X': '$X', 'R3t': 'Q9t', 'CH': 'J9t'}
    from frontend_bindings_261002_7124 import native_function
    payload={'entry':text,'native_to_canonical':{v:k for k,v in mapping.items()},'helpers':{name:native_function(text,mapping.get(name,name),node) for name in HELPERS},'renderer_helper':'async '+_extract_function(profile.ATTESTATION_MODULE.decode('utf8'),'qualifyIdleCache')}
    cp=subprocess.run([node,str((Path(__file__).resolve().parent/'codex_desktop_workflow/data'/'frontend_idle_scenarios_261002_7124.cjs'))],input=json.dumps(payload),text=True,encoding='utf8',capture_output=True,timeout=45)
    if cp.returncode:raise ContractError('Native idle cache contract: '+cp.stderr[-2400:])
    result=json.loads(cp.stdout)
    if result.get('status')!='passed':raise ContractError('Native idle cache result incomplete')
    result['entry_sha256']=hashlib.sha256(shared).hexdigest()
    return result
