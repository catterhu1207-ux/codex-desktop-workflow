import unittest
import subprocess
import sys
from electron_update_safety.lifecycle import ProcessIdentity
from codex_desktop_workflow.isolated_run import descendants


def row(pid, parent, created, image='C:/synthetic/app.exe'):
    return ProcessIdentity(pid, parent, image, '/Date('+str(created)+')/')


class ProcessAncestry(unittest.TestCase):
    def test_realistic_pid_reuse_cycle_terminates(self):
        # Equal timestamp resolution must not turn the cycle test itself into
        # an unbounded test if the visited-identity protection is regressed.
        code="from electron_update_safety.lifecycle import ProcessIdentity as P; from codex_desktop_workflow.isolated_run import descendants; r=[P(10,30,'C:/synthetic/app.exe','/Date(200)/'),P(20,10,'C:/synthetic/app.exe','/Date(200)/'),P(30,20,'C:/synthetic/app.exe','/Date(200)/')]; print([x.pid for x in descendants(r,r[0])])"
        result=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'[20, 30]')

    def test_older_child_of_reused_parent_is_not_owned(self):
        main=row(10,1,200)
        rows=[main,row(20,10,100),row(30,20,201),row(40,10,202)]
        self.assertEqual([x.pid for x in descendants(rows,main)],[40])

    def test_wrong_main_identity_cannot_adopt_descendants(self):
        expected=row(10,1,200)
        self.assertEqual(descendants([row(10,1,300),row(20,10,301)],expected),[])

    def test_deep_tree_visits_each_identity_once(self):
        main=row(10,1,100)
        rows=[main]+[row(i,i-1,100+i) for i in range(11,3000)]
        self.assertEqual(len(descendants(rows,main)),len(rows)-1)

    def test_ambiguous_pid_or_missing_birth_is_rejected(self):
        main=row(10,1,100)
        with self.assertRaises(RuntimeError):descendants([main,main],main)
        with self.assertRaises(RuntimeError):
            descendants([main,ProcessIdentity(20,10,'C:/synthetic/app.exe','')],main)


if __name__=='__main__':unittest.main()
