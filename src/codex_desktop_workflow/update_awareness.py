"""Bounded official metadata checks for the independently installed public app."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,urllib.request
from .official_package_probe import fetch_package,URL

def version(value):
    return tuple(map(int,value.split('.'))) if isinstance(value,str) and re.fullmatch(r'\d+\.\d+\.\d+\.\d+',value) else None

def prepared_candidate(portable):
    """Read qualified sibling installations without starting or enabling them."""
    if not portable:return None
    from . import workflow
    from .renderer_proof import parse_owned_logs
    current=Path(portable).resolve()
    metadata=current/'codex-desktop-workflow.json'
    if not metadata.is_file() or metadata.is_symlink() or metadata.stat().st_size>65536:return None
    current_version=version(json.loads(metadata.read_bytes()).get('package_version'))
    if current_version is None:return None
    root=current.parent
    from itertools import islice
    entries=list(islice(root.iterdir(),257))
    if len(entries)>256:return None
    candidates=[entry for entry in entries if entry.is_dir()]
    if len(candidates)>32:return None
    ready=[]
    for folder in candidates:
        try:
            if not folder.is_dir() or folder.is_symlink() or folder.stat().st_file_attributes&0x400:continue
            receipt=folder/'codex-desktop-workflow-verification.json'
            public=folder/'codex-desktop-workflow.json'
            if any(not p.is_file() or p.is_symlink() or p.stat().st_size>2**20 for p in (receipt,public)):continue
            raw=receipt.read_bytes();qualification=json.loads(raw);identity=json.loads(public.read_bytes())
            support=workflow.SUPPORTED_PACKAGES.get(identity.get('package_version'))
            if support is None or qualification.get('status')!='passed' or qualification.get('owned_cleanup',{}).get('owned_job_empty') is not True:continue
            if version(support.version)<=current_version:continue
            runs=qualification.get('runtime',[])
            if len(runs)<3 or {r['profile'] for r in runs}!={'empty','synthetic_tasks','faithful_projects'}:continue
            if workflow._sha256(folder/'resources/app.asar')!=identity['portable_asar_sha256'] or workflow._sha256(folder/'resources/codex.exe')!=identity['backend_sha256']:continue
            manifest=folder/'codex-desktop-workflow-manifest.json'
            if not manifest.is_file():continue
            good=True
            for run in runs:
                if run.get('observed_seconds',0)<60 or run.get('backend_match') is not True or run.get('close',{}).get('close_status')!='closed' or run.get('native_sidebar',{}).get('status')!='passed':good=False;break
                proof=parse_owned_logs(manifest,Path(run['run_directory']),run['pre_close']['main'],readonly=True)
                if proof.get('status')!='passed':good=False;break
            if not good:continue
            ready.append({'status':'adaptation_prepared','qualified':True,'version':support.version,'source_asar_sha256':support.asar_sha256,'qualification_sha256':hashlib.sha256(raw).hexdigest()})
        except (OSError,ValueError,KeyError,RuntimeError,AttributeError):continue
    return max(ready,key=lambda item:version(item['version'])) if ready else None

def inspect(output:Path):
    package=fetch_package();published=None;prepared=prepared_candidate(os.environ.get('CODEX_WORKFLOW_PORTABLE'))
    try:
        request=urllib.request.Request('https://persistent.oaistatic.com/codex-app-prod/windows-store-update.json',headers={'Cache-Control':'no-cache'})
        with urllib.request.urlopen(request,timeout=12) as response:
            raw=response.read(65537)
        if len(raw)>65536:raise ValueError('update_metadata_too_large')
        value=json.loads(raw);candidate=value.get('version') if isinstance(value,dict) else None
        if version(candidate):published=candidate
    except Exception:pass
    if package['status']!='manifest_verified' and published is None and prepared is None:return {'status':'unavailable'}
    status={'schema_version':2,'checked_at':datetime.now(timezone.utc).isoformat(),'published_version':published,'package':package,'content_logged':False}
    if prepared is not None:status['prepared']=prepared
    result={'schema_version':2,'last_status':status}
    output.parent.mkdir(parents=True,exist_ok=True)
    temp=output.with_name(output.name+'.tmp-'+str(os.getpid()));temp.write_text(json.dumps(result),encoding='utf8');os.replace(temp,output)
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--mode',choices=('inspect','show'),default='inspect');args=parser.parse_args()
    if args.mode=='inspect':inspect(args.output);return 0
    status={}
    if args.output.is_file() and not args.output.is_symlink() and args.output.stat().st_size<=65536:
        status=json.loads(args.output.read_bytes()).get('last_status',{})
    current=None
    portable=os.environ.get('CODEX_WORKFLOW_PORTABLE')
    if portable:
        metadata=Path(portable)/'codex-desktop-workflow.json'
        if metadata.is_file() and metadata.stat().st_size<=65536:
            current=version(json.loads(metadata.read_bytes()).get('package_version'))
    prepared=status.get('prepared',{})
    package=status.get('package',{})
    available=version(package.get('version')) if package.get('status')=='manifest_verified' else None
    if current and available and available>current and not (prepared.get('qualified') is True and version(prepared.get('version')) and version(prepared['version'])>current):
        import webbrowser
        webbrowser.open(URL)
        return 0
    import ctypes
    chinese=bool(os.name=='nt' and ctypes.windll.kernel32.GetUserDefaultUILanguage()&0x3ff==4)
    if chinese:
        text='\u5b98\u65b9\u516c\u5e03\u7248\u672c：'+str(status.get('published_version') or '\u6682\u672a\u53d6\u5f97')+'\n\u53ef\u4e0b\u8f7d\u539f\u5305\u7248\u672c：'+str(package.get('version') or '\u6682\u672a\u53d6\u5f97')
        text+='\n\u9002\u914d\u51c6\u5907\u7248\u672c：'+str(prepared.get('version') if prepared.get('qualified') is True else '\u6682\u65e0\u5df2\u9a8c\u8bc1\u7684\u65b0\u5019\u9009')
        text+='\n\n\u516c\u5e03\u65b0\u7248\u4e0d\u4ee3\u8868\u4e0b\u8f7d\u5165\u53e3\u5df2\u66f4\u65b0。\u5df2\u51c6\u5907\u7684\u72ec\u7acb\u5019\u9009\u53ef\u5728\u5f53\u524d\u5e94\u7528\u81ea\u7136\u9000\u51fa\u540e\u542f\u52a8。'
        title='Codex Desktop \u66f4\u65b0\u72b6\u6001'
    else:
        text='Announced: '+str(status.get('published_version') or 'unavailable')+'\nDownloadable package: '+str(package.get('version') or 'unavailable')
        text+='\nPrepared adaptation: '+str(prepared.get('version') if prepared.get('qualified') is True else 'none qualified')
        text+='\n\nAn announcement does not mean the download changed. Start a qualified independent candidate after the current app exits.'
        title='Codex Desktop update status'
    if os.name=='nt':ctypes.windll.user32.MessageBoxW(None,text,title,0x40)
    else:print(text)
    return 0

if __name__=='__main__':raise SystemExit(main())
