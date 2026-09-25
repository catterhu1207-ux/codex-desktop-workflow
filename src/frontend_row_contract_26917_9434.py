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
def _scenario_source() -> str:
    local = Path(__file__).with_name('frontend_row_scenarios_26917_9434.js')
    if local.is_file():
        return local.read_text(encoding='utf-8')
    from importlib import resources
    return resources.files('codex_desktop_workflow').joinpath(
        'data', 'frontend_row_scenarios_26917_9434.js'
    ).read_text(encoding='utf-8')


SCENARIOS = _scenario_source()
