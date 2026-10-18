"""Reconcile immutable raw calls and replay first/final policies after generation ends."""
import csv
import datetime
import json
from pathlib import Path
from pilot_lib import ROOT,LANE,CONFIG,read,dump,sha,verify_inputs,adapt,rego_decision,compile_model_ir,compile_policy,evaluate_ecas,PolicyError
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def compact(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def execute(task,method,policy,values,folder):
    rows=[]
    if method=='ECAS_MATCHED':
        contract=read(ROOT/'execution_inputs'/task/'contract.json')
    for i,item in enumerate(values):
        if method=='ECAS_MATCHED':actual=evaluate_ecas(policy,contract,item['input'],admission_mode='semantic')
        else:actual=rego_decision(policy,adapt(task,item['input']),folder,f'eval_{i:02d}')
        rows.append({**item,'actual':actual,'pass':actual.get('decision')==item['expected'] and not actual.get('engine_error')})
    return rows
def main():
    verify_inputs();state=read(ROOT/'EXECUTION_STATE.json')
    if state['status']=='RUNNING':raise RuntimeError('Generation active; do not evaluate initial policies yet')
    recovery_state=read(ROOT/'FORMAT_RECOVERY_STATE.json') if (ROOT/'FORMAT_RECOVERY_STATE.json').exists() else None
    if recovery_state and recovery_state['status']=='RUNNING':raise RuntimeError('Grounding recovery generation is active')
    documented_state=read(ROOT/'DOCUMENTED_EXECUTION_STATE.json') if (ROOT/'DOCUMENTED_EXECUTION_STATE.json').exists() else None
    if documented_state and documented_state['status']=='RUNNING':raise RuntimeError('Documented ECAS generation is active')
    calls=read(ROOT/'CALL_LEDGER.json');audit=[];outputs={}
    for call in calls:
        p=Path(call['raw_response_path'])
        ok=p.exists() and sha(p)==call.get('raw_response_sha256')
        if call['status']=='COMPLETED':
            raw=read(p);wrapped=json.loads(raw['choices'][0]['message']['content'])
            ok=ok and raw['model']==CONFIG['model'] and raw['choices'][0]['finish_reason']=='stop'
            parsed=read(Path(call['output_path']))
            # Only the documented extraction status alias is eligible normalization.
            normalized=json.loads(json.dumps(wrapped['output']))
            if call.get('format_normalizations') and call['stage']=='p2p_extract' and normalized.get('status')=='EXTRACTED':normalized['status']='READY'
            ok=ok and normalized==parsed
            usage=raw.get('usage',{});ok=ok and usage.get('prompt_tokens',10**9)<=CONFIG['max_prompt_tokens'] and usage.get('completion_tokens',10**9)<=CONFIG['max_tokens']
            outputs[call['index']]=parsed
        audit.append({'check':'raw_call_'+str(call['index']),'pass':ok,'path':str(p),'status':call['status']})
    audit.append({'check':'call_limit','pass':len(calls)<=CONFIG['max_calls'] and sum(c['smoke'] for c in calls)<=CONFIG['max_smoke_calls'] and sum(c['stage']=='repair' for c in calls)<=CONFIG['max_total_external_repair_calls']})
    rows=[]
    branch_protocol=read(ROOT/'sealed_evaluation/branch_protocol.json')
    for task in CONFIG['tasks']:
        final_vectors=[]
        for channel in ('O-L','O-I'):
            for v in read(ROOT/'sealed_evaluation'/task/(channel+'.json'))['vectors']:
                final_vectors.append({'id':channel,'input':v['envelope'],'expected':v['expected_class'],'basis':'archived_original'})
        probes=[{'id':x[0],'input':x[1],'expected':x[2],'basis':x[3]} for x in branch_protocol['vectors'][task]]
        for method in ('P2P_STYLE','AUTOPAC_STYLE','ECAS_MATCHED'):
            folder=ROOT/'effect_runs'/task/method
            recovered=ROOT/'format_recovery'/task/method
            if (recovered/'RESULT.json').exists() and read(recovered/'RESULT.json')['status']!='STARTED':folder=recovered
            formatted=ROOT/'format_replay'/task/method
            if (formatted/'RESULT.json').exists():folder=formatted
            documented=ROOT/'documented_ecas'/task/method
            if (documented/'RESULT.json').exists():folder=documented
            rp=folder/'RESULT.json'
            if not rp.exists():rows.append({'task':task,'method':method,'status':'NOT_RUN','requests':[]});continue
            result=read(rp)
            if result['status']=='EVALUATED':
                freeze=read(folder/'CANDIDATE_FREEZE.json')
                audit.append({'check':task+'_'+method+'_candidate_freeze_hash','pass':sha(Path(freeze['policy_path']))==freeze['policy_sha256'] and freeze['final_evaluation_not_yet_read'] is True})
            row={'task':task,'method':method,'status':result['status'],'requests':result.get('requests',[]),'calls':result.get('calls',[]),'repaired_once':result.get('repaired_once',False),'reason':result.get('reason'),'initial_requests':[],'branch_probes':[],'source_folder':str(folder),'format_recovery':result.get('format_recovery',False),'original_interface_status':result.get('original_interface_status',result['status'])}
            row['format_only_recovery']=result.get('format_only_recovery',False)
            row['documentation_revision']=result.get('documentation_revision',False)
            base_result=read(ROOT/'effect_runs'/task/method/'RESULT.json')
            row['original_batch_status']=base_result['status'];row['original_batch_requests']=base_result.get('requests',[])
            row['original_batch_pair_correct']=base_result.get('request_pair_correct',False)
            if row['format_only_recovery']:
                receipt=read(folder/'FORMAT_ONLY_RECEIPT.json')
                before=read(folder/'formatted/before_ast.stdout.txt');after=read(folder/'formatted/after_ast.stdout.txt')
                def strip_locations(value):
                    if isinstance(value,dict):return {k:strip_locations(v) for k,v in value.items() if k!='location'}
                    if isinstance(value,list):return [strip_locations(v) for v in value]
                    return value
                audit.append({'check':task+'_'+method+'_format_ast_equal','pass':strip_locations(before)==strip_locations(after) and receipt['ast_equal_without_locations'] and sha(Path(receipt['source_policy_path']))==receipt['source_policy_sha256'] and sha(Path(receipt['formatted_policy_path']))==receipt['formatted_policy_sha256']})
            if result.get('format_recovery'):
                original=read(folder/'extraction.json');grounded=read(folder/'extraction_grounded.json');receipt=read(folder/'GROUNDING_REPRESENTATION_RECEIPT.json')
                neutral=read(ROOT/'generation_inputs'/task/'packet.json')['common_adapter']['envelope_representation']
                expected=json.loads(json.dumps(original))
                eligible=True
                for change in receipt['changes']:
                    field=change['field'];index=change['component'];before=expected['components'][index][field]
                    eligible=eligible and before==neutral[field] and before['id']==change['to'] and change['from']==before
                    expected['components'][index][field]=before['id']
                audit.append({'check':task+'_format_only_grounding_recovery','pass':eligible and expected==grounded and sha(Path(receipt['original_source'])/'extraction.json')==receipt['source_extraction_sha256'] and sha(folder/'extraction_grounded.json')==receipt['derived_extraction_sha256']})
            policies={}
            if method=='ECAS_MATCHED':
                cp=folder/'candidate.json'
                if cp.exists():
                    candidate=read(cp)
                    matches=any(outputs.get(i,{}).get('candidate')==candidate for i in row['calls'])
                    audit.append({'check':task+'_'+method+'_candidate_matches_raw','pass':matches})
                if result.get('admission')=='ADMITTED':
                    proposal=compile_model_ir(read(cp));admitted=compile_policy(proposal['policy'],read(ROOT/'execution_inputs'/task/'contract.json'))
                    audit.append({'check':task+'_'+method+'_policy_matches_compile','pass':admitted==read(folder/'admitted_policy.json')})
                    policies={'initial':admitted,'final':admitted}
                row['common_developer_results']=result.get('common_developer_results')
            else:
                gp=folder/'generation.json'
                if gp.exists():audit.append({'check':task+'_'+method+'_generation_matches_raw','pass':any(outputs.get(i)==read(gp) for i in row['calls'])})
                initial=folder/'INITIAL_DEVELOPMENT.json'
                if initial.exists():
                    dev=read(initial);row['initial_developer_checks']=dev['checks'];row['initial_developer_results']=dev['developer_results'];row['judge']=dev.get('judge')
                    if dev['checks']['compile_exit']==0:policies['initial']=dev['checks']['policy_path']
                check=result.get('developer_checks',{})
                if check.get('compile_exit')==0 and check.get('policy_path'):policies['final']=check['policy_path']
                row['final_developer_results']=result.get('developer_results')
                for label,pp in policies.items():
                    genpath=folder/('repair.json' if label=='final' and row['repaired_once'] else 'generation.json')
                    if label=='final' and row['format_only_recovery']:
                        receipt=read(folder/'FORMAT_ONLY_RECEIPT.json')
                        exact=Path(receipt['source_policy_path']).read_text(encoding='utf-8')==read(genpath)['rego'] and Path(pp).read_text(encoding='utf-8')==Path(receipt['formatted_policy_path']).read_text(encoding='utf-8')
                    else:exact=Path(pp).read_text(encoding='utf-8')==read(genpath)['rego']
                    audit.append({'check':task+'_'+method+'_'+label+'_rego_exact_or_verified_format','pass':exact})
            for label,policy in policies.items():
                observed=execute(task,method,policy,final_vectors,ROOT/'audit_replay'/task/method/label)
                if label=='initial':row['initial_requests']=observed
                elif result['status']=='EVALUATED':
                    matches=len(observed)==len(result.get('requests',[])) and all(x['actual'].get('decision')==y['actual'].get('decision') and x['input']==y['input'] and x['expected']==y['expected'] for x,y in zip(observed,result['requests']))
                    audit.append({'check':task+'_'+method+'_requests_replay','pass':matches})
                branch=execute(task,method,policy,probes,ROOT/'audit_branches'/task/method/label)
                if label=='initial':row['initial_branch_probes']=branch
                else:row['branch_probes']=branch
            row['initial_pair_correct']=all(x['pass'] for x in row['initial_requests']) if len(row['initial_requests'])==2 else None
            row['pair_correct']=(len(row['requests'])==2 and all(x['actual'].get('decision')==x['expected'] and not x['actual'].get('engine_error') for x in row['requests'])) if result['status']=='EVALUATED' else None
            row['branch_count']=len(row['branch_probes']);row['branch_passed']=sum(x['pass'] for x in row['branch_probes'])
            dump(ROOT/'audit_rows'/f'{task}__{method}.json',row);rows.append(row)
    # Verify original source snapshots and unchanged complete business articles.
    for derivative in read(ROOT/'INPUT_DERIVATIONS.json'):
        audit.append({'check':'original_source_'+Path(derivative['path']).parent.name+'_'+Path(derivative['path']).name,'pass':sha(Path(derivative['source_path']))==derivative['source_sha256']})
    for task in CONFIG['tasks']:
        original=read(ROOT/'source_snapshots'/task/'visible_input.json');packet=read(ROOT/'generation_inputs'/task/'packet.json')
        for s in original['visible_sources']:
            if isinstance(s['content'],str) and s['source_id']!='frappe-rest-api.html':
                other=next(x for x in packet['visible_sources'] if x['evidence_id']==s['evidence_id'])
                audit.append({'check':task+'_'+s['evidence_id']+'_complete_business_article','pass':s['content']==other['content']})
    verify_inputs()
    reconciliation={'status':'PASS' if all(x['pass'] for x in audit) else 'FAIL','checked_at':now(),'checks':audit,'scientific_clearance':False,'scope_id':CONFIG['scope_id']}
    dump(ROOT/'FINAL_RECONCILIATION.json',reconciliation)
    overall=state['status'] if not recovery_state or recovery_state['status']=='COMPLETED' else 'RECOVERY_INCOMPLETE'
    if documented_state and documented_state['status']!='COMPLETED':overall='DOCUMENTED_CONFIGURATION_INCOMPLETE'
    summary={'status':overall,'base_batch_status':state['status'],'grounding_recovery_status':recovery_state['status'] if recovery_state else 'NOT_NEEDED_OR_NOT_STARTED','documented_ecas_status':documented_state['status'] if documented_state else 'NOT_RUN','scope_id':CONFIG['scope_id'],'classification':CONFIG['classification'],'rows':rows,'calls':len(calls),'smoke_calls':sum(c['smoke'] for c in calls),'repair_calls':sum(c['stage']=='repair' for c in calls),'prompt_tokens':sum((c.get('usage') or {}).get('prompt_tokens',0) for c in calls),'completion_tokens':sum((c.get('usage') or {}).get('completion_tokens',0) for c in calls),'reconciliation':reconciliation['status'],'cost':'UNKNOWN','native_baselines':'NOT_RUN'}
    dump(ROOT/'COMPARISON_SUMMARY.json',summary)
    fields=['task','method','status','initial_pair_correct','pair_correct','branch_passed','branch_count','repaired_once','reason']
    with (ROOT/'COMPARISON.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    headers=next(csv.reader((ROOT/'RESULT_TRACEABILITY.csv').open(encoding='utf-8-sig')))
    with (ROOT/'RESULT_TRACEABILITY.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=headers);writer.writeheader()
        for i,row in enumerate(rows):
            source=ROOT/'audit_rows'/f'{row["task"]}__{row["method"]}.json'
            writer.writerow({'result_id':f'FOUR-PEER-20261014-{i+1:02d}','experiment_id':CONFIG['scope_id'],'metric_name':'archived_request_pair_correct','dataset_name':row['task'],'dataset_version':'FSV_visible_v4_oracle_v1_derived_source_v1','data_split':'retrospective_already_exposed','sample_count':2 if row['status']=='EVALUATED' else 0,'raw_value':int(row.get('pair_correct',False)) if row['status']=='EVALUATED' else '', 'reported_value':int(row.get('pair_correct',False)) if row['status']=='EVALUATED' else '', 'unit':'boolean','aggregation':'per_case_per_adapted_method','source_output_path':str(source.relative_to(ROOT.parents[2])),'source_locator':'requests;status;initial_requests;branch_probes','script_path':str((ROOT/'run_pilot.py').relative_to(ROOT.parents[2])),'command_or_config':'EXECUTION_CONFIG.json;FROZEN_PROTOCOL_CN.md','seed':'NOT_SET','environment':'WSL Python/OPA/Regal;approved Windows GLM5.2 high wrapper','git_commit':'NOT_AVAILABLE_HASH_FROZEN','checksum':sha(source),'rounding_rule':'none','status':'PASS' if row['status']=='EVALUATED' and reconciliation['status']=='PASS' else 'NOT_APPLICABLE','verified_by':'deterministic_raw_source_and_policy_replay','verified_at':now(),'notes':'Adapted retrospective pilot; tool failures and scope exits excluded from accuracy denominator; no global superiority claim.'})
    print(json.dumps({'status':state['status'],'reconciliation':reconciliation['status'],'calls':len(calls),'rows':[{k:r.get(k) for k in fields} for r in rows]},ensure_ascii=False))
    if reconciliation['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
