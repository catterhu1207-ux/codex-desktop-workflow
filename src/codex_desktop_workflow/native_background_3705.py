"""Execute the packaged main-process background budget and both native callers."""
from pathlib import Path
import hashlib,json,subprocess
import hotfix_builder as b
import hotfix_integration_261021_3705 as p
from .native_checks_4894 import extract

def verify(portable):
    portable=Path(portable);archive=portable/'resources/app.asar'
    if b.sha256_path(archive)!=p.TARGET_ASAR_SHA256:raise ValueError('3705_background_archive_identity_differs')
    guard=portable/'resources/g.cjs'
    if guard.is_symlink() or b.sha256_path(guard)!=p.BACKGROUND_GUARD_SHA256:raise ValueError('3705_background_resource_differs')
    size,_,header=b.read_asar(archive)
    def read(name):return b.read_entry(archive,size,b.get_entry_meta(header,name))[1].decode()
    functions={'composer':extract(read(p.PROFILE['main_entry_path']),['FRe'],True)['FRe'],
        'generation':extract(read(p.PROFILE['background_generation_entry_path']),['uw'],True)['uw']}
    connection=read(p.PROFILE['background_generation_entry_path'])
    start='async readThread(e,t,n,r){'
    end='async listThreadTurns('
    if connection.count(start)!=1:raise ValueError('3705_native_metadata_reader_ambiguous')
    reader=connection[connection.index(start):connection.index(end,connection.index(start))]
    getter='get hostConfig(){return this.options.hostConfig}'
    if connection.count(getter)!=1 or 'includeTurns:t?.includeTurns??!1' not in reader:
        raise ValueError('3705_native_metadata_interface_changed')
    functions.update(native_read_thread=reader,native_host_getter=getter)
    script=Path(__file__).parent/'data/native_background_3705.cjs'
    result=subprocess.run(['node',str(script)],input=json.dumps({**functions,'guard':guard.read_text(encoding='utf8')}),
        capture_output=True,text=True,encoding='utf8',timeout=45,creationflags=0x08000000)
    if result.returncode:raise RuntimeError(result.stderr[-1500:])
    value=json.loads(result.stdout)
    if value.get('status')!='passed':raise ValueError('3705_background_budget_execution_failed')
    value['candidate_sha256']=p.TARGET_ASAR_SHA256
    value['guard_sha256']=p.BACKGROUND_GUARD_SHA256
    value['function_sha256']={key:hashlib.sha256(raw.encode()).hexdigest() for key,raw in functions.items()}
    return value
