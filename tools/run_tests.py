"""Run full Windows checks, or explicit binary-free CI checks with sealed evidence."""
from pathlib import Path
import argparse,sys,unittest

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-only',action='store_true',help='CI selection: unit tests and sealed native evidence; no fresh native execution')
args=parser.parse_args()
suite=unittest.TestSuite()
suite.addTests(unittest.TestLoader().discover(str(root/'tests')))
if not args.source_only:
    suite.addTests(unittest.TestLoader().discover(str(root/'acceptance_tests')))
else:
    print('CI source-only selection; fresh native acceptance must be completed separately before publication.',flush=True)
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
