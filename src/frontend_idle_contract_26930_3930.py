"""Execute the packaged idle cache and pending selector with isolated manager bindings."""
from pathlib import Path
import hashlib,json,subprocess
from frontend_feature_contracts import ContractError,_extract_function
import hotfix_profile_26930_3930 as profile
HELPERS=('SB','TB','R0t','z0t','Vm','bZt','Ym','p$','SH','CB','B0t','Um','wf','xZt','SZt','RV','Xm','_Zt','Jm','Km','zJn','ude','fde','dde','mde','Gm','tde')
def run(shared,node='node'):
    text=shared.decode('utf8')
    payload={'entry':text,'helpers':{name:_extract_function(text,name) for name in HELPERS},'renderer_helper':'async '+_extract_function(profile.ATTESTATION_MODULE.decode('utf8'),'qualifyIdleCache')}
    cp=subprocess.run([node,str((Path(__file__).resolve().parent/'codex_desktop_workflow/data'/'frontend_idle_scenarios_26930_3930.cjs'))],input=json.dumps(payload),text=True,encoding='utf8',capture_output=True,timeout=45)
    if cp.returncode:raise ContractError('Native idle cache contract: '+cp.stderr[-2400:])
    result=json.loads(cp.stdout)
    if result.get('status')!='passed':raise ContractError('Native idle cache result incomplete')
    result['entry_sha256']=hashlib.sha256(shared).hexdigest()
    return result
