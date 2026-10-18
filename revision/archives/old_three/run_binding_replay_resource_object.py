"""Symmetric post-hoc interface repair using declared neutral constants only.

Never rewrite business conditions, select a better earlier candidate, send final
labels to models, or merge these observations into the original run silently.
"""
import datetime
import json
import shutil
from pathlib import Path
from pilot_lib import ROOT,LANE,CONFIG,read,dump,sha,tool,policy_checks,adapt,rego_decision,evaluate_ecas,compile_policy,verify_inputs

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def strip(value):
    if isinstance(value,dict):return {k:strip(v) for k,v in value.items() if k!='location'}
    if isinstance(value,list):return [strip(v) for v in value]
    return value

def envelope(task,original):
    value=adapt(task,original)
    constants=read(ROOT/'generation_inputs'/task/'packet.json')['common_adapter']
    # Only predeclared neutral metadata aliases; no new state, rule or policy value.
    for key in ('subject_role','resource_system','resource_version'):
        value[key]=constants[key]
    value['resource']={'id':value['resource'],'system':constants['resource_system'],'version':constants['resource_version']}
    assert value['request']==original['request']
    assert value.get('trusted',{})==original.get('trusted',{})
    return value

def main():
    verify_inputs()
    state=read(ROOT/'EXECUTION_STATE.json')
    if state['status']!='COMPLETED':raise RuntimeError('Wait for original model batch completion')
    out=ROOT/'binding_replay_resource_object';out.mkdir(exist_ok=False)
    configuration={'classification':'POST_HOC_ENGINEERING_INTERFACE_REPAIR_NOT_FRESH_MODEL_EFFECT','additional_model_calls':0,'apply_to_all_methods_and_cases':True,
        'resource_profile':'object with id/system/version from declared constants','scalar_profile_reference':'binding_replay/SUMMARY.json','metadata_aliases':['subject_role','resource_system','resource_version'],'alias_source':'original common_adapter constants',
        'business_inputs_unchanged':['request','trusted'],'business_rules_rewritten':False,'earlier_candidate_selection':False,
        'formatting':'OPA fmt; AST equality without location metadata required','original_run':'EXECUTION_STATE.json','created_at':now()}
    dump(out/'PROTOCOL.json',configuration)
    results=[]
    for source_row in state['rows']:
        task=source_row['task'];method=source_row['method']
        folder=out/task/method;folder.mkdir(parents=True)
        result={'task':task,'method':method,'initial_status':source_row['status'],'status':source_row['status'],'classification':configuration['classification'],'requests':[],'model_calls':source_row.get('calls',[])}
        if method=='ECAS_MATCHED':
            original=ROOT/'effect_runs'/task/method
            if source_row.get('admission')!='ADMITTED':
                result['reason']=source_row.get('reason');dump(folder/'RESULT.json',result);results.append(result);continue
            policy=read(original/'admitted_policy.json');contract=read(ROOT/'execution_inputs'/task/'contract.json')
            compile_policy(policy,contract)
            for channel in ('O-L','O-I'):
                for v in read(ROOT/'sealed_evaluation'/task/(channel+'.json'))['vectors']:
                    mapped=envelope(task,v['envelope']);decision=evaluate_ecas(policy,contract,mapped,admission_mode='semantic')
                    result['requests'].append({'channel':channel,'input':v['envelope'],'mapped_input':mapped,'expected':v['expected_class'],'actual':decision})
            result['status']='EVALUATED'
            result['original_policy_sha256']=sha(original/'admitted_policy.json')
        else:
            checks=source_row.get('developer_checks')
            if not checks or checks.get('compile_exit')!=0:
                result['reason']=source_row.get('reason');dump(folder/'RESULT.json',result);results.append(result);continue
            source=Path(checks['policy_path'])
            if not source.is_file():raise RuntimeError('Last candidate source missing')
            policy=folder/'external_pilot/policy.rego';policy.parent.mkdir();shutil.copyfile(source,policy)
            before=tool([LANE/'tools/opa','parse','--format=json',source],folder,'before_ast')
            fmt=tool([LANE/'tools/opa','fmt','-w',policy],folder,'opa_fmt')
            after=tool([LANE/'tools/opa','parse','--format=json',policy],folder,'after_ast')
            if before.returncode or fmt.returncode or after.returncode:raise RuntimeError('OPA format/parse failed')
            ast_equal=strip(json.loads(before.stdout))==strip(json.loads(after.stdout))
            if not ast_equal:raise RuntimeError('Formatting changed AST')
            normalized=policy_checks(policy.read_text(encoding='utf-8'),folder/'validation',method=='P2P_STYLE')
            result['checks']=normalized;result['format_receipt']={'source_policy_sha256':sha(source),'formatted_sha256':sha(policy),'ast_equal_without_locations':ast_equal,'source_path':str(source)}
            if not normalized['accepted']:
                result['status']='DEVELOPMENT_REJECTED';dump(folder/'RESULT.json',result);results.append(result);continue
            tests=read(ROOT/'effect_runs'/task/method/'generated_developer_tests.json') if method=='P2P_STYLE' else read(ROOT/'execution_inputs/operator_developer_tests.json')['tasks'][task]
            developer=[]
            for j,t in enumerate(tests):
                d=rego_decision(normalized['policy_path'],envelope(task,t['input']),folder,f'developer_{j:02d}')
                developer.append({'id':t['id'],'expected':t['expected'],'actual':d,'pass':d['status']=='EXECUTED' and d['decision']==t['expected']})
            result['developer_results']=developer;dump(folder/'DEVELOPER_RESULTS.json',developer)
            if not developer or not all(x['pass'] for x in developer):
                result['status']='DEVELOPMENT_REJECTED';dump(folder/'RESULT.json',result);results.append(result);continue
            dump(folder/'CANDIDATE_FREEZE.json',{'policy_path':normalized['policy_path'],'policy_sha256':sha(normalized['policy_path']),'frozen_at':now(),'no_new_model_call':True,'source':str(source)})
            for channel in ('O-L','O-I'):
                for j,v in enumerate(read(ROOT/'sealed_evaluation'/task/(channel+'.json'))['vectors']):
                    mapped=envelope(task,v['envelope']);d=rego_decision(normalized['policy_path'],mapped,folder,f'final_{channel}_{j}')
                    result['requests'].append({'channel':channel,'input':v['envelope'],'mapped_input':mapped,'expected':v['expected_class'],'actual':d})
            result['status']='EVALUATED'
        result['request_pair_correct']=result['status']=='EVALUATED' and len(result['requests'])==2 and all(x['actual'].get('decision')==x['expected'] and not x['actual'].get('engine_error') for x in result['requests'])
        dump(folder/'RESULT.json',result);results.append(result)
    verify_inputs();dump(out/'SUMMARY.json',{'status':'COMPLETED','protocol':configuration,'rows':results,'new_model_calls':0})
    print(json.dumps({'rows':len(results),'new_model_calls':0,'summary':[{'task':r['task'],'method':r['method'],'status':r['status'],'pair_correct':r.get('request_pair_correct')} for r in results]},ensure_ascii=False))

if __name__=='__main__':main()
