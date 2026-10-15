"""English defaults for a new independent public data directory."""
import json
from pathlib import Path


def initialize_new_data(directory):
    directory = Path(directory)
    if any(directory.iterdir()):
        return False
    state = directory / '.codex-global-state.json'
    # Exclusive creation preserves a concurrently created user preference.
    try:
        with state.open('x', encoding='utf8') as stream:
            json.dump({'electron-persisted-atom-state': {'electron-language': 'en'}}, stream)
    except FileExistsError:
        return False
    return True
