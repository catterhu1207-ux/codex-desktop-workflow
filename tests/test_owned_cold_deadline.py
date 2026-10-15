"""Execute the actual cold-worker wait expression with an awake clock."""
import ast,unittest
from pathlib import Path
from types import SimpleNamespace

class ColdWorkerDeadline(unittest.TestCase):
    def statements(self):
        path=Path(__file__).resolve().parents[1]/'tools/new_chat/reopen_owned_9446.py'
        tree=ast.parse(path.read_text())
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
        block=next(n for n in main.body if isinstance(n,ast.Try)).body
        start=next(i for i,n in enumerate(block) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='deadline' for t in n.targets))
        return compile(ast.fix_missing_locations(ast.Module(body=block[start:start+3],type_ignores=[])),str(path),'exec')

    def test_paused_awake_clock_does_not_expire_worker(self):
        polls=iter([None,None,None,0]);sleeps=[]
        env={'worker':SimpleNamespace(poll=lambda:next(polls),returncode=0),'seconds':lambda:1000,'time':SimpleNamespace(sleep=lambda value:sleeps.append(value))}
        exec(self.statements(),env)
        self.assertEqual(len(sleeps),3)

    def test_actual_awake_expiration_still_rejects(self):
        times=iter([1000,1601])
        env={'worker':SimpleNamespace(poll=lambda:None,returncode=None),'seconds':lambda:next(times),'time':SimpleNamespace(sleep=lambda value:None)}
        with self.assertRaisesRegex(RuntimeError,'worker_awake_timeout'):exec(self.statements(),env)

if __name__=='__main__':unittest.main()
