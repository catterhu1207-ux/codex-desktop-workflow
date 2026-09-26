"""Exercise both SSH data chains through the real new Work picker and callback."""
from pathlib import Path
from frontend_contract_26924_1866 import execute, functions_from

PICKER_PATH='webview/assets/composer-project-picker-content-cefe9ab592b1.js'
PICKER_SHA256='b2182f5d9f3a731763bf12b9b28877482b694d2743e3b5496d8ae3bd435094bf'

def run(initial, primary, picker, shared, node='node'):
    functions=functions_from(initial,('k7t','qZx','m7t','Q5t','O7t','Wjr','t9t','II','FI','t7t'))
    functions.update(functions_from(primary,('b9','M8t','P8t','fZt','nX','S9t','W5t','y6t','d8t')))
    functions.update(functions_from(shared,('tj','ej','Qst')))
    lazy=functions_from(picker,('R','z','B','V','H'))
    scenario=Path(__file__).parent.joinpath('codex_desktop_workflow/data', 'frontend_work_scenarios_26924_1866.js').read_text(encoding='utf8')
    scenario=scenario.replace('/* EXACT_PICKER_FUNCTIONS */','\n'.join(lazy.values()))
    return execute(functions,scenario,node)
