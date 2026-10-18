"""Retain full first-configuration diagnostics rather than infer from revised candidates."""
from pilot_lib import ROOT,CONFIG,read,dump,verify_inputs,compile_model_ir,compile_policy,evaluate_ecas
verify_inputs();rows=[]
protocol=read(ROOT/'sealed_evaluation/branch_protocol.json')
for task in CONFIG['tasks']:
    source=ROOT/'effect_runs'/task/'ECAS_MATCHED'
    contract=read(ROOT/'execution_inputs'/task/'contract.json')
    proposal=compile_model_ir(read(source/'candidate.json'));policy=compile_policy(proposal['policy'],contract)
    assert policy==read(source/'admitted_policy.json')
    probes=[]
    for name,value,expected,basis in protocol['vectors'][task]:
        actual=evaluate_ecas(policy,contract,value,admission_mode='semantic')
        probes.append({'id':name,'input':value,'expected':expected,'basis':basis,'actual':actual,'pass':actual['decision']==expected and not actual.get('engine_error')})
    original=read(source/'RESULT.json')
    rows.append({'task':task,'configuration':'SCHEMA_ONLY_V1','requests':original['requests'],'pair_correct':original['request_pair_correct'],'branch_probes':probes})
verify_inputs();dump(ROOT/'V1_ECAS_DIAGNOSTICS.json',{'classification':'ORIGINAL_CONFIG_ENGINEERING_REPLAY_NO_NEW_MODEL_CALL','rows':rows,'new_model_calls':0})
import json
print(json.dumps([{'task':r['task'],'original_decisions':[x['actual']['decision'] for x in r['requests']],'wrong_probes':[x['id'] for x in r['branch_probes'] if not x['pass']]} for r in rows]))
