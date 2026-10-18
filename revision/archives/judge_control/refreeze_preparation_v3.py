#!/usr/bin/env python3
"""Freeze the zero-call pilot-pause repair without changing any model input."""
import copy
from pathlib import Path
import judge_control as j
root=j.ROOT;prior=root/'setup_history/preparation_v2'
if (root/'CALL_LEDGER.json').exists() or (root/'ROOT_DISPATCH_APPROVAL.json').exists():
    raise RuntimeError('no refreeze after approval or dispatch')
old=j.read(prior/'INPUT_MANIFEST.json')
allowed={str(root/p) for p in ['judge_control.py','verify_preparation.py','PROTOCOL_CN.md']}
for row in old:
    if row['path'] not in allowed and j.sha(row['path'])!=row['sha256']:
        raise RuntimeError('unexpected prepared input drift: '+row['path'])
plan=j.read(root/'CALL_PLAN.json');first=plan[0]
coverage={'actual_plan_receipt':'TOKEN_SMOKE_PLAN_ACTUAL.json','actual_plan_sha256':j.sha(root/'TOKEN_SMOKE_PLAN_ACTUAL.json'),
          'pilot_task':first['task'],'one_actual_call_only':True,'estimated_prompt_tokens':first['estimated_prompt_tokens'],
          'required_coverage':['longest_typed_ir_judge_input'],'maps_to_plan_dimensions':['p95','p99','max'],
          'dataset':'FOUR_TASKS_TYPED_IR_PUBLIC_SOURCE_CONTROL','maximum_k':2,
          'fragile_case_id':'FSV-B19_longest_two_candidate_review','all_response_schema_structures_same':True,
          'not_independent_observations':True,'total_judge_call_cap_unchanged':4,'shared_attempt_cap_unchanged':44}
j.dump(root/'PILOT_COVERAGE_MAP.json',coverage)
template={'schema_version':'1.0','data':{'scope_id':j.SCOPE,'status':'ROOT_FILLS_FROM_ACTUAL_MCP_RECEIPT','allow_formal_run':False,
        'final_max_output_tokens':16384,'dispatch_owner':'root','observed_records':'PILOT_RECORDS.json',
        'pilot_records_sha256':'ROOT_FILLS_AFTER_PILOT','pilot_ledger_sha256':'ROOT_FILLS_AFTER_PILOT',
        'actual_gate_receipt':'TOKEN_GATE_RECEIPT.json','actual_gate_receipt_sha256':'ROOT_FILLS_ACTUAL_MCP_RECEIPT_HASH','issues':[]}}
j.dump(root/'TOKEN_GATE_READY_TEMPLATE.json',template)
scope={'kind':'new-experiment-block','status':'FROZEN','protocol_path':'PROTOCOL_CN.md','protocol_sha256':j.sha(root/'PROTOCOL_CN.md'),
       'scope_id':j.SCOPE,'project_id':'EC-CSI','experiment_id':'typed-ir-semantic-judge-control',
       'tasks':j.TASKS,'classification':'RETROSPECTIVE_TYPED_IR_SEMANTIC_JUDGE_INTERNAL_CONTROL_NOT_NATIVE_AUTOPAC',
       'runtime_lane':str(j.LANE),'historical_exposure':'Four previously exposed tasks, eight archived parent candidates; not blind or independent holdout.',
       'paid_calls_authorized_total_cap':44,'judge_calls_within_shared_cap':4,'pilot_calls_within_judge_four':1,
       'remaining_calls_after_pilot':3,'automatic_api_retries':0,'new_systems':0,'new_cases':0}
j.dump(root/'EXPERIMENT_SCOPE.json',scope)
extra=['verify_preparation.py','PROTOCOL_CN.md','ROOT_DISPATCH_APPROVAL_TEMPLATE.json',
       'refreeze_preparation_v3.py','PILOT_COVERAGE_MAP.json','TOKEN_GATE_READY_TEMPLATE.json','TOKEN_SMOKE_PLAN_ACTUAL.json','EXPERIMENT_SCOPE.json']
paths={row['path'] for row in old}|{str(root/p) for p in extra}
items=[{'path':p,'sha256':j.sha(p)} for p in sorted(paths)]
j.dump(root/'INPUT_MANIFEST.json',items)
req=j.read(prior/'T0_REQUEST.json');req['run_id']='typed-ir-judge-t0-v3'
req['inputs']=items+[{'path':str(root/'INPUT_MANIFEST.json'),'sha256':j.sha(root/'INPUT_MANIFEST.json')}]
j.dump(root/'T0_REQUEST.json',req)
run=j.read(prior/'RUN_REQUEST_BASE.json');run['run_id']='typed-ir-judge-control-v3';run['inputs']=copy.deepcopy(req['inputs'])
j.dump(root/'RUN_REQUEST_BASE.json',run)
pilot=copy.deepcopy(run);pilot['run_id']='typed-ir-judge-pilot-v1';pilot['argv'][2]='pilot';pilot['timeout_seconds']=900
pilot['outputs'][0]['required_keys']=['status','calls','model_calls','pilot_records_sha256','pilot_ledger_sha256']
pilot['authorization_ref']='root-only first of original four Judge calls; pause for actual MCP token gate; shared44 cap unchanged'
j.dump(root/'PILOT_REQUEST_BASE.json',pilot)
print(j.compact({'status':'REFROZEN_FOR_ZERO_CALL_T0','input_count':len(items),'t0_run_id':req['run_id'],
                'pilot_run_id':pilot['run_id'],'remaining_run_id':run['run_id'],'all_original_model_inputs_unchanged':True,'model_calls':0}))
