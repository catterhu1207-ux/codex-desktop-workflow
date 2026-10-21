"""Run complete packaged row consumers with retained memo and synthetic state."""
import hashlib
from pathlib import Path
from .native_checks_4894 import extract,execute
import hotfix_builder as b
import hotfix_integration_261016_6573 as p
from frontend_feature_contracts import _with_module_stubs

def verify(portable):
    archive=Path(portable)/'resources/app.asar'
    if b.sha256_path(archive)!=p.TARGET_ASAR_SHA256:raise ValueError('6573 candidate differs')
    size,_,header=b.read_asar(archive)
    source=b.read_entry(archive,size,b.get_entry_meta(header,p.PROFILE['entry_path']))[1].decode()
    names=['mHc','bqc','oHc','MVc','Q2','qZDot','a7t','s7t','o7t','GJi','KJi','qJi','XJi','Ior','Lor','Z4894Plan']
    functions=extract(source,names,True)
    scenarios=(Path(__file__).parent/'data/native_row_6573.cjs').read_text()
    value=execute(_with_module_stubs('\n'.join(functions.values())+'\n'+scenarios,functions))
    negatives=[('parent_pin','bqc','qZPinned:O','qZPinned:!1','real parent pin prop lost'),
               ('async_request','XJi','n(UJi,{hostId:t,threadId:e})','!1','ongoing async question'),
               ('real_plan_source','mHc','qZRaw?.pendingRequest?.kind===`implementPlan`','!1','read plan yellow')]
    rejected=[]
    for label,name,before,after,expected in negatives:
        if functions[name].count(before)!=1:raise ValueError('Negative control source moved: '+label)
        changed=dict(functions);changed[name]=changed[name].replace(before,after)
        try:execute(_with_module_stubs('\n'.join(changed.values())+'\n'+scenarios,changed))
        except RuntimeError as error:
            if expected not in str(error):raise
            rejected.append(label)
        else:raise ValueError('Missing route incorrectly passes: '+label)
    value['negative_controls_rejected']=rejected
    value['function_sha256']={k:hashlib.sha256(v.encode()).hexdigest() for k,v in functions.items()}
    value['candidate_sha256']=p.TARGET_ASAR_SHA256
    return value
