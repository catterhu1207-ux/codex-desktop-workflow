"""Transfer only an ended disposable run's public dependency cache."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat

from .browser_isolation import _children, _digest, _io_path, _plain, _write


def _inventory(root):
    # FindFirstFile metadata avoids reopening tens of thousands of public
    # dependency files. An atomic same-volume directory rename keeps the root
    # identity and all children; file size/timestamps detect concurrent writes.
    rows=[];pending=[Path(root)]
    while pending:
        directory=pending.pop()
        with os.scandir(_io_path(directory)) as items:
            entries=sorted(items,key=lambda entry:entry.name)
        for entry in entries:
            info=entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
                raise ValueError('runtime_cache_redirected_entry')
            file=directory/entry.name
            if stat.S_ISDIR(info.st_mode):pending.append(file)
            elif stat.S_ISREG(info.st_mode):
                rows.append({'path':file.relative_to(root).as_posix(),'bytes':info.st_size,
                    'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns,
                    'attributes':getattr(info,'st_file_attributes',0)})
            else:raise ValueError('runtime_cache_unsupported_entry')
    rows.sort(key=lambda row:row['path'])
    encoded=json.dumps(rows,sort_keys=True,separators=(',',':')).encode()
    return rows,hashlib.sha256(encoded).hexdigest()


def transfer(source_run, destination_run, source_state):
    """Same-volume move, preserving every byte; never transfer user state.

    Only dependencies/plugins/runtime.json below a previously owned, exited
    run are eligible. Chat data, authentication, Electron data and plugin
    installation state remain in their separate original directories.
    """
    source_run,destination_run=Path(source_run),Path(destination_run)
    for run in (source_run,destination_run):
        if not run.is_absolute() or not re.fullmatch(r'run-[0-9a-f]{32}',run.name):
            raise ValueError('runtime_cache_requires_owned_run_directory')
        for parent in (run,*run.parents):_plain(parent)
    if source_run==destination_run or source_run.parent!=destination_run.parent:
        raise ValueError('runtime_cache_requires_same_owned_runs_root')
    receipt_path=destination_run/'runtime-cache-transfer.json'
    if _io_path(receipt_path).exists():raise ValueError('runtime_cache_transfer_requires_reconciliation')
    record=json.loads(_io_path(source_run/'run.json').read_bytes())
    if (record.get('shell_folders')!='owl_fresh_profile_browser_integration_isolated'
            or source_state.get('status')!='exited' or source_state.get('main')!=record.get('main')
            or source_state.get('alive_backends')):
        raise ValueError('runtime_cache_source_owner_not_exited')
    source=source_run/'profile/.cache/codex-runtimes/codex-primary-runtime'
    profile=destination_run/'profile'
    for parent in (source,*source.parents):_plain(parent)
    _plain(profile)
    if set(file.name for file in _children(source))!={'dependencies','plugins','runtime.json'}:
        raise ValueError('runtime_cache_inventory_not_public_dependencies')
    runtime=json.loads(_io_path(source/'runtime.json').read_bytes())
    if (runtime.get('targetPlatform')!='win32' or runtime.get('targetArch')!='x64'
            or not re.fullmatch(r'\d+(?:\.\d+){2}',str(runtime.get('bundleVersion','')))):
        raise ValueError('runtime_cache_manifest_identity_missing')
    for name in ('dependencies/node/bin/node.exe','dependencies/python/python.exe'):_digest(source/name)
    if _plain(source).st_dev!=_plain(profile).st_dev:
        raise ValueError('runtime_cache_transfer_requires_same_volume')
    destination=profile/'.cache/codex-runtimes/codex-primary-runtime'
    if _io_path(profile/'.cache').exists():
        raise ValueError('runtime_cache_destination_profile_not_fresh')
    source_info=_plain(source)
    source_identity=(source_info.st_dev,source_info.st_ino)
    manifest_sha256=_digest(source/'runtime.json')
    rows,before=_inventory(source)
    receipt={'schema_version':1,'status':'intent','source_run':str(source_run),
        'source':str(source),'destination':str(destination),'bundle_version':runtime['bundleVersion'],
        'inventory_sha256':before,'files':len(rows),'bytes':sum(r['bytes'] for r in rows),
        'inventory_kind':'same_volume_root_identity_and_file_metadata',
        'runtime_manifest_sha256':manifest_sha256,'source_directory_identity':source_identity,
        'user_data_moved':False,'same_volume':True,'source_owner':record['main']}
    _write(receipt_path,receipt)
    _io_path(destination.parent).mkdir(parents=True)
    os.rename(_io_path(source),_io_path(destination))
    after_rows,after=_inventory(destination)
    destination_info=_plain(destination)
    if (_io_path(source).exists() or before!=after or rows!=after_rows
            or (destination_info.st_dev,destination_info.st_ino)!=source_identity
            or _digest(destination/'runtime.json')!=manifest_sha256):
        raise RuntimeError('runtime_cache_transfer_readback_differs')
    receipt['status']='moved_with_native_identity_readback'
    _write(receipt_path,receipt)
    return receipt


def restore_unlaunched(destination_run, source_state):
    """Reconcile a completed move whose new application was never launched."""
    destination_run=Path(destination_run)
    if not destination_run.is_absolute():raise ValueError('runtime_cache_restore_requires_absolute_path')
    for parent in (destination_run,*destination_run.parents):_plain(parent)
    receipt_path=destination_run/'runtime-cache-transfer.json'
    _plain(receipt_path)
    receipt=json.loads(_io_path(receipt_path).read_bytes())
    source_run=Path(receipt['source_run'])
    if not source_run.is_absolute():raise ValueError('runtime_cache_restore_requires_absolute_path')
    for parent in (source_run,*source_run.parents):_plain(parent)
    if (receipt.get('status')!='moved_with_native_identity_readback'
            or source_run.parent!=destination_run.parent
            or not all(re.fullmatch(r'run-[0-9a-f]{32}',p.name) for p in (source_run,destination_run))
            or _io_path(destination_run/'run.json').exists()
            or _io_path(destination_run/'stdout.log').exists()
            or _io_path(destination_run/'browser-shared-state.json').exists()):
        raise ValueError('runtime_cache_restore_requires_proved_unlaunched_destination')
    owner=json.loads(_io_path(source_run/'run.json').read_bytes())
    if (source_state.get('status')!='exited' or source_state.get('main')!=owner.get('main')
            or source_state.get('alive_backends') or owner.get('main')!=receipt.get('source_owner')):
        raise ValueError('runtime_cache_restore_source_owner_not_exited')
    source=source_run/'profile/.cache/codex-runtimes/codex-primary-runtime'
    destination=destination_run/'profile/.cache/codex-runtimes/codex-primary-runtime'
    if str(source)!=receipt['source'] or str(destination)!=receipt['destination'] or _io_path(source).exists():
        raise ValueError('runtime_cache_restore_path_or_state_differs')
    for parent in (destination,*destination.parents):_plain(parent)
    identity=_plain(destination)
    rows,digest=_inventory(destination)
    if (list((identity.st_dev,identity.st_ino))!=receipt['source_directory_identity']
            or digest!=receipt['inventory_sha256']
            or _digest(destination/'runtime.json')!=receipt['runtime_manifest_sha256']):
        raise ValueError('runtime_cache_restore_inventory_changed')
    receipt['status']='restore_intent';_write(receipt_path,receipt)
    os.rename(_io_path(destination),_io_path(source))
    actual=_plain(source)
    if (_io_path(destination).exists() or _inventory(source)!=(rows,digest)
            or (actual.st_dev,actual.st_ino)!=(identity.st_dev,identity.st_ino)):
        raise RuntimeError('runtime_cache_restore_readback_differs')
    receipt['status']='restored_original_run_after_unlaunched_preparation_failure'
    _write(receipt_path,receipt)
    return receipt


def copy_ended_ssh_config(source_run,destination_run,source_state):
    """Seed only a prior owned fixture's SSH config before remote restoration."""
    source_run,destination_run=Path(source_run),Path(destination_run)
    if (source_run==destination_run or source_run.parent!=destination_run.parent
            or not all(p.is_absolute() and re.fullmatch(r'run-[0-9a-f]{32}',p.name) for p in (source_run,destination_run))):
        raise ValueError('ssh_fixture_requires_same_owned_runs_root')
    for run in (source_run,destination_run):
        for parent in (run,*run.parents):_plain(parent)
    record=json.loads(_io_path(source_run/'run.json').read_bytes())
    if (record.get('shell_folders')!='owl_fresh_profile_browser_integration_isolated'
            or source_state.get('status')!='exited' or source_state.get('main')!=record.get('main') or source_state.get('alive_backends')):
        raise ValueError('ssh_fixture_source_owner_not_exited')
    source=source_run/'profile/.ssh/config';profile=destination_run/'profile';destination=profile/'.ssh/config'
    for parent in (source,*source.parents):_plain(parent)
    _plain(profile)
    before=_plain(source)
    if not stat.S_ISREG(before.st_mode) or before.st_size>65536 or _io_path(profile/'.ssh').exists():
        raise ValueError('ssh_fixture_configuration_or_destination_unexpected')
    raw=_io_path(source).read_bytes();after=_plain(source)
    if (before.st_ino,before.st_mtime_ns,before.st_size)!=(after.st_ino,after.st_mtime_ns,after.st_size):
        raise ValueError('ssh_fixture_source_changed')
    _io_path(destination.parent).mkdir()
    with _io_path(destination).open('xb') as output:output.write(raw)
    digest=hashlib.sha256(raw).hexdigest()
    if _digest(destination)!=digest:raise RuntimeError('ssh_fixture_copy_readback_differs')
    receipt={'status':'copied_owned_ssh_configuration','source_run':str(source_run),'source_sha256':digest,
             'destination':str(destination),'private_keys_copied':False,'authentication_copied':False,'source_owner_exited':True}
    _write(destination_run/'ssh-fixture-config.json',receipt)
    return receipt
