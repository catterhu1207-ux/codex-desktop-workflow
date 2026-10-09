"""Execute the packaged start reducer, time selectors and project consumer."""
from pathlib import Path

def run(initial: bytes, shared: bytes, node='node'):
    from frontend_contract_26924_6891 import functions_from, execute
    functions = functions_from(initial, ('$A', 'K3t', 'G3t', 'Y3t', 'X3t', 'SM', 'a3t', 'r3t', 'i3t', 'l3t'))
    functions.update(functions_from(shared, ('CQt',)))
    return execute(functions, (Path(__file__).resolve().parent/'codex_desktop_workflow/data'/(Path(__file__).resolve().parent/'codex_desktop_workflow/data'/(Path(__file__).resolve().parent/'codex_desktop_workflow/data'/(Path(__file__).resolve().parent/'codex_desktop_workflow/data'/Path(__file__).with_suffix('.js').name).name).name).name).read_text(encoding='utf8'), node)
