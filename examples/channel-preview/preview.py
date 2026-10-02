"""Read-only channel preview; this example never switches a route or edits history."""
from __future__ import annotations

import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import tomllib

from profiles import credential_available, load_profiles

BINDING_FIELDS = {'model', 'model_reasoning_effort', 'model_provider',
                  'preferred_auth_method', 'forced_login_method',
                  'model_catalog_json', 'service_tier', 'base_url'}


def normalized_path(value: str | Path) -> Path:
    text = str(value)
    if text.startswith('\\\\?\\UNC\\'):
        text = '\\\\' + text[8:]
    elif text.startswith('\\\\?\\'):
        text = text[4:]
    return Path(os.path.realpath(os.path.abspath(text)))


def is_within(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath((str(path), str(root))).casefold() == str(root).casefold()
    except ValueError:
        return False


def validate_target(home: Path, profile: dict, config: dict) -> None:
    if profile['route_type'] == 'subscription':
        filename = 'models_cache.json'
    else:
        section = config.get('model_providers', {}).get(profile['provider'])
        if not isinstance(section, dict) or not section.get('base_url') or section.get('wire_api') != 'responses':
            raise ValueError('Responses provider configuration is incomplete')
        if profile['env_key'] and section.get('env_key') != profile['env_key']:
            raise ValueError('Provider credential variable does not match the profile')
        filename = profile['catalog']
    data = json.loads((home / filename).read_text(encoding='utf-8-sig'))
    models = data.get('models', [])
    if not isinstance(models, list) or any(
        not isinstance(item, dict) or 'experimental_supported_tools' not in item
        or ('base_instructions' not in item and not (item.get('model_messages') or {}).get('instructions_template'))
        for item in models
    ):
        raise ValueError('Model catalog lacks fields required by the supported desktop backend')
    matches = [m for m in models if m.get('slug') == profile['model']]
    if len(matches) != 1 or profile['effort'] not in [r['effort'] for r in matches[0].get('supported_reasoning_levels', [])]:
        raise ValueError('Default model or reasoning effort is absent from the catalog')


def inventory(home: Path, provider: str) -> dict:
    state = home / 'state_5.sqlite'
    with closing(sqlite3.connect(f'file:{state.as_posix()}?mode=ro', uri=True)) as connection:
        if connection.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise ValueError('Thread index integrity check failed')
        columns = {row[1] for row in connection.execute('PRAGMA table_info(threads)')}
        if not {'rollout_path', 'archived', 'model_provider'}.issubset(columns):
            raise ValueError('Thread index schema is unsupported')
        rows = connection.execute('SELECT rollout_path, model_provider FROM threads WHERE archived = 0').fetchall()
    roots = (normalized_path(home / 'sessions'), normalized_path(home / 'archived_sessions'))
    managed = [(path, current) for path, current in rows
               if any(is_within(normalized_path(path), root) for root in roots)]
    return {'managed_unarchived': len(managed),
            'estimated_to_migrate': sum(current != provider for _, current in managed),
            'already_on_target_provider': sum(current == provider for _, current in managed),
            'external_unarchived': len(rows) - len(managed)}


def preview(home: Path, target: str) -> dict:
    profiles, _ = load_profiles()
    if target not in profiles:
        raise ValueError('Unknown channel')
    profile = profiles[target]
    config = tomllib.loads((home / 'config.toml').read_text(encoding='utf-8-sig'))
    validate_target(home, profile, config)
    desired = {'model': profile['model'], 'model_reasoning_effort': profile['effort']}
    if profile['route_type'] == 'subscription':
        desired['service_tier'] = 'default'
    else:
        desired.update(model_provider=profile['provider'], preferred_auth_method='apikey',
                       model_catalog_json=(home / profile['catalog']).as_posix())
        if profile['route_type'] != 'proxy':
            desired['forced_login_method'] = 'api'
    changed = sorted(name for name in BINDING_FIELDS if config.get(name) != desired.get(name))
    current_provider = config.get('model_provider') or 'openai'
    current_channel = next((name for name, entry in profiles.items() if entry['provider'] == current_provider), None)
    credential = credential_available(profile['env_key'])
    return {'schema_version': 1, 'status': 'ready' if credential is not False else 'missing_credential',
            'current': {'channel': current_channel, 'provider': current_provider,
                        'model': config.get('model'), 'effort': config.get('model_reasoning_effort')},
            'target': {'channel': target, 'provider': profile['provider'],
                       'model': profile['model'], 'effort': profile['effort']},
            'changed_keys': changed, 'already_configured': not changed,
            'credential': {'env_key': profile['env_key'], 'present': credential},
            'inheritance_estimate': inventory(home, profile['provider']),
            'note': 'Estimate only; a qualified safe-start implementation must determine the final migration set.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', required=True)
    parser.add_argument('--home', type=Path, default=Path.home() / '.codex')
    args = parser.parse_args()
    try:
        print(json.dumps(preview(args.home, args.target), ensure_ascii=False))
    except Exception as error:
        print(json.dumps({'status': 'failed', 'message': str(error)}, ensure_ascii=False))
        raise SystemExit(1)
