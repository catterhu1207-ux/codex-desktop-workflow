"""Validated, data-only channel definitions shared by the menu and switcher."""
from __future__ import annotations

import json
import re
from pathlib import Path

FIELDS = {'id', 'label', 'provider', 'model', 'effort', 'catalog', 'env_key', 'route_type'}
ROUTES = {'subscription', 'direct', 'proxy'}


def load_profiles(path: Path | None = None) -> tuple[dict[str, dict], bytes]:
    path = path or Path(__file__).with_name('profiles.json')
    raw = path.read_bytes()
    data = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(data, dict) or data.get('schema_version') != 1 or not isinstance(data.get('profiles'), list):
        raise ValueError('Unsupported channel profile schema')
    profiles = {}
    providers = set()
    for item in data['profiles']:
        if not isinstance(item, dict) or set(item) != FIELDS:
            raise ValueError('Channel profile fields are invalid')
        for field in ('id', 'label', 'provider', 'model', 'effort'):
            if not isinstance(item[field], str) or not item[field].strip():
                raise ValueError(f'Channel profile {field} is invalid')
        if not re.fullmatch(r'[a-z][a-z0-9_-]*', item['id']):
            raise ValueError('Channel profile id is invalid')
        if item['id'] in profiles or item['provider'] in providers:
            raise ValueError('Duplicate channel id or provider')
        if item['route_type'] not in ROUTES:
            raise ValueError('Unsupported channel route type')
        catalog = item['catalog']
        if catalog is not None and (not isinstance(catalog, str) or Path(catalog).name != catalog or not catalog.endswith('.json')):
            raise ValueError('Channel catalog must be a JSON filename')
        env_key = item['env_key']
        if env_key is not None and (not isinstance(env_key, str) or not re.fullmatch(r'[A-Z][A-Z0-9_]*', env_key)):
            raise ValueError('Channel credential variable name is invalid')
        if item['route_type'] == 'subscription' and (catalog is not None or env_key is not None or item['provider'] != 'openai'):
            raise ValueError('Subscription profile is invalid')
        if item['route_type'] != 'subscription' and catalog is None:
            raise ValueError('API channel must declare a model catalog')
        profiles[item['id']] = item
        providers.add(item['provider'])
    if not profiles or 'openai' not in profiles:
        raise ValueError('OpenAI subscription profile is required')
    return profiles, raw


def credential_available(name: str | None) -> bool | None:
    if name is None:
        return None
    import os
    if os.name == 'nt':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
                value, _ = winreg.QueryValueEx(key, name)
                if isinstance(value, str) and value.strip():
                    return True
        except OSError:
            pass
    return bool(os.environ.get(name, '').strip())
