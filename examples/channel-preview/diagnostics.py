"""Read-only local checks and explicitly requested minimal Responses probes."""
from __future__ import annotations

import argparse
import base64
import json
import os
import struct
import sys
import time
import tomllib
import urllib.error
import urllib.request
import zlib
from pathlib import Path

from profiles import credential_available, load_profiles
from preview import validate_target

def test_image() -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))
    row = b'\x00' + b'\xff\xff\xff' * 64
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 64, 64, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(row * 64)) + chunk(b'IEND', b''))


TEST_PNG = test_image()


def credential(name: str | None) -> str | None:
    if name is None:
        return None
    if os.name == 'nt':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
                value, _ = winreg.QueryValueEx(key, name)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        except OSError:
            pass
    return os.environ.get(name) or None


def classify_http(code: int) -> str:
    if code in (401, 403):
        return 'authentication'
    if code == 429:
        return 'quota_or_rate_limit'
    if code in (400, 404, 422):
        return 'model_or_protocol'
    return 'service'


def probe(base_url: str, key: str, model: str, kind: str) -> dict:
    body: dict = {'model': model, 'stream': True, 'max_output_tokens': 512 if kind == 'image' else 192}
    if kind == 'text':
        body['input'] = 'Reply with OK.'
    elif kind == 'tool':
        body['input'] = 'Call the ping function with value OK.'
        body['tools'] = [{'type': 'function', 'name': 'ping',
                          'description': 'Return a minimal test value.',
                          'parameters': {'type': 'object', 'properties': {'value': {'type': 'string'}},
                                         'required': ['value'], 'additionalProperties': False}}]
    else:
        body['input'] = [{'role': 'user', 'content': [
            {'type': 'input_text', 'text': 'Is this a white image? Reply yes or no.'},
            {'type': 'input_image', 'image_url': 'data:image/png;base64,' + base64.b64encode(TEST_PNG).decode('ascii')}
        ]}]
    request = urllib.request.Request(
        base_url.rstrip('/') + '/responses',
        data=json.dumps(body, separators=(',', ':')).encode('utf-8'),
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json',
                 'Accept': 'text/event-stream'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            if response.headers.get('Content-Type', '').split(';')[0].strip() != 'text/event-stream':
                return {'status': 'failed', 'category': 'protocol'}
            lines = []
            size = 0
            for line in response:
                size += len(line)
                if size > 2_000_000:
                    return {'status': 'failed', 'category': 'protocol'}
                if line.startswith(b'data:'):
                    lines.append(line[5:].strip())
            events = []
            for line in lines:
                if line == b'[DONE]':
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    return {'status': 'failed', 'category': 'protocol'}
            completed = [event.get('response') for event in events if event.get('type') == 'response.completed']
            if len(completed) != 1 or not isinstance(completed[0], dict):
                return {'status': 'failed', 'category': 'protocol'}
            output = completed[0].get('output', [])
            if kind == 'tool':
                valid = any(item.get('type') == 'function_call' and item.get('name') == 'ping' for item in output if isinstance(item, dict))
            else:
                valid = any(part.get('type') == 'output_text' and part.get('text')
                            for item in output if isinstance(item, dict)
                            for part in item.get('content', []) if isinstance(part, dict))
            return {'status': 'passed' if valid else 'failed',
                    'category': None if valid else 'protocol'}
    except urllib.error.HTTPError as error:
        return {'status': 'failed', 'category': classify_http(error.code), 'http_status': error.code}
    except (urllib.error.URLError, TimeoutError, OSError):
        return {'status': 'failed', 'category': 'network'}


def diagnose(home: Path, target: str, online: bool = False) -> dict:
    started = time.monotonic()
    profiles, _ = load_profiles()
    if target not in profiles:
        raise ValueError('Unknown channel')
    profile = profiles[target]
    config = tomllib.loads((home / 'config.toml').read_text(encoding='utf-8-sig'))
    validate_target(home, profile, config)
    key_state = credential_available(profile['env_key'])
    result = {'schema_version': 1, 'channel': target, 'model': profile['model'],
              'local': {'status': 'passed' if key_state is not False else 'missing_credential',
                        'credential': 'present' if key_state is True else 'missing' if key_state is False else 'provider_managed'}}
    if not online:
        result['online'] = {'status': 'not_requested'}
        result['elapsed_ms'] = round((time.monotonic() - started) * 1000)
        return result
    key = credential(profile['env_key'])
    if profile['route_type'] == 'subscription' or key is None:
        result['online'] = {'status': 'unavailable', 'category': 'credential_or_route'}
        result['elapsed_ms'] = round((time.monotonic() - started) * 1000)
        return result
    section = config['model_providers'][profile['provider']]
    base_url = section['base_url']
    catalog = json.loads((home / profile['catalog']).read_text(encoding='utf-8-sig'))
    model = next(item for item in catalog['models'] if item['slug'] == profile['model'])
    checks = {}
    for kind in ('text', 'tool'):
        checks[kind] = probe(base_url, key, profile['model'], kind)
        if checks[kind]['status'] != 'passed':
            break
    if all(value['status'] == 'passed' for value in checks.values()) and 'image' in model.get('input_modalities', []):
        checks['image'] = probe(base_url, key, profile['model'], 'image')
    result['online'] = {'status': 'passed' if checks and all(v['status'] == 'passed' for v in checks.values()) else 'failed',
                        'checks': checks}
    result['elapsed_ms'] = round((time.monotonic() - started) * 1000)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', required=True)
    parser.add_argument('--home', type=Path, default=Path.home() / '.codex')
    parser.add_argument('--online', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(diagnose(args.home, args.target, args.online), ensure_ascii=False))
    except Exception as error:
        print(json.dumps({'status': 'failed', 'category': 'local_validation', 'message': str(error)}, ensure_ascii=False))
        raise SystemExit(1)
