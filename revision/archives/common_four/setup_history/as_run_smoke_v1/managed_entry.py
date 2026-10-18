"""Managed foreground entry. Root owns paid dispatch and gate files."""
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
mode=sys.argv[1]
result=subprocess.run(['/usr/bin/python3',str(ROOT/'run_matched.py'),mode])
if result.returncode:raise SystemExit(result.returncode)
source=ROOT/('SMOKE_RECORDS.json' if mode=='smoke' else 'EXECUTION_STATE.json')
target=Path(sys.argv[2]);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
