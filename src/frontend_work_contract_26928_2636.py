"""Exercise both SSH data chains through the real new Work picker and callback."""
from pathlib import Path
from frontend_contract_26928_2636 import execute, functions_from
PICKER_PATH = 'webview/assets/composer-project-picker-content-208ae4bb11d4.js'
PICKER_SHA256 = 'a91969f319b280c88a61f07e4f90e21ec5a87fea8ca1c5e04151620dd0eb4ae9'

def run(initial, primary, picker, shared, node='node'):
    functions = functions_from(initial, ('VOn', 'qZx', 'OOn', 'oOn', 'BOn', 'cQi', 'mkn', 'TM', 'fzn', 'uOn'))
    functions['rawRemoteSelection'] = functions.pop('VOn').replace('function VOn(', 'function rawRemoteSelection(', 1)
    functions['actualProjectRoute'] = functions.pop('TM').replace('function TM(', 'function actualProjectRoute(', 1)
    functions.update(functions_from(primary, ('T7', 'fOt', 'mOt', '_et', 'u4', 'AAt', 'pkt', 'cDt', 'VDt')))
    functions.update(functions_from(shared, ('EM', 'TM', 'obt')))
    lazy = functions_from(picker, ('R', 'z', 'B', 'V', 'H'))
    scenario = (Path(__file__).resolve().parent/'codex_desktop_workflow/data'/'frontend_work_scenarios_26928_2636.js').read_text(encoding='utf8')
    scenario = scenario.replace('/* EXACT_PICKER_FUNCTIONS */', '\n'.join(lazy.values()))
    return execute(functions, scenario, node)
