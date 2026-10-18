"""Managed foreground entry preserving true exit and final artifact."""
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
mode=sys.argv[1]
proc=subprocess.run(['/usr/bin/python3',str(ROOT/'run_pilot.py'),mode])
if proc.returncode:raise SystemExit(proc.returncode)
source=ROOT/'SMOKE_RECORDS.json' if mode=='recover_ecas_smoke' else ROOT/'EXECUTION_STATE.json'
dest=Path(sys.argv[2]);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
