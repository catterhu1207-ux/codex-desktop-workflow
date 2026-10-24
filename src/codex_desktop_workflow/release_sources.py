"""Verify current framework inputs while retaining immutable release evidence."""
from pathlib import Path
import hashlib,json

CURRENT='qualification-26.1021.3705.0.json'

def digest(path):
    path=Path(path);raw=path.read_bytes()
    if path.suffix!='.bin':raw=raw.replace(b'\r\n',b'\n')
    return hashlib.sha256(raw).hexdigest()

def source_inventory(root=None):
    root=Path(root) if root is not None else Path(__file__).parent.parent
    files=[p for p in root.glob('*.py') if p.name.startswith(('hotfix_','frontend_','composer_selector_contract'))]
    files.extend(p for p in (root/'codex_desktop_workflow').rglob('*') if p.is_file()
        and p.suffix in ('.py','.js','.cjs','.mjs','.bin','.ps1','.json')
        and not p.name.startswith('qualification-') and '__pycache__' not in p.parts)
    return {p.relative_to(root).as_posix():digest(p) for p in sorted(files)}

def _check(root,inputs):
    if not inputs:raise ValueError('release_source_inventory_empty')
    mismatches=[]
    for name,expected in inputs.items():
        file=(root/name).resolve()
        if not file.is_relative_to(root.resolve()) or not file.is_file():raise ValueError('release_source_missing:'+name)
        if digest(file)!=expected:mismatches.append(name)
    return mismatches

def validate_current(policy_path,value,*,root=None,package_version=None):
    if package_version is None:
        from . import __version__
        package_version=__version__
    if (value.get('status')!='passed' or value.get('desktop_version')!='26.1021.3705.0'
            or value.get('package_version')!=package_version):raise ValueError('current_framework_qualification_incomplete')
    if value.get('source_inputs')!=source_inventory(root):raise ValueError('current_framework_source_changed')
    matrix=value.get('runtime_matrix',{})
    if set(matrix)!={'official','compat'}:raise ValueError('current_release_backend_matrix_incomplete')
    for mode,cases in matrix.items():
        if set(cases)!={'empty','synthetic_tasks'}:raise ValueError('current_release_profile_matrix_incomplete:'+mode)
        for case,proof in cases.items():
            if (proof.get('status')!='passed' or proof.get('observed_seconds',0)<60
                    or proof.get('normal_exit') is not True or proof.get('actual_backend_matched') is not True
                    or proof.get('renderer_features')!=23 or proof.get('browser_shared_state_unchanged') is not True):
                raise ValueError('current_release_runtime_incomplete:'+mode+'/'+case)
            if case=='synthetic_tasks' and proof.get('synthetic_tasks',0)<400:
                raise ValueError('current_release_synthetic_history_incomplete:'+mode)
        native=value.get('native_ui',{}).get(mode,{})
        if (native.get('status')!='passed' or native.get('first_send_cases')!=6
                or native.get('cold_reopened_chats')!=6 or native.get('history_original_bytes_preserved') is not True
                or native.get('priority_and_activity_ordering')!='passed'):
            raise ValueError('current_release_native_ui_incomplete:'+mode)
    if (value.get('frontend_contracts',{}).get('status')!='passed'
            or value['frontend_contracts'].get('count')!=26
            or value.get('background_history_budget',{}).get('status')!='passed'):
        raise ValueError('current_release_frontend_or_memory_guard_incomplete')
    return {'status':'passed','sha256':hashlib.sha256(Path(policy_path).read_bytes()).hexdigest()}

def validate(policy_path,value,*,root=None,current_path=None,package_version=None):
    """A changed framework requires explicit, independently qualified regression.

    Older policies stay byte-for-byte intact. Their version-specific frontend
    inputs must still match their original policy; the current complete source
    inventory covers shared operational changes.
    """
    policy_path=Path(policy_path)
    root=Path(root) if root is not None else Path(__file__).parent.parent
    mismatches=_check(root,value['source_inputs'])
    result={'status':'passed','sha256':hashlib.sha256(policy_path.read_bytes()).hexdigest()}
    if not mismatches:return result
    current_path=Path(current_path) if current_path is not None else policy_path.parent/CURRENT
    if current_path==policy_path or not current_path.is_file():raise ValueError('release_source_changed:'+mismatches[0])
    current=json.loads(current_path.read_text(encoding='utf8'))
    if package_version is None:
        from . import __version__
        package_version=__version__
    if (current.get('status')!='passed' or current.get('desktop_version')!='26.1021.3705.0'
            or current.get('package_version')!=package_version):raise ValueError('current_framework_qualification_incomplete')
    validate_current(current_path,current,root=root,package_version=package_version)
    actual=source_inventory(root)
    if current.get('source_inputs')!=actual:raise ValueError('current_framework_source_changed')
    prior=current.get('legacy_profile_regressions',{}).get(value['desktop_version'],{})
    immutable=prior.get('profile_source_inputs',{})
    if (prior.get('status')!='passed' or prior.get('historical_policy_sha256')!=result['sha256']
            or type(prior.get('tests')) is not int or prior['tests']<1 or not immutable):
        raise ValueError('legacy_profile_regression_missing:'+value['desktop_version'])
    if any(value['source_inputs'].get(name)!=expected for name,expected in immutable.items()):
        raise ValueError('legacy_profile_identity_rewritten')
    changed=_check(root,immutable)
    if changed:raise ValueError('legacy_profile_source_changed:'+changed[0])
    result['framework_qualification_sha256']=hashlib.sha256(current_path.read_bytes()).hexdigest()
    return result
