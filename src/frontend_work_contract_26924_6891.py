"""Exercise both SSH data chains through the real new Work picker and callback."""
from pathlib import Path
from frontend_contract_26924_6891 import execute, functions_from
PICKER_PATH = 'webview/assets/composer-project-picker-content-2c91512fdbc2.js'
PICKER_SHA256 = '3c6bfc080ba964730e750db72674d9bdc3a8a00ace0b22691e6c6350cd067986'

def run(initial, primary, picker, shared, node='node'):
    functions = functions_from(initial, ('h9t', 'qZx', 'e9t', 'R7t', 'm9t', 'BNr', 'V9t', 'jI', 'AI', 'V7t'))
    functions['rawRemoteSelection'] = functions.pop('h9t').replace('function h9t(', 'function rawRemoteSelection(', 1)
    functions.update(functions_from(primary, ('b9', '_5t', 'y5t', 'ZZt', 'ZY', 'sen', 'k7t', 'i8t', 'X8t')))
    functions.update(functions_from(shared, ('YA', 'JA', 'ict')))
    lazy = functions_from(picker, ('R', 'z', 'B', 'V', 'H'))
    scenario = (Path(__file__).resolve().parent/'codex_desktop_workflow/data'/'frontend_work_scenarios_26924_6891.js').read_text(encoding='utf8')
    scenario = scenario.replace('/* EXACT_PICKER_FUNCTIONS */', '\n'.join(lazy.values()))
    return execute(functions, scenario, node)
