"""Exercise the actual deadline expression; complete installer runs follow it."""
import ast,inspect,unittest
from codex_desktop_workflow import workflow,owned_verification

class CurrentExecutionBudget(unittest.TestCase):
    def test_confirmed_49_second_execution_fits_and_91_seconds_does_not(self):
        tree=ast.parse(inspect.getsource(workflow._verify_isolated))
        expressions=[n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='deadline' for t in n.targets) and isinstance(n.value,ast.BinOp) and isinstance(n.value.left,ast.Name) and n.value.left.id=='module_at']
        self.assertEqual(len(expressions),1)
        scope={'module_at':1000.0};exec(compile(ast.fix_missing_locations(ast.Module(body=expressions,type_ignores=[])),'actual-deadline','exec'),scope)
        self.assertLess(1000+49,scope['deadline']);self.assertGreater(1000+91,scope['deadline'])
        self.assertEqual(scope['deadline'],1090)

    def test_owner_budget_retains_observation_and_old_version_bound(self):
        tree=ast.parse(inspect.getsource(owned_verification.verify_owned))
        expression=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='per_run_budget' for t in n.targets))
        compiled=compile(ast.fix_missing_locations(ast.Module(body=[expression],type_ignores=[])),'actual-owner-budget','exec')
        for version in ('26.1007.9446.0','26.1013.4894.0','26.1016.6573.0'):
            with self.subTest(version=version):
                scope={'metadata':{'package_version':version},'observe_seconds':60,'SEALED_VERSIONS':owned_verification.SEALED_VERSIONS};exec(compiled,scope)
                self.assertEqual(scope['per_run_budget'],240+120+90+60+120+30+300)
        scope={'metadata':{'package_version':'26.928.4866.0'},'observe_seconds':60,'SEALED_VERSIONS':owned_verification.SEALED_VERSIONS};exec(compiled,scope);self.assertEqual(scope['per_run_budget'],420)

if __name__=='__main__':unittest.main()
