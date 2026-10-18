#!/usr/bin/env python3
"""Bind actual zero-call T0 evidence and its engineering-only scope ledger."""
import csv
import io
from pathlib import Path
import judge_control as j
root=j.ROOT
t0=j.read(root/'T0_RECEIPT.json');request=j.read(root/'T0_REQUEST.json')
status=j.read(Path(request['run_root'])/request['run_id']/'status.json')
if t0['status']!='PASS' or status['state']!='SUCCEEDED' or status['exit_code']!=0:
    raise RuntimeError('actual successful T0 required')
manifest={'status':'PASS','scope_id':j.SCOPE,'run_id':request['run_id'],'runtime_lane':str(j.LANE),
          'receipt_path':'T0_RECEIPT.json','receipt_sha256':j.sha(root/'T0_RECEIPT.json'),'completed_at':t0['completed_at']}
j.dump(root/'T0_EVIDENCE.json',manifest)
header=next(csv.reader(io.StringIO((j.MAIN/'RESULT_TRACEABILITY.csv').read_text(encoding='utf-8-sig'))))
count=len(t0['checks']);relative='working/exploration/20261014_matched_evidence_labor/judge_control/'
values={'result_id':'JUDGE-20261015-T0-V3','experiment_id':j.SCOPE,'metric_name':'non_scientific_t0_checks',
        'dataset_name':'SYNTHETIC_ENGINEERING_FIXTURES','dataset_version':'T0-v3','data_split':'engineering_only_not_scientific',
        'sample_count':str(count),'raw_value':str(count),'reported_value':str(count),'unit':'checks',
        'aggregation':'count_actual_passed_checks','source_output_path':relative+'T0_RECEIPT.json',
        'source_locator':'status;checks','script_path':relative+'judge_control.py','command_or_config':'T0_REQUEST.json;judge_control.py t0',
        'seed':'NOT_APPLICABLE','environment':'WSL Ubuntu Python3.10 isolated typed-IR Judge lane; zero model calls',
        'git_commit':'NOT_AVAILABLE_HASH_FROZEN','git_tag':'','checksum':j.sha(root/'T0_RECEIPT.json'),
        'rounding_rule':'none','status':'PASS','verified_by':'actual_managed_t0_and_scope_preparation_QA','verified_at':t0['completed_at'],
        'notes':'Engineering only: actual-main-run binding and pilot pause/token gate/cache checks; no semantic effect result'}
with (root/'RESULT_TRACEABILITY.csv').open('w',encoding='utf-8-sig',newline='') as out:
    writer=csv.DictWriter(out,fieldnames=header,quoting=csv.QUOTE_ALL);writer.writeheader();writer.writerow(values)
claimheader=(j.MAIN/'CLAIM_EVIDENCE_MATRIX.csv').read_text(encoding='utf-8-sig').splitlines()[0]
(root/'CLAIM_EVIDENCE_MATRIX.csv').write_text(claimheader+'\n',encoding='utf-8')
def normalize_schema(value):
    if isinstance(value,dict):return {k:('__LITERAL__' if k=='const' else normalize_schema(v)) for k,v in value.items()}
    if isinstance(value,list):return [normalize_schema(v) for v in value]
    return value
schemas=[normalize_schema(j.read(root/'schemas'/f'{task}.json')) for task in j.TASKS]
old=j.read(root/'setup_history/preparation_v2/INPUT_MANIFEST.json')
protected=[row for row in old if any(part in row['path'] for part in ['/prompts/','/candidate_inputs/','/schemas/','/generation_inputs/'])]
qa={'status':'PASS','model_calls':0,'all_original_model_inputs_unchanged':all(j.sha(row['path'])==row['sha256'] for row in protected),
    'same_response_schema_structure_except_literal_ids':all(schema==schemas[0] for schema in schemas),
    'protected_input_count':len(protected),'source_plan_sha256':j.sha(root/'TOKEN_SMOKE_PLAN_ACTUAL.json'),
    'one_observation_for_one_call':True,'required_coverage':['longest_typed_ir_judge_input']}
if not qa['all_original_model_inputs_unchanged'] or not qa['same_response_schema_structure_except_literal_ids']:
    raise RuntimeError('model input/response schema structure changed')
j.dump(root/'PILOT_COVERAGE_QA.json',qa)
print(j.compact({'status':'SCOPE_ENGINEERING_EVIDENCE_BOUND','t0_run_id':request['run_id'],'check_count':count,
                 'scope_ledger_rows':1,'claim_rows':0,'model_calls':0,'coverage_qa':qa['status']}))
