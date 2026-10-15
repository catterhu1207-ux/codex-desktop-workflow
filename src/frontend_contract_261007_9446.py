"""Exact 9446 source preparation; semantics require fresh native runtime."""
from pathlib import Path
import hashlib,json,subprocess
from codex_desktop_workflow.awake_process import capture as run_awake
import hotfix_builder as b
import hotfix_profile_261007_9446 as p
from frontend_feature_contracts import ContractError,_validate_renderer_probe
from frontend_ssh_261007_9446 import require_routes
VALIDATOR_VERSION='2.7.0'
def validate_source(source_asar,portable_asar,node='node'):
    source_asar,portable_asar=Path(source_asar),Path(portable_asar)
    if b.sha256_path(source_asar)!=p.PROFILE['asar_source_sha256']:
        raise ContractError('Exact official 9446 ASAR identity differs')
    source_size,_,source_header=b.read_asar(source_asar)
    target_size,_,target_header=b.read_asar(portable_asar)
    srcfiles=dict(b.walk_entries(source_header['files']));dstfiles=dict(b.walk_entries(target_header['files']))
    if set(srcfiles)!=set(dstfiles):raise ContractError('9446 archive entry inventory changed')
    roles=[('entry_path',lambda raw:b.patch_current_frontend_entry(raw,profile=p.PROFILE)[0]),('secondary_entry_path',lambda raw:b.patch_profile_secondary_entry(raw,p.PROFILE)[0]),('shared_entry_path',lambda raw:b.patch_profile_shared_entry(raw,p.PROFILE)),('main_entry_path',lambda raw:b.patch_portable_update_status_entry(raw,p.PROFILE)),('attestation_protocol_entry_path',lambda raw:b.patch_frontend_attestation_protocol_entry(raw,p.PROFILE))]
    originals={};patched={};transforms=[]
    for key,fn in roles:
        path=p.PROFILE[key];raw=b.read_entry(source_asar,source_size,srcfiles[path])[1];out=b.read_entry(portable_asar,target_size,dstfiles[path])[1]
        sha_key=key.replace('_path','_source_sha256').replace('attestation_protocol_entry_source','attestation_protocol_source')
        if b.sha256_bytes(raw)!=p.PROFILE[sha_key]:raise ContractError('Official entry hash differs: '+key)
        expected=fn(raw)
        if len(raw)!=len(out) or expected!=out:raise ContractError('Actual 9446 transformation differs: '+key)
        cp=run_awake([node,'--input-type=module','--check'],input=out,capture_output=True,timeout=45,creationflags=0x08000000)
        if cp.returncode:raise ContractError('Actual patched entry syntax failed: '+key)
        originals[key]=raw;patched[key]=out;transforms.append({'path':path,'source_sha256':b.sha256_bytes(raw),'portable_sha256':b.sha256_bytes(out),'length':len(out)})
    changed={p.PROFILE[key]for key,_ in roles};unchanged=0;unpacked=0;digest=hashlib.sha256()
    for path,meta in srcfiles.items():
        if path in changed:continue
        other=dstfiles[path]
        if ('offset'in meta)!=('offset'in other):raise ContractError('Entry storage type changed: '+path)
        if 'offset'not in meta:
            if meta!=other:raise ContractError('Non-target entry metadata changed: '+path)
            continue
        if meta.get('unpacked') or other.get('unpacked'):
            if meta!=other:raise ContractError('External unpacked entry metadata changed: '+path)
            unpacked+=1
            continue
        try:
            raw=b.read_entry(source_asar,source_size,meta)[1];out=b.read_entry(portable_asar,target_size,other)[1]
        except Exception as error:
            raise ContractError('Non-target source/readback failed: '+path+' '+str(error)) from error
        if raw!=out:raise ContractError('Non-target entry bytes changed: '+path)
        digest.update(path.encode()+b'\0'+hashlib.sha256(raw).digest());unchanged+=1
    require_routes(patched['entry_path'],patched['secondary_entry_path'],patched['shared_entry_path'])
    probe=_validate_renderer_probe(patched['entry_path'],portable_asar,b,p.PROFILE)
    return {'source_asar_sha256':p.PROFILE['asar_source_sha256'],'portable_asar_sha256':b.sha256_path(portable_asar),'transformations':transforms,'non_target_entries_verified':unchanged,'external_unpacked_metadata_verified':unpacked,'external_unpacked_file_bytes_scope':'separate_full_package_gate_required','non_target_inventory_sha256':digest.hexdigest(),'live_renderer_probe':probe},originals,patched

def validate(source_asar,portable_asar,node='node'):
    gate,src,out=validate_source(source_asar,portable_asar,node)
    from frontend_ssh_261007_9446 import execute_merge
    ssh=execute_merge(out['entry_path'],out['shared_entry_path'],[{'id':'11111111-1111-4111-8111-111111111111','hostId':'synthetic-ssh','label':'11111111-1111-4111-8111-111111111111','remotePath':'/srv/project-alpha'}],node)
    hashes={p.PROFILE[k]:b.sha256_bytes(v)for k,v in out.items()};source_hashes={p.PROFILE[k]:b.sha256_bytes(v)for k,v in src.items()}
    inspected,_=b.inspect_archive(Path(source_asar));contracts={}
    for name in b.frontend_feature_statuses(p.PROFILE):
        status=inspected['features'][name]['status']
        if status not in ('official_fixed','patchable'):raise ContractError('Source feature unsupported: '+name)
        nonrenderer=name in b.NON_RENDERER_ATTESTATION_FEATURES
        contracts[name]={'status':'source_checked_pending_runtime','source_identity':{'status':'passed','official_asar_sha256':gate['source_asar_sha256'],'entry_paths':list(hashes),'official_entry_sha256':source_hashes,'portable_entry_sha256':hashes},'semantic_execution':{'status':'pending_native_runtime','method':'fresh_packaged_native_execution_required'},'route_wiring':{'status':'passed','exact_transformations':True,'non_target_inventory_sha256':gate['non_target_inventory_sha256']},'runtime_attestation':{'status':'pending_native_runtime'if nonrenderer else'pending_live_renderer','attestation_version':VALIDATOR_VERSION,'protocol':'component_contract_v1'if nonrenderer else gate['live_renderer_probe']['protocol'],'scope':'main_process'if nonrenderer else'renderer','artifact_id':b.frontend_attestation_artifact_id(p.PROFILE),'content_logged':False}}
    result={'schema_version':2,'validator_version':VALIDATOR_VERSION,'status':'bundle_qualified_only','source_asar_sha256':gate['source_asar_sha256'],'portable_asar_sha256':gate['portable_asar_sha256'],'frontend_entry_path':p.PROFILE['entry_path'],'frontend_entry_sha256':hashes[p.PROFILE['entry_path']],'feature_contracts':contracts,'blocked_feature_ids':[],'actual_javascript':{'source_and_archive':gate,'actual_ssh_functions':ssh,'native_semantics':'pending_public_runtime_not_private_evidence'},'live_renderer_probe':gate['live_renderer_probe'],'content_logged':False}
    result['summary_sha256']=b.sha256_bytes(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result
