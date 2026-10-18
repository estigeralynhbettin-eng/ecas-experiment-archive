"""Local execution functions; no network or model calls."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CONFIG=json.loads((ROOT/'EXECUTION_CONFIG.json').read_text(encoding='utf-8'))
LANE=Path(CONFIG['runtime_lane'])
sys.path.insert(0,str(LANE/'runtime/scripts'))
from ec_field_security_engine_v3 import compile_model_ir, compile_policy, evaluate as evaluate_ecas, PolicyError

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify_inputs():
    for item in read(ROOT/'EXECUTION_INPUT_MANIFEST.json'):
        if sha(item['path'])!=item['sha256']:raise RuntimeError('Frozen input changed: '+item['path'])

def tool(args,folder,name,timeout=25):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    proc=subprocess.run([str(a) for a in args],capture_output=True,text=True,encoding='utf-8',timeout=timeout)
    (folder/f'{name}.stdout.txt').write_text(proc.stdout,encoding='utf-8')
    (folder/f'{name}.stderr.txt').write_text(proc.stderr,encoding='utf-8')
    return proc

def adapt(task,envelope):
    p=read(ROOT/'generation_inputs'/task/'packet.json')
    value=json.loads(json.dumps(envelope))
    value.update({'subject':{'role':p['common_adapter']['subject_role']},'action':p['target']['operation'],
                  'resource':p['target']['system']+':'+p['target']['version']})
    return value

def capabilities(folder):
    r=tool([LANE/'tools/opa','capabilities','--current'],folder,'capabilities')
    if r.returncode:raise RuntimeError('Cannot discover OPA capabilities')
    cap=json.loads(r.stdout)
    forbidden={'http.send','net.lookup_ip_addr','opa.runtime','rand.intn','time.now_ns','print','internal.print'}
    cap['builtins']=[b for b in cap['builtins'] if b['name'] not in forbidden]
    cap['allow_net']=[]
    dest=Path(folder)/'restricted_capabilities.json';dump(dest,cap);return dest

def policy_checks(rego,folder,do_lint):
    folder=Path(folder);pp=folder/'external_pilot/policy.rego';pp.parent.mkdir(parents=True,exist_ok=True)
    pp.write_text(rego,encoding='utf-8')
    cap=LANE/'outputs/t0/restricted_capabilities.json'
    r=tool([LANE/'tools/opa','check','--strict','--capabilities',cap,pp],folder,'compile')
    check={'compile_exit':r.returncode,'compile_error':r.stderr[:4000],'policy_path':str(pp),'lint_exit':None,'lint_report':None}
    if do_lint:
        # Full Regal rule set is retained. The directory/package matching rule is
        # omitted because per-case output directories are a study storage convention.
        l=tool([LANE/'tools/regal','lint','--disable','directory-package-mismatch','--format','json','--timeout','20s',pp],folder,'lint')
        check['lint_exit']=l.returncode
        try:check['lint_report']=json.loads(l.stdout)
        except ValueError:check['lint_report']={'error':l.stderr[:3000]}
    check['accepted']=r.returncode==0 and (not do_lint or check['lint_exit']==0)
    dump(folder/'CHECKS.json',check);return check

def rego_decision(policy,envelope,folder,name):
    folder=Path(folder);ip=folder/f'{name}.input.json';dump(ip,envelope)
    r=tool([LANE/'tools/opa','eval','--capabilities',LANE/'outputs/t0/restricted_capabilities.json','--format=json','--data',policy,'--input',ip,'data.external_pilot.allow'],folder,name)
    if r.returncode:return {'status':'EVALUATION_ERROR','decision':None,'exit_code':r.returncode}
    results=json.loads(r.stdout).get('result',[])
    if len(results)!=1 or len(results[0].get('expressions',[]))!=1:return {'status':'UNDEFINED_OR_AMBIGUOUS','decision':None,'exit_code':0}
    value=results[0]['expressions'][0]['value']
    if type(value) is not bool:return {'status':'NON_BOOLEAN','decision':None,'exit_code':0}
    return {'status':'EXECUTED','decision':'allow' if value else 'deny','exit_code':0}

def run_tests(task,policy,tests,folder):
    rows=[]
    for i,t in enumerate(tests):
        if not isinstance(t,dict) or t.get('expected') not in ('allow','deny') or not isinstance(t.get('input'),dict):raise ValueError('Malformed developer test')
        result=rego_decision(policy,adapt(task,t['input']),folder,f'dev_{i:02d}')
        rows.append({'id':t.get('id',str(i)),'expected':t['expected'],'actual':result,'pass':result['decision']==t['expected'] and result['status']=='EXECUTED'})
    if not rows or not {'allow','deny'}.issubset({x['expected'] for x in rows}):raise ValueError('Developer tests lack positive/negative coverage')
    dump(Path(folder)/'DEVELOPER_RESULTS.json',rows)
    return {'passed':all(x['pass'] for x in rows),'rows':rows}
