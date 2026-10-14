"""Exercise both SSH data chains through the real new Work picker and callback."""
from pathlib import Path
from frontend_contract_26930_6422 import execute, functions_from
PICKER_PATH = 'webview/assets/composer-project-picker-content-1743898f92aa.js'
PICKER_SHA256 = '74b9634932a044d8fe2aaa149b3aa8a79b7f301330ba19adfe08e148ea5d9d8f'

def run(initial, primary, picker, shared, node='node'):
    functions = functions_from(initial, ('BOn', 'qZx', 'DOn', 'iOn', 'zOn', 'rQi', 'pkn', 'kM', 'lzn', 'cOn'), 'initial', node)
    functions['rawRemoteSelection'] = functions.pop('BOn').replace('function BOn(', 'function rawRemoteSelection(', 1)
    functions['actualProjectRoute'] = functions.pop('kM').replace('function kM(', 'function actualProjectRoute(', 1)
    functions.update(functions_from(primary, ('T7', 'fOt', 'mOt', '_et', 'u4', 'AAt', 'pkt', 'cDt', 'VDt'), 'primary', node))
    functions.update(functions_from(shared, ('EM', 'TM', 'obt'), 'shared', node))
    lazy = functions_from(picker, ('R', 'z', 'B', 'V', 'H'), 'picker', node)
    scenario = (Path(__file__).resolve().parent/'codex_desktop_workflow/data'/'frontend_work_scenarios_26930_6422.js').read_text(encoding='utf8')
    scenario = scenario.replace('/* EXACT_PICKER_FUNCTIONS */', '\n'.join(lazy.values()))
    return execute(functions, scenario, node)
