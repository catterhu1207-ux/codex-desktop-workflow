"""Execute the packaged idle cache and pending selector with isolated manager bindings."""
from pathlib import Path
import hashlib,json,subprocess
from frontend_feature_contracts import ContractError,_extract_function
import hotfix_profile_26928_4866 as profile
HELPERS=('RR','VR','c4t','l4t','Bm','qQt','Zm','JQ','l8t','zR','u4t','Um','If','JQt','YQt','nB','Qm','WQt','Xm','Jm','LJn','nde','ide','rde','ode','Km','que')
def run(shared,node='node'):
    text=shared.decode('utf8')
    payload={'entry':text,'helpers':{name:_extract_function(text,name) for name in HELPERS},'renderer_helper':'async '+_extract_function(profile.ATTESTATION_MODULE.decode('utf8'),'qualifyIdleCache')}
    cp=subprocess.run([node,str(Path(__file__).parent.joinpath('codex_desktop_workflow/data', 'frontend_idle_scenarios_26928_4866.cjs'))],input=json.dumps(payload),text=True,encoding='utf8',capture_output=True,timeout=45)
    if cp.returncode:raise ContractError('Native idle cache contract: '+cp.stderr[-2400:])
    result=json.loads(cp.stdout)
    if result.get('status')!='passed':raise ContractError('Native idle cache result incomplete')
    result['entry_sha256']=hashlib.sha256(shared).hexdigest()
    return result
