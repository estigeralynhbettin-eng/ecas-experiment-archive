"""Read-only original-evidence reconciliation across the pilot and local replay."""
import json
from pathlib import Path
from pilot_lib import ROOT,CONFIG,read,dump,sha,verify_inputs

def main():
    verify_inputs();calls=read(ROOT/'CALL_LEDGER.json');rows=read(ROOT/'binding_replay/SUMMARY.json')['rows'];checks=[];ids=[]
    for item in calls:
        rawpath=Path(item['raw_response_path']);raw=read(rawpath)
        ids.append(raw.get('id',raw.get('request_id')))
        content=json.loads(raw['choices'][0]['message']['content'])
        usage=raw['usage']
        checks.append({'object':f'call-{item["index"]}','check':'immutable_raw_model_finish_usage','pass':sha(rawpath)==item['raw_response_sha256'] and raw['model']=='glm-5.2' and raw['choices'][0]['finish_reason']=='stop' and bool(content['output']) and usage['prompt_tokens']<=16384 and usage['completion_tokens']<=16384})
        checks.append({'object':f'call-{item["index"]}','check':'final_fixture_labels_absent_from_prompt','pass':'expected_class' not in Path(item['prompt_path']).read_text(encoding='utf-8') and 'sealed_evaluation' not in Path(item['prompt_path']).read_text(encoding='utf-8')})
    checks.append({'object':'budget','check':'calls_smoke_repairs_and_distinct_ids','pass':len(calls)<=30 and sum(x['smoke'] for x in calls)<=4 and sum(x['stage']=='repair' for x in calls)<=5 and len(ids)==len(set(ids))})
    profiled_rows=[('binding_replay',r) for r in rows]+[('binding_replay_resource_object',r) for r in read(ROOT/'binding_replay_resource_object/SUMMARY.json')['rows']]
    for profile,row in profiled_rows:
        folder=ROOT/profile/row['task']/row['method']
        if 'format_receipt' in row:
            receipt=row['format_receipt']
            checks.append({'object':row['task']+'/'+row['method'],'check':'policy_source_hash_ast_equal','pass':sha(receipt['source_path'])==receipt['source_policy_sha256'] and receipt['ast_equal_without_locations']})
        for req in row['requests']:
            original=read(ROOT/'sealed_evaluation'/row['task']/(req['channel']+'.json'))['vectors']
            original_equal=any(v['envelope']==req['input'] and v['expected_class']==req['expected'] for v in original)
            mapping_equal=req['mapped_input']['request']==req['input']['request'] and req['mapped_input'].get('trusted',{})==req['input'].get('trusted',{})
            checks.append({'object':row['task']+'/'+row['method']+'/'+req['channel'],'check':'archived_fixture_and_payload_trusted_equal','pass':original_equal and mapping_equal})
            if row['method']!='ECAS_MATCHED':
                raw_eval=read(folder/(f"final_{req['channel']}_0.stdout.txt"))
                value=raw_eval['result'][0]['expressions'][0]['value']
                checks.append({'object':row['task']+'/'+row['method']+'/'+req['channel'],'check':'raw_opa_boolean_decision','pass':type(value) is bool and ('allow' if value else 'deny')==req['actual']['decision']})
    checks.append({'object':'native_methods','check':'not_claimed_executed','pass':all(r['execution_status']=='NOT_RUN' for r in read(ROOT/'RUN_STATUS.json')['rows'] if r['method'] in ('P2P_NATIVE','AUTOPAC_NATIVE'))})
    diag=read(ROOT/'targeted_diagnostics/regex_literal/RESULT.json')
    checks.append({'object':'regex_diagnostic','check':'literal_match_observed_without_policy_rewrite','pass':diag['observed_match'] is True and diag['original_policy_changed'] is False})
    result={'status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','checks':checks,'count':len(checks),'scope':CONFIG['scope_id'],'model_calls':len(calls),'original_generation_rows':len(read(ROOT/'EXECUTION_STATE.json')['rows']),'posthoc_binding_rows':len(profiled_rows),'independent_samples_added':0,'scientific_whole_paper_pass':False}
    dump(ROOT/'FINAL_OUTPUT_AUDIT.json',result)
    print(json.dumps({'status':result['status'],'checks':len(checks),'calls':len(calls),'failures':[x for x in checks if not x['pass']]}))

if __name__=='__main__':main()
