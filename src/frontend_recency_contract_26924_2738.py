"""Execute the packaged start reducer, time selectors and project consumer."""
from pathlib import Path


def run(initial: bytes, shared: bytes, node='node'):
    from frontend_contract_26924_2738 import functions_from, execute
    functions=functions_from(initial, ('GA','W3t','U3t','q3t','J3t','aM','r3t','t3t','n3t','s3t'))
    functions.update(functions_from(shared, ('QZt',)))
    return execute(functions, Path(__file__).parent.joinpath('codex_desktop_workflow/data', 'frontend_recency_contract_26924_2738.js').read_text(encoding='utf8'),node)
