"""Finish pending lint-only paths with deterministic OPA formatting, no LLM calls."""
import json
import shutil
from pathlib import Path
from pilot_lib import ROOT,read,dump,sha,LANE,tool,policy_checks,run_tests
from run_pilot import final_rego,now

def strip_locations(value):
    if isinstance(value,dict):return {k:strip_locations(v) for k,v in value.items() if k!='location'}
    if isinstance(value,list):return [strip_locations(v) for v in value]
    return value

def main():
    state=read(ROOT/'EXECUTION_STATE.json')
    if state['status']!='COMPLETED':raise RuntimeError('Original model batch not complete; do not mutate inputs or outcome')
    history=ROOT/'PRE_FORMAT_EXECUTION_STATE.json';shutil.copyfile(ROOT/'EXECUTION_STATE.json',history)
    repairs=[]
    for i,row in enumerate(state['rows']):
        if row['method']!='P2P_STYLE' or row['status']!='DEVELOPMENT_REJECTED':continue
        checks=row['developer_checks'];violations=(checks.get('lint_report') or {}).get('violations',[])
        if checks.get('compile_exit')!=0 or not violations or any(x['title']!='opa-fmt' for x in violations):continue
        base=ROOT/'effect_runs'/row['task']/row['method']
        original=read(base/'RESULT.json');dump(base/'PRE_FORMAT_RESULT.json',original)
        tests=read(base/'generated_developer_tests.json')
        source=Path(checks['policy_path']);out=base/'formatted';out.mkdir(exist_ok=False)
        formatted=out/'external_pilot/policy.rego';formatted.parent.mkdir();shutil.copyfile(source,formatted)
        before=tool([LANE/'tools/opa','parse','--format=json',source],out,'before_ast')
        fmt=tool([LANE/'tools/opa','fmt','-w',formatted],out,'opa_fmt')
        after=tool([LANE/'tools/opa','parse','--format=json',formatted],out,'after_ast')
        if before.returncode or fmt.returncode or after.returncode:raise RuntimeError('OPA formatting/AST parse failed')
        semantic_equal=strip_locations(json.loads(before.stdout))==strip_locations(json.loads(after.stdout))
        if not semantic_equal:raise RuntimeError('Formatting unexpectedly changed AST')
        normalized=policy_checks(formatted.read_text(encoding='utf-8'),out/'validated',True)
        developer=run_tests(row['task'],normalized['policy_path'],tests,out/'validated') if normalized['accepted'] else {'passed':False,'rows':[]}
        receipt={'source_sha256':sha(source),'formatted_sha256':sha(formatted),'ast_equal_without_locations':semantic_equal,'opa_fmt_exit':fmt.returncode,'new_model_calls':0,'no_oracle_feedback_used':True,'checked_at':now()}
        dump(out/'FORMAT_ONLY_RECEIPT.json',receipt)
        if not normalized['accepted'] or not developer['passed']:continue
        dump(base/'CANDIDATE_FREEZE.json',{'policy_path':normalized['policy_path'],'policy_sha256':sha(normalized['policy_path']),'frozen_at':now(),'final_evaluation_not_yet_read':True,'format_only_receipt':'formatted/FORMAT_ONLY_RECEIPT.json'})
        row.update({'status':'EVALUATED','initial_status':'DEVELOPMENT_REJECTED','format_only_recovery':receipt,'developer_checks':normalized,'developer_results':developer,'requests':final_rego(row['task'],row['method'],normalized['policy_path'],base),'completed_at':now()})
        row['request_pair_correct']=len(row['requests'])==2 and all(x['actual']['decision']==x['expected'] for x in row['requests'])
        dump(base/'RESULT.json',row);repairs.append({'task':row['task'],'method':row['method'],'pair_correct':row['request_pair_correct']})
    state['format_only_rechecks']=repairs;state['completed_at']=now();dump(ROOT/'EXECUTION_STATE.json',state)
    dump(ROOT/'FORMAT_ONLY_CLOSEOUT.json',{'status':'COMPLETED','repairs':repairs,'new_model_calls':0,'original_state_path':str(history),'separate_original_rejections_retained':True})
    print(json.dumps({'format_only_recovered':len(repairs),'new_model_calls':0,'rows':repairs}))

if __name__=='__main__':main()
