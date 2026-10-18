"""Hash-bound single-dispatch managed requests; no model calls."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mode=sys.argv[1];config=read(ROOT/'EXECUTION_CONFIG.json');manifest=read(ROOT/'EXECUTION_INPUT_MANIFEST.json')
if mode=='smoke':
    if (ROOT/'CALL_LEDGER.json').exists():raise RuntimeError('Smoke already started; query original run')
    changes=[]
    for x in manifest:
        if x['path']==str(ROOT/'managed_entry.py'):
            changes.append({'path':x['path'],'before':x['sha256'],'after':sha(ROOT/'managed_entry.py'),'reason':'smoke artifact selection repair before first call'})
            x['sha256']=sha(ROOT/'managed_entry.py')
    for name in ['build_requests.py','T0_RECEIPT.json','T0_EVIDENCE.json','SCOPED_GATE_READY.json']:
        p=ROOT/name;manifest.append({'path':str(p),'sha256':sha(p)})
    dump(ROOT/'PRE_CALL_FREEZE_REPAIR.json',{'model_calls':0,'changes':changes})
    dump(ROOT/'EXECUTION_INPUT_MANIFEST.json',manifest)
elif mode!='run':raise ValueError('Unsupported mode')
runid='four-peer-token-smoke-v1' if mode=='smoke' else 'four-peer-effects-v1'
inputs=manifest+[{'path':str(ROOT/'EXECUTION_INPUT_MANIFEST.json'),'sha256':sha(ROOT/'EXECUTION_INPUT_MANIFEST.json')}]
if mode=='run':inputs.append({'path':str(ROOT/'TOKEN_GATE_READY.json'),'sha256':sha(ROOT/'TOKEN_GATE_READY.json')})
request={'schema_version':1,'run_id':runid,'run_root':config['runtime_lane']+'/managed_runs','argv':['/usr/bin/python3',str(ROOT/'managed_entry.py'),mode,'{run_dir}/outputs/result.json'],'cwd':str(ROOT),'inputs':inputs,'outputs':[{'path':'outputs/result.json','kind':'json','required_keys':(['status','rows'] if mode=='run' else []),'nonempty':True}],'timeout_seconds':1800 if mode=='smoke' else 18000,'authorization_ref':str(ROOT/'AUTHORIZATION_CN.md')+'; current user starts four-case peer baselines, total <=40 calls'}
dump(ROOT/(runid+'.request.json'),request)
print(json.dumps({'request':str(ROOT/(runid+'.request.json')),'inputs':len(inputs)}))
