"""Fresh scope-bound engineering T0. No model calls."""
import datetime
import importlib.metadata
import json
import platform
import shutil
from pilot_lib import ROOT,LANE,CONFIG,read,dump,sha,tool,verify_inputs,capabilities,policy_checks,rego_decision,adapt,compile_model_ir,compile_policy,evaluate_ecas,PolicyError
verify_inputs();out=LANE/'outputs/t0';out.mkdir(exist_ok=False);capabilities(out)
checks=[]
for exe in ('opa','regal'):
    r=tool([LANE/'tools'/exe,'version'],out,exe+'_version');checks.append({'check':exe+'_startup','pass':r.returncode==0,'output':r.stdout})
good=policy_checks('package external_pilot\n\nimport rego.v1\n\ndefault allow := false\n\nallow if {\n\tinput.request.body.probe > 0\n}\n',out/'good',True)
checks.append({'check':'compile_and_full_regal','pass':good['accepted'],'detail':good})
for name,value,expected in [('allow',1,'allow'),('deny',-1,'deny')]:
    result=rego_decision(good['policy_path'],adapt('FSV-S03',{'request':{'body':{'probe':value}},'trusted':{}}),out,name)
    checks.append({'check':name,'pass':result['decision']==expected,'detail':result})
for name,source,expected in [('syntax','package external_pilot\nallow :=\n','COMPILE_REJECTED'),('network','package external_pilot\nimport rego.v1\nallow if { http.send({"method":"GET","url":"https://example.invalid"}) }\n','COMPILE_REJECTED'),('undefined','package external_pilot\nimport rego.v1\nallow if { false }\n','UNDEFINED_OR_AMBIGUOUS'),('non_boolean','package external_pilot\nallow := "deny"\n','NON_BOOLEAN')]:
    checked=policy_checks(source,out/name,False)
    status='COMPILE_REJECTED' if checked['compile_exit'] else rego_decision(checked['policy_path'],{'request':{'body':{}}},out/name,'evaluate')['status']
    checks.append({'check':name,'pass':status==expected,'observed':status})
screen=ROOT.parent/'20261014_multi_case_extension_screen'
candidate=read(screen/'cases/FSV-S03/gpt-5.6-sol-high/candidate.json');contract=read(ROOT/'execution_inputs/FSV-S03/contract.json')
proposal=compile_model_ir(candidate);admitted=compile_policy(proposal['policy'],contract)
directions=[evaluate_ecas(admitted,contract,{'request':{'body':{'age':value}},'trusted':{}},admission_mode='semantic')['decision']==expect for value,expect in [(43,'allow'),('43','deny')]]
missing=json.loads(json.dumps(contract));missing['evidence']=[]
try:compile_policy(proposal['policy'],missing);negative=False
except PolicyError:negative=True
checks.append({'check':'ecas_compile_admission_allow_deny_missing_evidence','pass':all(directions) and negative,'archived_engineering_fixture_not_model_input':True})
for task in CONFIG['tasks']:
    original={'request':{'body':{'probe':'T0-only'}},'trusted':{'probe':'unchanged'}};mapped=adapt(task,original)
    p=read(ROOT/'generation_inputs'/task/'packet.json')
    checks.append({'check':'complete_adapter_'+task,'pass':mapped['request']==original['request'] and mapped['trusted']==original['trusted'] and mapped['subject']=={'id':'authenticated_api_caller','role':'authenticated_api_caller'} and mapped['resource']=={'id':p['common_adapter']['resource_id'],'system':p['target']['system'],'version':p['target']['version']} and mapped['action']==p['target']['operation']})
tool(['ps','-eo','pid,comm'],out,'process_inventory')
receipt={'status':'PASS' if all(t['pass'] for t in checks) else 'FAIL','scope_id':CONFIG['scope_id'],'run_id':'four-peer-t0-v1','runtime_lane':str(LANE),'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observations':checks,'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'free_bytes':shutil.disk_usage(LANE).free,'shared_resources_used':[],'outputs_isolated':True,'raw_model_calls':0,'scientific_result':False}
verify_inputs();dump(ROOT/'T0_RECEIPT.json',receipt);dump(out/'RECEIPT.json',receipt)
dump(ROOT/'T0_EVIDENCE.json',{'status':receipt['status'],'scope_id':CONFIG['scope_id'],'run_id':receipt['run_id'],'receipt_path':'T0_RECEIPT.json','receipt_sha256':sha(ROOT/'T0_RECEIPT.json'),'completed_at':receipt['completed_at']})
print(json.dumps({'status':receipt['status'],'checks':len(checks),'failures':[t['check'] for t in checks if not t['pass']]}))
if receipt['status']!='PASS':raise SystemExit(2)
