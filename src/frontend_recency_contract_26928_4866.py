"""Execute the packaged start reducer, time selectors and project consumer."""
from pathlib import Path

def run(initial: bytes, shared: bytes, node='node'):
    from frontend_contract_26928_4866 import functions_from, execute
    functions = functions_from(initial, ('g0n', 'Qpn', 'Xpn', 'tmn', 'nmn', 'HA', 'spn', 'apn', 'opn', 'dpn'), 'initial', node)
    functions.update(functions_from(shared, ('l7t',), 'shared', node))
    return execute(functions, (Path(__file__).parent / 'codex_desktop_workflow/data/frontend_recency_contract_26928_4866.js').read_text(encoding='utf8'), node)
