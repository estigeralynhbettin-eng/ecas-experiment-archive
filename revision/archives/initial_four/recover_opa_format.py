"""Deterministic AST-preserving OPA formatting in separate replay folders, no model calls."""
import json
import shutil
from pathlib import Path
from pilot_lib import ROOT,LANE,CONFIG,read,dump,sha,tool,policy_checks,run_tests,verify_inputs
from run_pilot import final_rego,now
def strip(value):
    if isinstance(value,dict):return {k:strip(v) for k,v in value.items() if k!='location'}
    if isinstance(value,list):return [strip(v) for v in value]
    return value
def main():
    if read(ROOT/'EXECUTION_STATE.json')['status']!='COMPLETED':raise RuntimeError('Original model batch active')
    if (ROOT/'FORMAT_RECOVERY_STATE.json').exists() and read(ROOT/'FORMAT_RECOVERY_STATE.json')['status']=='RUNNING':raise RuntimeError('Grounding generation active')
    verify_inputs();rows=[]
    for task in CONFIG['tasks']:
        for method in ('P2P_STYLE','AUTOPAC_STYLE'):
            source=ROOT/'format_recovery'/task/method
            if not (source/'RESULT.json').exists():source=ROOT/'effect_runs'/task/method
            result=read(source/'RESULT.json');checks=result.get('developer_checks',{})
            violations=(checks.get('lint_report') or {}).get('violations',[])
            if result['status']!='DEVELOPMENT_REJECTED' or checks.get('compile_exit')!=0 or not violations or any(v['title']!='opa-fmt' for v in violations):continue
            dest=ROOT/'format_replay'/task/method
            if (dest/'RESULT.json').exists():rows.append({'task':task,'method':method,'status':'EXISTING_REPLAY_NOT_REPEATED'});continue
            dest.mkdir(parents=True,exist_ok=False)
            for filename in ('generation.json','repair.json','detection.json','extraction.json','extraction_grounded.json','GROUNDING_REPRESENTATION_RECEIPT.json','INITIAL_DEVELOPMENT.json','generated_developer_tests.json'):
                if (source/filename).exists():shutil.copyfile(source/filename,dest/filename)
            dump(dest/'ORIGINAL_RESULT.json',result)
            policy=Path(checks['policy_path']);formatted=dest/'formatted/external_pilot/policy.rego';formatted.parent.mkdir(parents=True);shutil.copyfile(policy,formatted)
            before=tool([LANE/'tools/opa','parse','--format=json',policy],dest/'formatted','before_ast')
            fmt=tool([LANE/'tools/opa','fmt','-w',formatted],dest/'formatted','opa_fmt')
            after=tool([LANE/'tools/opa','parse','--format=json',formatted],dest/'formatted','after_ast')
            equal=not before.returncode and not after.returncode and strip(json.loads(before.stdout))==strip(json.loads(after.stdout))
            if fmt.returncode or not equal:raise RuntimeError('Formatting changed AST or failed')
            tests=read(source/'generated_developer_tests.json')
            normalized=policy_checks(formatted.read_text(encoding='utf-8'),dest/'validated',method=='P2P_STYLE')
            dev=run_tests(task,normalized['policy_path'],tests,dest/'validated') if normalized['accepted'] else {'passed':False,'rows':[]}
            receipt={'source_policy_path':str(policy),'source_policy_sha256':sha(policy),'formatted_policy_path':str(formatted),'formatted_policy_sha256':sha(formatted),'ast_equal_without_locations':bool(equal),'new_model_calls':0,'original_status':result['status'],'no_final_oracle_feedback':True}
            dump(dest/'FORMAT_ONLY_RECEIPT.json',receipt)
            output=json.loads(json.dumps(result));output.update({'format_only_recovery':True,'original_format_status':result['status'],'source_folder_before_format':str(source),'developer_checks':normalized,'developer_results':dev})
            if normalized['accepted'] and dev['passed']:
                dump(dest/'CANDIDATE_FREEZE.json',{'policy_path':normalized['policy_path'],'policy_sha256':sha(normalized['policy_path']),'frozen_at':now(),'final_evaluation_not_yet_read':True})
                output['requests']=final_rego(task,method,normalized['policy_path'],dest);output['status']='EVALUATED'
                output['request_pair_correct']=len(output['requests'])==2 and all(x['actual'].get('decision')==x['expected'] for x in output['requests'])
            dump(dest/'RESULT.json',output);rows.append({'task':task,'method':method,'status':output['status'],'pair_correct':output.get('request_pair_correct')})
    verify_inputs();dump(ROOT/'FORMAT_ONLY_CLOSEOUT.json',{'status':'COMPLETED','rows':rows,'new_model_calls':0})
    print(json.dumps({'format_replays':rows,'new_model_calls':0},ensure_ascii=False))
if __name__=='__main__':main()
