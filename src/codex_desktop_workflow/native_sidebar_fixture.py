"""Synthetic native settings and projects for the 4866 isolated release check."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import time
import uuid


def seed(home: Path) -> dict:
    home = home.resolve()
    if (home / '.codex-global-state.json').exists():
        raise ValueError('synthetic_settings_target_must_be_new')
    now = int(time.time() * 1000)
    projects = {}
    for index in range(2):
        identity = str(uuid.uuid4())
        root = home / 'synthetic-workspaces' / str(index)
        root.mkdir(parents=True, exist_ok=True)
        projects[identity] = {'id': identity, 'name': f'Local fixture {index + 1}',
                              'rootPaths': [str(root)], 'createdAt': now - index * 1000,
                              'updatedAt': now - index * 1000}
    remote = [{'id': str(uuid.uuid4()), 'hostId': 'synthetic-ssh-host',
               'label': f'Remote fixture {index + 1}',
               'remotePath': f'/workspace/synthetic-project-{index + 1}'} for index in range(2)]
    state = {
        'electron-persisted-atom-state': {'flat-project-sidebar-preferences-v1': {
            'chatSortMode': 'updated_at', 'initialized': True, 'mode': 'project',
            'projectSortMode': 'updated_at', 'manualSortVersion': 1}},
        'remote-projects': remote, 'local-projects': projects,
        'electron-saved-workspace-roots': [p for value in projects.values() for p in value['rootPaths']],
        'electron-workspace-roots': [str(home / 'synthetic-workspaces' / str(i)) for i in range(12)],
        'codex-managed-remote-connections': [{'hostId': 'synthetic-ssh-host',
            'displayName': 'Synthetic SSH host', 'source': 'ssh-config',
            'alias': 'synthetic-unconfigured-host', 'hostname': None, 'sshPort': None,
            'identity': None, 'connectionAnalyticsId': str(uuid.uuid4())}],
        'remote-connection-auto-connect-by-host-id': {'synthetic-ssh-host': False},
        'pinned-project-ids': [next(iter(projects)), remote[0]['id']],
        'project-order': ['codex:project:' + key for key in [*projects, *[p['id'] for p in remote]]],
    }
    (home / '.codex-global-state.json').write_text(json.dumps(state, indent=2), encoding='utf8')
    return {'synthetic_only': True, 'local_projects': 2, 'remote_projects': 2,
            'pinned_projects': 2, 'credentials_copied': False}


def blocked_ssh_binding(home: Path) -> Path:
    """A copied Node executable rejects SSH arguments without contacting a host.

    It is created locally from the installed runtime, never distributed as an
    asset. This fixture tests native project restoration, not SSH networking.
    """
    node = shutil.which('node')
    if not node:
        raise ValueError('node_required_for_native_sidebar_acceptance')
    target = home / 'isolated-test-bin'
    target.mkdir(exist_ok=False)
    original = Path(node).resolve()
    copied = target / 'ssh.exe'
    shutil.copy2(original, copied)
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if digest(copied) != digest(original):
        raise ValueError('isolated_ssh_binding_copy_mismatch')
    (target / 'binding.json').write_text(json.dumps({
        'kind': 'rejecting_local_service_binding', 'node_sha256': digest(original),
        'real_ssh_network_tested': False,
    }, indent=2), encoding='utf8')
    return target
