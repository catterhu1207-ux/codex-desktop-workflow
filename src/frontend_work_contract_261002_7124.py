"""Exercise both SSH data chains through the real new Work picker and callback."""
from pathlib import Path
from frontend_contract_261002_7124 import execute, functions_from
PICKER_PATH = 'webview/assets/composer-project-picker-content-9ec8ec549fb9.js'
PICKER_SHA256 = '8920fe7ae368e52e35016860ab1678a71f5fd3b9ec838f87cc07fbe0052bd48a'

def run(initial, primary, picker, shared, node='node'):
    from frontend_bindings_261002_7124 import native_function
    functions = functions_from(initial, ('BOn', 'qZx', 'DOn', 'iOn', 'zOn', 'rQi', 'pkn', 'kM', 'lzn', 'cOn'), 'initial', node)
    functions['rawRemoteSelection'] = functions.pop('BOn').replace('function BOn(', 'function rawRemoteSelection(', 1)
    functions['actualProjectRoute'] = functions.pop('kM').replace('function kM(', 'function actualProjectRoute(', 1)
    text=initial.decode() if isinstance(initial,bytes) else initial
    if text.count('Ifi as jzt')!=1 or (primary.decode() if isinstance(primary,bytes) else primary).count('jzt as CAe')!=1:
        raise RuntimeError('Native local capability import chain differs')
    functions['CAe']=native_function(text,'Ifi',node)+'\nconst CAe=Ifi;'
    functions.update(functions_from(primary, ('T7', 'fOt', 'mOt', '_et', 'u4', 'AAt', 'pkt', 'cDt', 'VDt'), 'primary', node))
    functions.update(functions_from(shared, ('EM', 'TM', 'obt'), 'shared', node))
    lazy = functions_from(picker, ('R', 'z', 'B', 'V', 'H'), 'picker', node)
    scenario = (Path(__file__).resolve().parent/'codex_desktop_workflow/data'/'frontend_work_scenarios_261002_7124.js').read_text(encoding='utf8')
    scenario='const wu={projectChatGptProvisioning:{}},gD=()=>false;\n'+scenario
    scenario = scenario.replace('/* EXACT_PICKER_FUNCTIONS */', '\n'.join(lazy.values()))
    return execute(functions, scenario, node)
