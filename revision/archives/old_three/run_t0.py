"""Observed local T0 with positive and negative fixtures; no model calls."""
import datetime
import json
import os
import platform
import shutil
import subprocess
import importlib.metadata
from pathlib import Path
from pilot_lib import ROOT,LANE,CONFIG,dump,read,sha,verify_inputs,tool,capabilities,policy_checks,rego_decision,adapt,compile_model_ir,compile_policy,evaluate_ecas,PolicyError

def main():
    verify_inputs()
    out=LANE/'outputs/t0';out.mkdir(exist_ok=False)
    capabilities(out)
    observations=[]
    for exe in ('opa','regal'):
        r=tool([LANE/'tools'/exe,'version'],out,exe+'_version')
        observations.append({'check':exe+'_startup','pass':r.returncode==0,'output':r.stdout})
    fake='package external_pilot\n\nimport rego.v1\n\ndefault allow := false\n\nallow if {\n\tinput.request.body.probe > 0\n}\n'
    good=policy_checks(fake,out/'good',True)
    observations.append({'check':'compile_and_regal','pass':good['accepted'],'detail':good})
    for name,value,expected in [('allow',1,'allow'),('deny',-1,'deny')]:
        result=rego_decision(good['policy_path'],adapt('FSV-B06',{'request':{'body':{'probe':value}},'trusted':{}}),out,name)
        observations.append({'check':name,'pass':result['decision']==expected,'detail':result})
    for name,source,expected in [
       ('syntax','package external_pilot\nallow :=\n','COMPILE_REJECTED'),
       ('network','package external_pilot\nimport rego.v1\nallow if { http.send({"method":"GET","url":"https://example.invalid"}) }\n','COMPILE_REJECTED'),
       ('undefined','package external_pilot\nimport rego.v1\nallow if { false }\n','UNDEFINED_OR_AMBIGUOUS'),
       ('non_boolean','package external_pilot\nallow := "deny"\n','NON_BOOLEAN')]:
        ch=policy_checks(source,out/name,False)
        status='COMPILE_REJECTED' if ch['compile_exit'] else rego_decision(ch['policy_path'],{'request':{'body':{}}},out/name,'evaluate')['status']
        observations.append({'check':name,'pass':status==expected,'observed':status})
    # Exercise unchanged ECAS engine/admission/negative path on an archived engineering fixture.
    demo=ROOT.parent/'20261013_gateway_case_audit/selected_case_demo'
    candidate=read(demo/'cases/FSV-B06/main-qwen/candidate.json')
    contract=read(ROOT/'execution_inputs/FSV-B06/contract.json')
    proposal=compile_model_ir(candidate);admitted=compile_policy(proposal['policy'],contract)
    decisions=[]
    for truth,expected in [(True,'allow'),(False,'deny')]:
        result=evaluate_ecas(admitted,contract,{'request':{'body':{'developer_probe':'T0'}},'trusted':{'reAgeIsLatestTransaction':truth}},admission_mode='semantic')
        decisions.append(result['decision']==expected and not result.get('engine_error'))
    missing=json.loads(json.dumps(contract));missing['evidence']=[]
    try:compile_policy(proposal['policy'],missing);negative=False
    except PolicyError:negative=True
    observations.append({'check':'ecas_compile_admit_allow_deny_missing_evidence','pass':all(decisions) and negative,'archived_fixture':True})
    original={'request':{'body':{'developer_probe':'T0-only'}},'trusted':{'state':'unchanged'}}
    mapped=adapt('FSV-B06',original)
    observations.append({'check':'adapter_preserves_payload_and_trusted','pass':mapped['request']==original['request'] and mapped['trusted']==original['trusted']})
    # Observe active resources. This lane uses neither Docker, GPU, DB, ports nor services.
    ps=tool(['ps','-eo','pid,comm,args'],out,'process_inventory')
    disk=shutil.disk_usage(LANE)
    receipt={'status':'PASS' if all(x['pass'] for x in observations) else 'FAIL','scope_id':CONFIG['scope_id'],'run_id':'external-adaptation-t0-v1','runtime_lane':str(LANE),'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observations':observations,'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'free_bytes':disk.free,'shared_resources_used':[],'outputs_isolated':True,'raw_model_calls':0,'scientific_result':False,'engine_inputs_frozen':True}
    verify_inputs();dump(out/'RECEIPT.json',receipt);dump(ROOT/'T0_RECEIPT.json',receipt)
    if receipt['status']=='PASS':
        # Scope-bound receipt, not a root scientific-result ledger mutation.
        pointer={'status':'PASS','scope_id':CONFIG['scope_id'],'run_id':receipt['run_id'],'runtime_lane':str(LANE),'completed_at':receipt['completed_at'],'receipt_path':'working/exploration/20261014_external_baseline_pilot/T0_RECEIPT.json','receipt_sha256':sha(ROOT/'T0_RECEIPT.json')}
        root_pointer=ROOT.parents[2]/'T0_EVIDENCE.json'
        if root_pointer.exists():raise RuntimeError('Root T0 exists; do not replace another scope')
        dump(root_pointer,pointer)
    print(json.dumps({'status':receipt['status'],'checks':len(observations),'failures':[x['check'] for x in observations if not x['pass']]}))
    return 0 if receipt['status']=='PASS' else 2

if __name__=='__main__':raise SystemExit(main())
