"""Prepare a separate immutable request after first-batch completion."""
import json
from pathlib import Path
from pilot_lib import ROOT,CONFIG,read,dump,sha,verify_inputs
verify_inputs()
if read(ROOT/'EXECUTION_STATE.json')['status']!='COMPLETED':raise RuntimeError('First batch active or failed')
manifest=read(ROOT/'EXECUTION_INPUT_MANIFEST.json')
for name in ['EXECUTION_INPUT_MANIFEST.json','EXECUTION_STATE.json','TOKEN_GATE_READY.json','FORMAT_RECOVERY_PROTOCOL_CN.md','recover_grounding.py','build_recovery_request.py']:
    p=ROOT/name;manifest.append({'path':str(p),'sha256':sha(p)})
for p in (ROOT/'effect_runs').rglob('*.json'):manifest.append({'path':str(p),'sha256':sha(p)})
dest=ROOT/'FORMAT_RECOVERY_INPUT_MANIFEST.json'
if dest.exists():raise RuntimeError('Recovery freeze exists')
dump(dest,manifest)
inputs=manifest+[{'path':str(dest),'sha256':sha(dest)}]
request={'schema_version':1,'run_id':'four-peer-grounding-recovery-v1','run_root':CONFIG['runtime_lane']+'/managed_runs','argv':['/usr/bin/python3',str(ROOT/'recover_grounding.py'),'{run_dir}/outputs/result.json'],'cwd':str(ROOT),'inputs':inputs,'outputs':[{'path':'outputs/result.json','kind':'json','required_keys':['status','rows'],'nonempty':True}],'timeout_seconds':7200,'authorization_ref':str(ROOT/'AUTHORIZATION_CN.md')+'; same tasks/model/call cap; format-only object-id recovery documented in FORMAT_RECOVERY_PROTOCOL_CN.md'}
dump(ROOT/'four-peer-grounding-recovery-v1.request.json',request)
print(json.dumps({'inputs':len(inputs),'calls_consumed':len(read(ROOT/'CALL_LEDGER.json')),'max_calls':CONFIG['max_calls']}))
