"""Exercise both SSH data chains through the real new Work picker and callback."""
from pathlib import Path
from frontend_contract_26930_7945 import execute, functions_from
PICKER_PATH = 'webview/assets/composer-project-picker-content-2ad99af79d29.js'
PICKER_SHA256 = 'ab19a477d9ca6932906d14da8b87468c1049cdb526ca7bd18882a442e402a499'

def run(initial, primary, picker, shared, node='node'):
    functions = functions_from(initial, ('BOn', 'qZx', 'DOn', 'iOn', 'zOn', 'rQi', 'pkn', 'kM', 'lzn', 'cOn'), 'initial', node)
    functions['rawRemoteSelection'] = functions.pop('BOn').replace('function BOn(', 'function rawRemoteSelection(', 1)
    functions['actualProjectRoute'] = functions.pop('kM').replace('function kM(', 'function actualProjectRoute(', 1)
    functions.update(functions_from(primary, ('T7', 'fOt', 'mOt', '_et', 'u4', 'AAt', 'pkt', 'cDt', 'VDt'), 'primary', node))
    functions.update(functions_from(shared, ('EM', 'TM', 'obt'), 'shared', node))
    lazy = functions_from(picker, ('R', 'z', 'B', 'V', 'H'), 'picker', node)
    scenario = (Path(__file__).resolve().parent/'codex_desktop_workflow/data'/'frontend_work_scenarios_26930_7945.js').read_text(encoding='utf8')
    scenario = scenario.replace('/* EXACT_PICKER_FUNCTIONS */', '\n'.join(lazy.values()))
    return execute(functions, scenario, node)
