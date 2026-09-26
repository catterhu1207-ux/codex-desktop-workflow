"""Pinned, optional source-built compatibility backend support."""
from pathlib import Path
import hashlib,json,subprocess,sys,os,shutil

PIN_PATH=Path(__file__).parent/'policies/backend-source.json'

def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def pin():
    return json.loads(PIN_PATH.read_text())

def validate_manifest(path):
    data=json.loads(path.read_text());p=pin();provenance=data.get('provenance',{})
    required={'source_commit':p['upstream_commit'],'profile_sha256':p['profile_sha256'],'compat_commit':p['commit'],'compat_repository':p['repository'],'build_recipe_sha256':p['build_recipe_sha256']}
    if data.get('mode')!='patched' or any(provenance.get(k)!=v for k,v in required.items()):
        raise ValueError('compat_backend_provenance_mismatch')
    if provenance.get('patch_files')!=p['patch_files'] or provenance.get('external_dependencies_unchanged') is not True:
        raise ValueError('compat_backend_dependency_proof_mismatch')
    if data.get('official',{}).get('sha256')!=p['official_backend_sha256']:
        raise ValueError('compat_backend_official_identity_mismatch')
    binary=(path.parent/data['patched']['file']).resolve()
    if not binary.is_relative_to(path.parent.resolve()) or sha(binary)!=data['patched']['sha256']:
        raise ValueError('compat_backend_binary_identity_mismatch')
    raw=binary.read_bytes()
    if provenance.get('migration_sha384')!=p['migration_sha384'] or any(bytes.fromhex(v) not in raw for v in p['migration_sha384'].values()):
        raise ValueError('compat_backend_migration_identity_mismatch')
    return data

def build(source_app,target):
    p=pin();target=target.resolve()
    if sys.version_info < (3,11):raise ValueError('python_3_11_required_for_source_build')
    if target.exists():raise ValueError('backend_target_must_not_exist')
    target.mkdir(parents=True)
    repository=target/'repository'
    subprocess.run(['git','clone','--no-checkout',p['repository'],str(repository)],check=True)
    subprocess.run(['git','-C',str(repository),'checkout','--detach',p['commit']],check=True)
    recipe=repository/'build_backend.py'
    if sha(recipe)!=p['build_recipe_sha256']:
        raise ValueError('compat_build_recipe_identity_mismatch')
    destination=target/'backend'
    cache=os.environ.get('CODEX_COMPAT_BUILD_CACHE')
    build_target=Path(cache).resolve() if cache else destination
    command=[sys.executable,str(recipe),'--profile',p['profile'],'--target',str(build_target),'--official-backend',str(source_app/'resources/codex.exe')]
    if cache:command.append('--reuse-verified-source')
    result=subprocess.run(command,capture_output=True,text=True,encoding='utf8',errors='replace')
    log=target/'backend-build.log'
    log.write_text(result.stdout+'\n'+result.stderr,encoding='utf8')
    if result.returncode:raise ValueError('compat_source_build_failed: '+str(log))
    if cache:
        validate_manifest(build_target/'manifest.json')
        destination.mkdir()
        shutil.copy2(build_target/'codex.exe',destination/'codex.exe')
        shutil.copy2(build_target/'manifest.json',destination/'manifest.json')
    manifest=destination/'manifest.json'
    validate_manifest(manifest)
    return {'status':'built','manifest':str(manifest),'content_logged':False}
