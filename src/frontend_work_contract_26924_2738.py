"""Exercise both SSH data chains through the real new Work picker and callback."""
from pathlib import Path
from frontend_contract_26924_2738 import execute, functions_from
PICKER_PATH = 'webview/assets/composer-project-picker-content-99d6c0f04204.js'
PICKER_SHA256 = 'b9466380b7c6e96165c7da0f5b2d04c6c72adb6a8f0259c739db255973811a1c'

def run(initial, primary, picker, shared, node='node'):
    functions = functions_from(initial, ('S9t', 'qZx', 's9t', 'G7t', 'x9t', 'DNr', 'J9t', 'xI', 'bI', 'J7t'))
    # The two real chunks reuse S9t for different functions; alias only the extracted declaration.
    functions['rawRemoteSelection'] = functions.pop('S9t').replace('function S9t(', 'function rawRemoteSelection(', 1)
    functions.update(functions_from(primary, ('b9', 'M8t', 'P8t', 'fZt', '$Y', 'S9t', 'W5t', 'y6t', 'd8t')))
    functions.update(functions_from(shared, ('ij', 'rj', 'Yst')))
    lazy = functions_from(picker, ('R', 'z', 'B', 'V', 'H'))
    scenario = Path(__file__).parent.joinpath('codex_desktop_workflow/data', 'frontend_work_scenarios_26924_2738.js').read_text(encoding='utf8')
    scenario = scenario.replace('/* EXACT_PICKER_FUNCTIONS */', '\n'.join(lazy.values()))
    return execute(functions, scenario, node)
