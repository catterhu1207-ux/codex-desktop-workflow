"""Execute the packaged start reducer, time selectors and project consumer."""
from pathlib import Path

def run(initial: bytes, shared: bytes, node='node'):
    from frontend_contract_26928_2636 import functions_from, execute
    functions = functions_from(initial, ('v0n', 'smn', 'amn', 'umn', 'dmn', 'BA', 'bpn', 'vpn', 'ypn', 'wpn'))
    functions.update(functions_from(shared, ('l7t',)))
    return execute(functions, (Path(__file__).resolve().parent/'codex_desktop_workflow/data'/(Path(__file__).resolve().parent/'codex_desktop_workflow/data'/(Path(__file__).resolve().parent/'codex_desktop_workflow/data'/(Path(__file__).resolve().parent/'codex_desktop_workflow/data'/Path(__file__).with_suffix('.js').name).name).name).name).read_text(encoding='utf8'), node)
