"""Execute the version-bound complete row and its real pending selectors."""
import hashlib
from pathlib import Path
from .native_checks_4894 import extract,execute
import hotfix_builder as b
import hotfix_integration_261021_3705 as p
from frontend_feature_contracts import _with_module_stubs

def verify(portable):
    archive=Path(portable)/'resources/app.asar'
    if b.sha256_path(archive)!=p.TARGET_ASAR_SHA256:raise ValueError('3705 candidate differs')
    size,_,header=b.read_asar(archive)
    def read(name):return b.read_entry(archive,size,b.get_entry_meta(header,name))[1].decode()
    primary=read(p.PROFILE['secondary_entry_path']);initial=read(p.PROFILE['entry_path'])
    for token in ('OS as b_','pRt as h2e'):
        if primary.count(token)!=1:raise ValueError('3705 row import binding differs: '+token)
    for token in ('$ts as OS','pAi as pRt','N1n as CCn'):
        if initial.count(token)!=1:raise ValueError('3705 row export binding differs: '+token)
    functions=extract(primary,['LJn','RZn','vX','cJn'],True)
    functions.update(extract(initial,['$ts','qZDot','J9t','Y9t','NT','lAi','uAi','dAi','mAi','d$n','f$n','Z4894Plan'],True))
    scenarios=(Path(__file__).parent/'data/native_row_3705.cjs').read_text()
    value=execute(_with_module_stubs('\n'.join(functions.values())+'\n'+scenarios,functions))
    negatives=[('parent_pin','RZn','isPinned:D','isPinned:!1','real parent pin prop lost'),
               ('async_request','mAi','n(sAi,{hostId:t,threadId:e})','null','ongoing async question'),
               ('real_plan_source','LJn','qZRaw?.pendingRequest?.kind===`implementPlan`','!1','read plan yellow')]
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
