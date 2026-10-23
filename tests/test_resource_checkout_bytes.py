"""A Windows checkout must preserve bytes used by source/runtime hash gates."""
from pathlib import Path
import os,subprocess,tempfile,unittest

ROOT=Path(__file__).resolve().parents[1]

class ResourceCheckoutBytes(unittest.TestCase):
    def test_future_version_resources_survive_autocrlf_checkout(self):
        raw=b'// synthetic future runtime\nexport const feature = "retained";\n'
        with tempfile.TemporaryDirectory() as name:
            folder=Path(name)
            def git(*args):
                return subprocess.run(['git','-C',str(folder),*args],capture_output=True,check=True)
            git('init');git('config','core.autocrlf','true')
            (folder/'.gitattributes').write_bytes((ROOT/'.gitattributes').read_bytes())
            files=[]
            for suffix in ['mjs','cjs','ps1','json','bin']:
                file=folder/'src/codex_desktop_workflow/data'/('future-261999-9999.'+suffix)
                file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(raw);files.append(file)
            git('add','.')
            for file in files:file.unlink()
            git('checkout-index','--all','--force')
            for file in files:
                with self.subTest(resource=file.name):self.assertEqual(file.read_bytes(),raw)

    def test_control_without_resource_attribute_changes_text_bytes(self):
        if os.name!='nt':self.skipTest('Actual Windows newline conversion control')
        with tempfile.TemporaryDirectory() as name:
            folder=Path(name)
            def git(*args):
                return subprocess.run(['git','-C',str(folder),*args],capture_output=True,check=True)
            git('init');git('config','core.autocrlf','true')
            file=folder/'runtime.mjs';raw=b'export const synthetic = true;\n';file.write_bytes(raw)
            git('add','.');file.unlink();git('checkout-index','--all','--force')
            self.assertNotEqual(file.read_bytes(),raw)
            self.assertIn(b'\r\n',file.read_bytes())
