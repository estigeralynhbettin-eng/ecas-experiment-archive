"""Bounded local OPA conformance checks; never generate baseline candidates."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OPA=ROOT.parent/'20260807_stage3_no_result_engineering_acceptance/tools/opa_windows_amd64_v1.19.0.exe'
EXPECTED='ED4EE673B2182352AF3A9D5F0DE4A74D23A063CBBB447723FB21AC5EAD8CD599'
FORBIDDEN={'http.send','net.lookup_ip_addr','opa.runtime','rand.intn','time.now_ns'}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def run(args,folder,name):
    r=subprocess.run([str(OPA),*map(str,args)],capture_output=True,text=True,encoding='utf-8',errors='strict',timeout=15)
    (folder/f'{name}.stdout.txt').write_text(r.stdout,encoding='utf-8')
    (folder/f'{name}.stderr.txt').write_text(r.stderr,encoding='utf-8')
    return r

def evaluate(policy,envelope,folder,name,capabilities):
    request=folder/f'{name}.input.json';dump(request,envelope)
    check=run(['check','--strict','--capabilities',capabilities,policy],folder,f'{name}_check')
    if check.returncode:
        return {'status':'COMPILE_REJECTED','check_exit':check.returncode,'decision':None}
    r=run(['eval','--capabilities',capabilities,'--format=json','--data',policy,'--input',request,'data.external_pilot.allow'],folder,f'{name}_eval')
    if r.returncode:
        return {'status':'EVALUATION_ERROR','check_exit':0,'eval_exit':r.returncode,'decision':None}
    data=json.loads(r.stdout)
    results=data.get('result',[])
    if len(results)!=1 or len(results[0].get('expressions',[]))!=1:
        return {'status':'UNDEFINED_OR_AMBIGUOUS','decision':None}
    value=results[0]['expressions'][0]['value']
    if type(value) is not bool:
        return {'status':'INVALID_DECISION_TYPE','decision':None}
    return {'status':'EXECUTED','check_exit':0,'eval_exit':0,'decision':'allow' if value else 'deny'}

def main():
    if sha(OPA)!=EXPECTED:raise RuntimeError('Frozen OPA binary hash mismatch')
    out=ROOT/'local_opa_conformance'
    out.mkdir(exist_ok=False)
    version=run(['version'],out,'version')
    if version.returncode:raise RuntimeError('OPA cannot start')
    r=run(['capabilities','--current'],out,'capabilities')
    if r.returncode:raise RuntimeError('OPA capability discovery failed')
    cap=json.loads(r.stdout)
    cap['builtins']=[b for b in cap['builtins'] if b['name'] not in FORBIDDEN]
    cap['allow_net']=[]
    caps=out/'restricted_capabilities.json';dump(caps,cap)
    valid=out/'synthetic_valid.rego'
    valid.write_text('package external_pilot\nimport rego.v1\ndefault allow := false\nallow if { input.request.body.probe >= 0 }\n',encoding='utf-8')
    malformed=out/'synthetic_malformed.rego';malformed.write_text('package external_pilot\nallow :=\n',encoding='utf-8')
    unsafe=out/'synthetic_forbidden.rego'
    unsafe.write_text('package external_pilot\nimport rego.v1\nallow if { http.send({"method":"GET","url":"https://example.invalid"}) }\n',encoding='utf-8')
    results=[]
    for name,policy,value,expected in [('known_allow',valid,0,'allow'),('known_deny',valid,-1,'deny'),('invalid_syntax',malformed,0,None),('forbidden_builtin',unsafe,0,None)]:
        result=evaluate(policy,{'request':{'body':{'probe':value}}},out,name,caps)
        ok=result['decision']==expected and (result['status']=='EXECUTED' if expected is not None else result['status']=='COMPILE_REJECTED')
        results.append({'fixture':name,'expected':expected,'actual':result,'pass':ok})
    report={'status':'PASS' if all(x['pass'] for x in results) else 'FAIL','classification':'SYNTHETIC_LOCAL_EVALUATOR_CONFORMANCE_ONLY','execution_lane':'WINDOWS_NATIVE_FROZEN_OPA','exception_reason':'Linux OPA/Regal download routes failed; reuse frozen Windows OPA for preparatory conformance only','opa_path':str(OPA),'opa_sha256':EXPECTED,'runner_sha256':sha(Path(__file__)),'checks':results,'baseline_model_calls':0,'baseline_effect_results':0,'formal_experiment_ready':False,'regal_available':False}
    dump(out/'SUMMARY.json',report)
    print(json.dumps({'status':report['status'],'checks':len(results),'baseline_effect_results':0}))
    return 0 if report['status']=='PASS' else 2

if __name__=='__main__':raise SystemExit(main())
