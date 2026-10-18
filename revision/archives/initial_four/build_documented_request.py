"""Freeze the documented ECAS configuration and bind separate serial requests."""
import sys
from pilot_lib import ROOT,CONFIG,read,dump,sha,verify_inputs
mode=sys.argv[1];verify_inputs()
if read(ROOT/'EXECUTION_STATE.json')['status']!='COMPLETED':raise RuntimeError('Base batch active')
if (ROOT/'FORMAT_RECOVERY_STATE.json').exists() and read(ROOT/'FORMAT_RECOVERY_STATE.json')['status']=='RUNNING':raise RuntimeError('Recovery active')
manifest=read(ROOT/'EXECUTION_INPUT_MANIFEST.json')
dest=ROOT/'DOCUMENTED_INPUT_MANIFEST.json'
if mode=='smoke':
    if dest.exists():raise RuntimeError('Documented config already frozen')
    for filename in ('EXECUTION_INPUT_MANIFEST.json','DOCUMENTED_ECAS_PROTOCOL_CN.md','DOCUMENTED_OPERATOR_SEMANTICS.json','DOCUMENTATION_SOURCE_RECEIPT.json','prepare_documented_ecas.py','run_documented_ecas.py','build_documented_request.py','DOCUMENTED_PROMPT_SIZES.json'):
        p=ROOT/filename;manifest.append({'path':str(p),'sha256':sha(p)})
    dump(dest,manifest)
elif mode=='run':manifest=read(dest)
else:raise ValueError('Unsupported mode')
inputs=manifest+[{'path':str(dest),'sha256':sha(dest)}]
if mode=='run':inputs.append({'path':str(ROOT/'DOCUMENTED_TOKEN_GATE.json'),'sha256':sha(ROOT/'DOCUMENTED_TOKEN_GATE.json')})
request={'schema_version':1,'run_id':'four-peer-documented-ecas-'+mode+'-v1','run_root':CONFIG['runtime_lane']+'/managed_runs','argv':['/usr/bin/python3',str(ROOT/'run_documented_ecas.py'),mode,'{run_dir}/outputs/result.json'],'cwd':str(ROOT),'inputs':inputs,'outputs':[{'path':'outputs/result.json','kind':'json','nonempty':True}],'timeout_seconds':1800 if mode=='smoke' else 3600,'authorization_ref':str(ROOT/'AUTHORIZATION_CN.md')+'; complete all-operation API documentation, same four cases/model/call cap<=40; schema-only outcomes retained separately'}
dump(ROOT/(request['run_id']+'.request.json'),request)
print({'run_id':request['run_id'],'calls':len(read(ROOT/'CALL_LEDGER.json')),'inputs':len(inputs)})
