"""Exercise the packaged resolver before URL canonicalization can hide traversal."""
from pathlib import Path
import json,subprocess,hashlib,re
import hotfix_builder as b
import hotfix_profile_261007_9446 as p

def verify(portable):
    a=Path(portable)/'resources/app.asar';s,_,h=b.read_asar(a)
    raw=b.read_entry(a,s,b.get_entry_meta(h,p.PROFILE['attestation_protocol_entry_path']))[1].decode()
    helper=Path(__file__).parent/'data/native_fragments_261007_9446.cjs'
    def extract(source,names):
        cp=subprocess.run(['node',str(helper)],input=json.dumps({'source':source,'names':names}),capture_output=True,text=True,encoding='utf8',timeout=30,creationflags=0x08000000)
        if cp.returncode:raise RuntimeError(cp.stderr)
        return json.loads(cp.stdout)
    parts=extract(raw,['E','F','I','L','y','g','h','_'])
    src=b.read_entry(a,s,b.get_entry_meta(h,'.vite/build/src-CP7XXlpZ.js'))[1].decode()
    match=re.search(r'Object.defineProperty\(exports,"yi",\{enumerable:!0,get:function\(\)\{return (\w+)\}\}\)',src)
    if not match:raise RuntimeError('Packaged slash normalization export absent')
    normalizer=extract(src,[match[1]])[match[1]]
    scenario=r'''
const assert=require('node:assert/strict'),n='C:/synthetic/app/resources/app.asar/webview';
assert.equal(E('app://-/x',n),n+'/../../x.js');
assert.equal(a.relative(n,E('app://-/index.html',n)),'index.html');
assert.equal(a.relative(n,E('app://-/assets/module.js',n)),a.join('assets','module.js'));
const paths=['app://-/../x.js','app://-/%2e%2e/x.js','app://-/assets/%2e%2e/x.js','app://-/assets/%5c..%5cx.js','app://-/assets/.. ./x.js','app://other/x','https://-/x','file:///x','app://-/@fs/C:/private/x.js'];
for(const url of paths)assert.equal(E(url,n),null,url);
for(const url of ['app://-/x?extra=1','app://-/x#extra','app://-/%78','app://-/x.js'])assert.notEqual(E(url,n),n+'/../../x.js',url);
console.log(JSON.stringify({status:'passed',actual_packaged_resolver:true,actual_packaged_raw_path_guard:true,actual_packaged_slash_normalizer:true,exact_signed_route:true,ordinary_resource_route:true,traversal_rejected:true,bypass_rejected:true,negative_cases:paths.length+4}));
'''
    script="const a=require('node:path');\n"+normalizer+'\nconst t={yi:'+match[1]+'};\n'+'\n'.join(parts.values())+'\n'+scenario
    cp=subprocess.run(['node','-'],input=script,capture_output=True,text=True,encoding='utf8',timeout=30,creationflags=0x08000000)
    if cp.returncode:raise RuntimeError(cp.stderr)
    result=json.loads(cp.stdout);result['actual_script_sha256']=hashlib.sha256(script.encode()).hexdigest();return result
