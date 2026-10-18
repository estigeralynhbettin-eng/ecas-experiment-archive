"""Explicit zero-network reparse of the third immutable smoke raw response."""
import datetime
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from pilot_lib import ROOT,read,dump,sha
from run_matched import normalize_stage,validate_stage,make_prompt,SCHEMA

EXPECTED_RAW='5fa3595aff72e11800f8cf69e9aa8575d05bf2d8cddf040f0ccf696de8a1351a'
folder=ROOT/'calls/03_FSV-B19_ecas_generate'
raw_path=folder/'response.raw.json'
if sha(raw_path)!=EXPECTED_RAW:raise RuntimeError('Explicit recovery raw identity mismatch')
snapshot=ROOT/'setup_history/as_run_smoke_v1'
original_ledger=read(snapshot/'CALL_LEDGER.json')
ledger=read(ROOT/'CALL_LEDGER.json')
if len(ledger)!=3 or ledger!=original_ledger:raise RuntimeError('Recovery must apply to the exact unresolved three-attempt ledger')
item=ledger[2]
if item['index']!=3 or item['status']!='STOPPED_PROTOCOL_OR_TRANSPORT' or item.get('error_type')!='KeyError' or item.get('error')!="'candidate'":
    raise RuntimeError('Prior failure is not the approved wrapper-only failure')
raw=read(raw_path);content=json.loads(raw['choices'][0]['message']['content'])
if content!=read(folder/'content.json'):raise RuntimeError('Wrapper content and immutable raw disagree')
prompt,begin,end=make_prompt('FSV-B19','ecas_generate',smoke=True,smoke_id='ecas_long')
if hashlib.sha256(prompt.encode()).hexdigest()!=item['prompt_sha256'] or sha(item['prompt_path'])!=item['prompt_sha256']:
    raise RuntimeError('Recovery prompt differs from the exact original')
if raw.get('model')!='glm-5.2' or raw['choices'][0]['finish_reason']!='stop':raise RuntimeError('Recovery model/finish mismatch')
if content.get('begin')!=begin or content.get('end')!=end or content.get('stage')!='ecas_generate':raise RuntimeError('Recovery sentinel/stage mismatch')
summary=read(folder/'wrapper_summary.json')
if summary['completeness_gate']!='PASS' or summary['capture_mode']!='direct_before_parse':raise RuntimeError('Original wrapper did not pass capture/completeness')
if raw['usage']!=item['usage'] or raw['usage']['prompt_tokens']>16384 or raw['usage']['completion_tokens']>16384:raise RuntimeError('Recovery usage mismatch/out of cap')
Draft202012Validator(SCHEMA).validate(content['output'])
normalized,changes=normalize_stage('ecas_generate',content['output'])
if len(changes)!=1 or normalized['candidate']!=content['output']:raise RuntimeError('Recovery changed business IR')
validate_stage('ecas_generate',normalized,True)
output_path=folder/'locally_recovered_output_v2.json'
if output_path.exists():raise RuntimeError('Explicit recovery already generated; do not rewrite derivatives')
dump(output_path,normalized)
receipt={'classification':'DETERMINISTIC_COMPLETE_IR_OUTER_WRAPPER_RECOVERY','scope_id':item['scope_id'],'call_index':3,'new_API_calls':0,
         'original_status':item['status'],'original_error_type':item['error_type'],'original_error':item['error'],
         'as_run_ledger_snapshot_path':str(snapshot/'CALL_LEDGER.json'),'as_run_ledger_snapshot_sha256':sha(snapshot/'CALL_LEDGER.json'),
         'raw_response_path':str(raw_path),'raw_response_sha256_before':EXPECTED_RAW,'raw_response_sha256_after':sha(raw_path),
         'original_schema_sha256':sha(ROOT/'execution_inputs/ecas_output_schema.json'),'original_IR_schema_valid':True,
         'original_IR_canonical_sha256':hashlib.sha256(json.dumps(content['output'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),
         'normalized_output_path':str(output_path),'normalized_output_sha256':sha(output_path),'candidate_json_equal_to_original_IR':True,
         'business_fields_changed':False,'original_usage_preserved':raw['usage'],'returned_model':raw['model'],'finish_reason':'stop',
         'recovered_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
dump(folder/'LOCAL_WRAPPER_RECOVERY_RECEIPT_V2.json',receipt)
old_error={k:item[k] for k in ['status','error_type','error','completed_at']}
item.pop('error_type');item.pop('error')
item.update(status='COMPLETED',as_run_failure=old_error,local_recovery_status='RECOVERED_COMPLETE_IR_OUTER_WRAPPER_ONLY',
            local_recovery_new_API_calls=0,local_recovery_receipt=str(folder/'LOCAL_WRAPPER_RECOVERY_RECEIPT_V2.json'),
            output_path=str(output_path),output_sha256=sha(output_path),parse_status='PASS',completeness_gate='PASS',recovered_at=receipt['recovered_at'])
dump(ROOT/'CALL_LEDGER.json',ledger)
dump(ROOT/'WRAPPER_RECOVERY_STATE_V2.json',{'status':'COMPLETED_LOCAL_REPARSE_ONLY','scope_id':item['scope_id'],'actual_paid_attempts':3,
     'new_API_calls':0,'original_smoke_remaining_new_calls':1,'completed_cached_calls':[1,2,3],'as_run_snapshot':str(snapshot),
     'raw_sha256_unchanged':sha(raw_path)==EXPECTED_RAW,'receipt_path':str(folder/'LOCAL_WRAPPER_RECOVERY_RECEIPT_V2.json')})
print(json.dumps({'status':'COMPLETED_LOCAL_REPARSE_ONLY','actual_paid_attempts':3,'new_API_calls':0,'original_IR_unchanged':True,'raw_sha256':sha(raw_path)}))
