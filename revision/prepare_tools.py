#!/usr/bin/env python3
"""Download the fixed OPA prerequisite; run before network isolation."""
from pathlib import Path
import urllib.request,hashlib,json,os,tempfile
root=Path(__file__).resolve().parent
target=root/'runtime/bin/opa'
expected='1dd5c5591ff856f5e20a1d66bafae9511ddf3c5552ed3b5070c70b2b6580ee3f'
url='https://github.com/open-policy-agent/opa/releases/download/v1.19.0/opa_linux_amd64_static'
target.parent.mkdir(parents=True,exist_ok=True)
if target.exists():
 if hashlib.sha256(target.read_bytes()).hexdigest()!=expected:raise SystemExit('Existing tool has a different digest; choose a fresh extraction.')
 target.chmod(target.stat().st_mode|0o111)
 print(json.dumps({'status':'PASS','downloaded':False}))
else:
 tmp=None
 try:
  with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as f:
   tmp=Path(f.name)
   with urllib.request.urlopen(url,timeout=60) as response:
    while True:
     chunk=response.read(1048576)
     if not chunk:break
     f.write(chunk)
  if hashlib.sha256(tmp.read_bytes()).hexdigest()!=expected:raise SystemExit('Downloaded tool digest mismatch; tool not installed.')
  tmp.chmod(tmp.stat().st_mode|0o111);os.replace(tmp,target);tmp=None
  print(json.dumps({'status':'PASS','downloaded':True}))
 finally:
  if tmp is not None and tmp.exists():tmp.unlink()
