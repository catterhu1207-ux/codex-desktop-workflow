"""Execute the complete packaged row with retained memo and synthetic state."""
import json, subprocess
from frontend_feature_contracts import _extract_function, _with_module_stubs, ContractError

def run(initial, node='node'):
    funcs = {n: _extract_function(initial.decode(), n) for n in ('Hmt', 'Umt', 'up', 'lp', 'CVs', 'nRs', 'OCs', 'L4', 'zbs', 'Bbs', 'qZp')}
    script = '\n'.join(funcs.values()) + SCENARIOS
    cp = subprocess.run([node, '-'], input=_with_module_stubs(script, funcs), text=True, capture_output=True, encoding='utf8', timeout=30)
    if cp.returncode:
        raise ContractError('Actual mounted row: ' + cp.stderr[-2000:])
    return json.loads(cp.stdout)
from pathlib import Path
SCENARIOS = (Path(__file__).resolve().parent/'codex_desktop_workflow/data'/'frontend_row_scenarios_26917_8451.js').read_text(encoding='utf8')
